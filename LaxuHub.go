// go build -ldflags="-s -w" -o LaxuHub.exe LaxuHub.go
package main

import (
	"bufio"
	"net/url" 
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	
	"github.com/pelletier/go-toml/v2" // 新增 TOML 库
)

const (
	ConfigFileName     = "laxuhub_config.ini"
	GreenDirConfigFile = "laxuhub.toml" // 修改为 TOML 文件
	ConfigVersion      = "1.1"
)

type GreenDirConfig struct {
	Version      string                    `toml:"version"` // 修改标签
	Environments map[string]LanguageConfig `toml:"environments"`
}

type LanguageConfig struct {
    DisplayName       string            `toml:"display_name"`
    BaseDir           string            `toml:"base_dir"`
    PathDirs          []string          `toml:"path_dirs"`
    EnvVars           map[string]string `toml:"env_vars"`
    SearchPrefixString []string         `toml:"searchprefix_string"`
}

var (
	basePath               string
	configLastEnvironments []string
	availableEnvironments  map[string][]string
	selectedEnvironments   []string
	myBinPath              string
	myBinSubPaths          []string
	greenDirConfig         GreenDirConfig
)

func main() {
	// 获取基础路径
	basePath = getBasePath()
	myBinPath = filepath.Join(basePath, "mybin")

	// 解析命令行参数
	quietMode := false
	targetPath := ""

	for _, arg := range os.Args[1:] {
		if arg == "-q" || arg == "--quiet" {
			quietMode = true
		} else if targetPath == "" && !strings.HasPrefix(arg, "-") {
			// 第一个非标志参数作为目标路径
			targetPath = arg
		}
	}

	// 设置工作目录
	if targetPath != "" {
		if _, err := os.Stat(targetPath); err == nil {
			os.Chdir(targetPath)
			//fmt.Printf("工作目录设置为: %s\n", targetPath)
		} else {
			fmt.Printf("警告: 路径 '%s' 不存在，使用当前目录\n", targetPath)
			targetPath = ""
		}
	}

	// 加载绿色目录配置
	loadGreenDirConfig()

	// 发现可用环境
	discoverEnvironments()

	// 加载用户配置
	loadConfig()

	// 统一处理静默模式和交互模式
	if quietMode {
		// 静默模式：使用上次配置
		if len(configLastEnvironments) == 0 {
			fmt.Println("提示: 无上次配置记录，进入交互模式...")
			showEnvironmentSelection()

			// 检查用户是否在交互模式中选择了环境
			if len(selectedEnvironments) == 0 {
				fmt.Println("未选择任何环境，程序退出")
				return
			}
		} else {
			selectedEnvironments = configLastEnvironments
			fmt.Println("静默模式启动，使用上次配置...")
		}
	} else {
		// 交互模式：让用户选择
		if len(configLastEnvironments) > 0 {
			showQuickStartMenu()
		} else {
			showEnvironmentSelection()
		}

		// 检查用户是否选择了环境
		if len(selectedEnvironments) == 0 {
			fmt.Println("未选择任何环境，程序退出")
			return
		}
	}

	// 统一的后续流程
	setupSelectedEnvironments(selectedEnvironments)
	showEnvironmentInfo()
	startEnvironment(targetPath)
}

func getBasePath() string {
	if basePath != "" {
		return basePath
	}

	exePath, err := os.Executable()
	if err != nil {
		fmt.Printf("获取可执行文件路径失败: %v\n", err)
		os.Exit(1)
	}
	return filepath.Dir(exePath)
}

func loadGreenDirConfig() {
	configPath := filepath.Join(basePath, GreenDirConfigFile)

	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		fmt.Printf("配置文件 %s 不存在\n", GreenDirConfigFile)
		os.Exit(1)
	}

	// 读取 TOML 文件内容
	fileContent, err := os.ReadFile(configPath)
	if err != nil {
		fmt.Printf("读取 %s 失败: %v\n", GreenDirConfigFile, err)
		os.Exit(1)
	}

	// 解析 TOML
	if err := toml.Unmarshal(fileContent, &greenDirConfig); err != nil {
		fmt.Printf("解析 %s 失败: %v\n", GreenDirConfigFile, err)
		os.Exit(1)
	}
}

func discoverEnvironments() {
	availableEnvironments = make(map[string][]string)

	for langKey, langConfig := range greenDirConfig.Environments {
		langDir := filepath.Join(basePath, langConfig.BaseDir)

		if _, err := os.Stat(langDir); os.IsNotExist(err) {
			continue
		}

		files, err := os.ReadDir(langDir)
		if err != nil {
			continue
		}

		var versions []string

		for _, file := range files {
			if file.IsDir() {
				dirName := file.Name()
				lowerDirName := strings.ToLower(dirName)

				// 获取配置的前缀数组
				prefixesToUse := langConfig.SearchPrefixString
				// 如果配置为空数组，使用语言键作为默认前缀
				if len(prefixesToUse) == 0 {
					prefixesToUse = []string{strings.ToLower(langKey)}
				}

				// 遍历所有配置的前缀进行匹配
				for _, prefix := range prefixesToUse {
					lowerPrefix := strings.ToLower(prefix)
					if strings.HasPrefix(lowerDirName, lowerPrefix) {
						versions = append(versions, dirName)
						break // 匹配到一个前缀就退出内层循环
					}
				}
			}
		}

		if len(versions) > 0 {
			sort.Strings(versions)
			availableEnvironments[langKey] = versions
		}
	}

	// 发现 mybin 子目录
	subPattern := filepath.Join(myBinPath, "sub_*")
	subMatches, err := filepath.Glob(subPattern)
	if err == nil {
		for _, match := range subMatches {
			if info, err := os.Stat(match); err == nil && info.IsDir() {
				myBinSubPaths = append(myBinSubPaths, match)
			}
		}
	}
}

func loadConfig() {
	configPath := filepath.Join(basePath, ConfigFileName)
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		return
	}

	file, err := os.Open(configPath)
	if err != nil {
		fmt.Printf("读取配置文件失败: %v\n", err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if strings.HasPrefix(line, "LastEnvironments=") {
			envs := strings.TrimPrefix(line, "LastEnvironments=")
			encodedEnvs := strings.Fields(envs)
			
			// 解码URL编码的字符串
			for _, encodedEnv := range encodedEnvs {
				if decoded, err := url.QueryUnescape(encodedEnv); err == nil {
					configLastEnvironments = append(configLastEnvironments, decoded)
				} else {
					fmt.Printf("解码配置项失败: %v\n", err)
				}
			}
			break
		}
	}
}

func saveConfig() {
	configPath := filepath.Join(basePath, ConfigFileName)
	file, err := os.Create(configPath)
	if err != nil {
		fmt.Printf("保存配置失败: %v\n", err)
		return
	}
	defer file.Close()

	// 对目录名进行URL编码，处理空格和特殊字符
	var encodedEnvs []string
	for _, env := range selectedEnvironments {
		encoded := url.QueryEscape(env) // 使用URL编码
		encodedEnvs = append(encodedEnvs, encoded)
	}

	content := fmt.Sprintf("[Settings]\nLastEnvironments=%s\nConfigVersion=%s\n",
		strings.Join(encodedEnvs, " "), ConfigVersion)
	file.WriteString(content)
}

func showQuickStartMenu() {
	fmt.Println()
	fmt.Println("   ================================")
	fmt.Println("       Laxuhub 开发环境引导器")
	fmt.Println("   ================================")
	fmt.Println()
	fmt.Println("   检测到上次配置: ")
	for _, env := range configLastEnvironments {
		fmt.Printf("       %s\n", env)
	}
	fmt.Println()

	fmt.Print("是否加载上次配置？(回车确认/Y=确认/N=重新配置): ")
	reader := bufio.NewReader(os.Stdin)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(strings.ToLower(input))

	if input == "" || input == "y" {
		selectedEnvironments = configLastEnvironments
		return
	}

	showEnvironmentSelection()
}

func showEnvironmentSelection() {
	maxRetries := 5

	for retry := 0; retry < maxRetries; retry++ {
		// 清空本轮选择
		selectedEnvironments = nil

		fmt.Println()
		fmt.Println("   ================================")
		fmt.Println("       环境配置 - 多语言选择")
		fmt.Println("   ================================")
		fmt.Println()
		fmt.Println("   请选择要使用的环境（可多选，输入多个编号用空格分隔）")
		fmt.Println()

		index := 1
		optionMap := make(map[int]string)
		var languages []string
		for lang := range availableEnvironments {
			languages = append(languages, lang)
		}
		sort.Strings(languages)

		for _, lang := range languages {
			versions := availableEnvironments[lang]
			langConfig := greenDirConfig.Environments[lang]
			for _, version := range versions {
				fmt.Printf(" [%d] %s : %s\n", index, langConfig.DisplayName, version)
				optionMap[index] = fmt.Sprintf("%s_%s", lang, version)
				index++
			}
		}

		fmt.Println()
		fmt.Println(" [0] 完成选择")
		fmt.Println(" [q] 退出选择")
		fmt.Println()
		fmt.Printf("   示例: 1 3 5  (选择多个环境, 剩余尝试次数: %d/%d)\n", maxRetries-retry, maxRetries)
		fmt.Println()

		fmt.Print("请输入要选择的环境编号: ")
		reader := bufio.NewReader(os.Stdin)
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		// 退出选项
		if input == "0" {
			return
		}
		if strings.ToLower(input) == "q" {
			selectedEnvironments = nil
			return
		}

		// 处理选择
		selections := strings.Fields(input)
		selectedLanguages := make(map[string]bool)

		for _, selStr := range selections {
			sel, err := strconv.Atoi(selStr)
			if err != nil || sel < 1 || sel >= index {
				fmt.Printf("无效的选择: %s\n", selStr)
				continue
			}

			envKey := optionMap[sel]
			lang := strings.Split(envKey, "_")[0]

			if selectedLanguages[lang] {
				fmt.Printf("语言 %s 已选择，跳过重复选择\n", lang)
				continue
			}

			selectedLanguages[lang] = true
			selectedEnvironments = append(selectedEnvironments, envKey)
		}

		if len(selectedEnvironments) > 0 {
			saveConfig()
			return // 选择成功，退出循环
		}

		// 选择失败处理
		if retry < maxRetries-1 {
			fmt.Printf("错误：未选择任何环境，还有 %d 次尝试机会\n", maxRetries-retry-1)
		} else {
			fmt.Println("错误次数过多，退出环境选择")
			selectedEnvironments = nil
		}
	}
}

func setupSelectedEnvironments(envs []string) {
	fmt.Println()
	fmt.Println("   ================================")
	fmt.Println("       快速启动环境")
	fmt.Println("   ================================")
	fmt.Println()
	fmt.Printf("   正在启动: %s\n", strings.Join(envs, " "))
	fmt.Println()
	fmt.Println("   ================================")

	currentPath := os.Getenv("PATH")
	newPath := currentPath

	newPath = myBinPath + string(os.PathListSeparator) + newPath

	for _, subPath := range myBinSubPaths {
		newPath = subPath + string(os.PathListSeparator) + newPath
	}

	for _, env := range envs {
		parts := strings.Split(env, "_")
		if len(parts) < 2 {
			continue
		}

		lang := parts[0]
		version := strings.Join(parts[1:], "_")

		fmt.Printf("[设置 %s 环境: %s]...\n", lang, version)

		langConfig, exists := greenDirConfig.Environments[lang]
		if !exists {
			continue
		}

		fullPath := filepath.Join(basePath, langConfig.BaseDir, version)

		for envVar, valueTemplate := range langConfig.EnvVars {
			value := strings.Replace(valueTemplate, "{full_path}", fullPath, -1)
			os.Setenv(envVar, value)
		}

		for _, pathDir := range langConfig.PathDirs {
			pathToAdd := fullPath
			if pathDir != "" {
				pathToAdd = filepath.Join(fullPath, pathDir)
			}
			newPath = pathToAdd + string(os.PathListSeparator) + newPath
		}
	}

	os.Setenv("PATH", newPath)
}

func showEnvironmentInfo() {
	fmt.Println()
	fmt.Println("================================")
	fmt.Println("   环境变量设置完成：")
	fmt.Println("================================")

	fmt.Println()
	fmt.Println("PATH:", os.Getenv("PATH"))
	fmt.Println()

	// cn_mirror.bat 在 mybin 目录下
	mirrorBat := filepath.Join(myBinPath, "cn_mirror.bat")
	if _, err := os.Stat(mirrorBat); err == nil {
		fmt.Println("设置镜像源...")

		// 使用特殊方法执行bat并获取环境变量
		err := applyBatchFileEnvVars(mirrorBat)
		if err != nil {
			fmt.Printf("镜像源设置执行失败: %v\n", err)
		} else {
			fmt.Println("镜像源设置完成")
		}
	} else {
		fmt.Println("cn_mirror.bat 文件不存在，使用默认源")
	}

	fmt.Println("================================")
}

func applyBatchFileEnvVars(batchFile string) error {
	originalEnv := getCurrentEnvMap()

	cmd := exec.Command("cmd", "/C", batchFile, "&&", "set")
	output, err := cmd.Output()
	if err != nil {
		return err
	}

	newEnv := parseEnvOutput(string(output))

	// 新增：按字母顺序排序
	var keys []string
	for key := range newEnv {
		keys = append(keys, key)
	}
	sort.Strings(keys) // 按字母排序

	// 按排序后的顺序遍历
	for _, key := range keys {
		newValue := newEnv[key]
		if oldValue, exists := originalEnv[key]; !exists || oldValue != newValue {
			os.Setenv(key, newValue)
			fmt.Printf("   设置: %s=%s\n", key, newValue)
		}
	}

	return nil
}

// 辅助函数：获取当前环境变量的map
func getCurrentEnvMap() map[string]string {
	envMap := make(map[string]string)
	for _, env := range os.Environ() {
		if parts := strings.SplitN(env, "=", 2); len(parts) == 2 {
			envMap[parts[0]] = parts[1]
		}
	}
	return envMap
}

// 辅助函数：解析 set 命令的输出
func parseEnvOutput(output string) map[string]string {
	envMap := make(map[string]string)
	lines := strings.Split(output, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		if strings.Contains(line, "=") && !strings.HasPrefix(line, "=") {
			parts := strings.SplitN(line, "=", 2)
			if len(parts) == 2 {
				envMap[parts[0]] = parts[1]
			}
		}
	}
	return envMap
}

func startEnvironment(targetPath string) {
	fmt.Println()

	if targetPath != "" {
		fmt.Printf("工作目录: %s\n", targetPath)
	} else {
		currentDir, _ := os.Getwd()
		fmt.Printf("工作目录: %s\n", currentDir)
	}
	fmt.Println()

	tempDir := filepath.Join(basePath, "data", "temp")
	os.Setenv("CLINK_PROFILE", tempDir)

	cleanupClinkTempFiles(tempDir)

	clinkPath := filepath.Join(myBinPath, "sub_clink", "clink.bat")
	if _, err := os.Stat(clinkPath); err == nil {
		fmt.Println("正在启动 Clink 增强命令行...")
		fmt.Println()

		cmd := exec.Command("cmd.exe", "/k", clinkPath, "inject", "--quiet")
		cmd.Env = os.Environ()
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.Stdin = os.Stdin

		err := cmd.Run()
		if err != nil {
			fmt.Printf("启动 Clink 环境失败: %v\n", err)
			fmt.Println("按回车键退出...")
			bufio.NewReader(os.Stdin).ReadBytes('\n')
		}
	} else {
		fmt.Println("警告: 未找到 Clink，启动普通命令行")
		fmt.Println()

		cmd := exec.Command("cmd.exe", "/k")
		cmd.Env = os.Environ()
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.Stdin = os.Stdin

		err := cmd.Run()
		if err != nil {
			fmt.Printf("启动命令行失败: %v\n", err)
			fmt.Println("按回车键退出...")
			bufio.NewReader(os.Stdin).ReadBytes('\n')
		}
	}
}

func cleanupClinkTempFiles(tempDir string) {
	pattern := filepath.Join(tempDir, "clink_errorlevel_*.txt")
	files, err := filepath.Glob(pattern)
	if err != nil {
		return
	}

	for _, file := range files {
		os.Remove(file)
	}
}
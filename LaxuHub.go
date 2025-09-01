//go build -ldflags="-s -w" -o LaxuHub.exe LaxuHub.go
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	//"time"
)

const (
	ConfigFileName     = "laxuhub_config.ini"
	GreenDirConfigFile = "green_dir.json"
	ConfigVersion      = "1.0"
)

// 新增数据结构
type GreenDirConfig struct {
	Version      string                    `json:"version"`
	Environments map[string]LanguageConfig `json:"environments"`
}

type LanguageConfig struct {
	DisplayName       string            `json:"display_name"`
	BaseDir           string            `json:"base_dir"`
	PathDirs          []string          `json:"path_dirs"`
	EnvVars           map[string]string `json:"env_vars"`
	VersionPattern    string            `json:"version_pattern"`
	ValidationCommand []string          `json:"validation_command"`
}

var (
	basePath               string
	configLastEnvironments []string
	availableEnvironments  map[string][]string // language -> versions
	selectedEnvironments   []string
	myBinPath              string
	myBinSubPaths          []string
	greenDirConfig         GreenDirConfig // 新增全局配置
)

func main() {
	// 获取基础路径
	basePath = getBasePath()
	myBinPath = filepath.Join(basePath, "mybin")
	
	// 加载绿色目录配置
	loadGreenDirConfig()
	
	// 发现可用环境
	discoverEnvironments()
	
	// 加载用户配置
	loadConfig()
	
	// 主循环
	for {
		if len(configLastEnvironments) > 0 {
			showQuickStartMenu()
		} else {
			showEnvironmentSelection()
		}
		
		// 设置环境
		setupSelectedEnvironments(selectedEnvironments)
		
		// 验证环境
		validateCommands()
		
		// 启动环境
		startEnvironment()
		
		break
	}
}

func getBasePath() string {
	if basePath != "" {
		return basePath
	}
	
	// 获取可执行文件所在目录
	exePath, err := os.Executable()
	if err != nil {
		fmt.Printf("获取可执行文件路径失败: %v\n", err)
		os.Exit(1)
	}
	return filepath.Dir(exePath)
}

// 新增：加载绿色目录配置
func loadGreenDirConfig() {
	configPath := filepath.Join(basePath, GreenDirConfigFile)
	
	// 如果JSON文件不存在，使用默认配置
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		greenDirConfig = getDefaultGreenDirConfig()
		return
	}
	
	file, err := os.Open(configPath)
	if err != nil {
		fmt.Printf("读取 %s 失败: %v, 使用默认配置\n", GreenDirConfigFile, err)
		greenDirConfig = getDefaultGreenDirConfig()
		return
	}
	defer file.Close()
	
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&greenDirConfig); err != nil {
		fmt.Printf("解析 %s 失败: %v, 使用默认配置\n", GreenDirConfigFile, err)
		greenDirConfig = getDefaultGreenDirConfig()
		return
	}
}

// 新增：默认配置
func getDefaultGreenDirConfig() GreenDirConfig {
	return GreenDirConfig{
		Version: "1.0",
		Environments: map[string]LanguageConfig{
			"python": {
				DisplayName:       "Python",
				BaseDir:           "green_python",
				PathDirs:          []string{"", "Scripts"},
				EnvVars:           map[string]string{"PYTHON_HOME": "{full_path}"},
				VersionPattern:    "python*",
				ValidationCommand: []string{"--version"},
			},
			"node": {
				DisplayName:       "Node.js",
				BaseDir:           "green_node",
				PathDirs:          []string{""},
				EnvVars:           map[string]string{"JC_HOME": "{full_path}"},
				VersionPattern:    "node*",
				ValidationCommand: []string{"--version"},
			},
			"go": {
				DisplayName:       "Go",
				BaseDir:           "green_go",
				PathDirs:          []string{"bin"},
				EnvVars:           map[string]string{"GO_ROOT": "{full_path}", "GO_HOME": "{full_path}/bin"},
				VersionPattern:    "go*",
				ValidationCommand: []string{"version"},
			},
			"java": {
				DisplayName:       "Java",
				BaseDir:           "green_java",
				PathDirs:          []string{"bin"},
				EnvVars:           map[string]string{"JAVA_ROOT": "{full_path}", "JAVA_HOME": "{full_path}/bin"},
				VersionPattern:    "java*",
				ValidationCommand: []string{"--version"},
			},
		},
	}
}

// 修改：环境发现函数
func discoverEnvironments() {
	availableEnvironments = make(map[string][]string)
	
	for langKey, langConfig := range greenDirConfig.Environments {
		langDir := filepath.Join(basePath, langConfig.BaseDir)
		
		// 检查基础目录是否存在
		if _, err := os.Stat(langDir); os.IsNotExist(err) {
			continue
		}
		
		// 使用 os.ReadDir 遍历所有目录，进行不区分大小写的匹配
		files, err := os.ReadDir(langDir)
		if err != nil {
			continue
		}
		
		var versions []string
		lowerLang := strings.ToLower(langKey)
		
		for _, file := range files {
			if file.IsDir() {
				dirName := file.Name()
				lowerDirName := strings.ToLower(dirName)
				
				// 不区分大小写的匹配：目录名以语言名开头
				if strings.HasPrefix(lowerDirName, lowerLang) {
					versions = append(versions, dirName)
				}
			}
		}
		
		if len(versions) > 0 {
			sort.Strings(versions)
			availableEnvironments[langKey] = versions
		}
	}
	
	// 扫描 mybin 子目录（保持不变）
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
			configLastEnvironments = strings.Fields(envs)
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
	
	content := fmt.Sprintf("[Settings]\nLastEnvironments=%s\nConfigVersion=%s\n",
		strings.Join(selectedEnvironments, " "), ConfigVersion)
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
	fmt.Println()
	fmt.Println("   ================================")
	fmt.Println("       环境配置 - 多语言选择")
	fmt.Println("   ================================")
	fmt.Println()
	fmt.Println("   请选择要使用的环境（可多选，输入多个编号用空格分隔）")
	fmt.Println()
	
	// 显示可用环境
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
	fmt.Println()
	fmt.Println("   示例: 1 3 5  (选择多个环境)")
	fmt.Println()
	
	// 获取用户输入
	fmt.Print("请输入要选择的环境编号: ")
	reader := bufio.NewReader(os.Stdin)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(input)
	
	if input == "0" {
		saveConfig()
		return
	}
	
	// 解析选择
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
		
		// 检查语言是否已选择
		if selectedLanguages[lang] {
			fmt.Printf("语言 %s 已选择，跳过重复选择\n", lang)
			continue
		}
		
		selectedLanguages[lang] = true
		selectedEnvironments = append(selectedEnvironments, envKey)
	}
	
	if len(selectedEnvironments) == 0 {
		fmt.Println("错误：未选择任何环境！")
		showEnvironmentSelection()
		return
	}
	
	saveConfig()
}

// 修改：环境设置函数
func setupSelectedEnvironments(envs []string) {
	fmt.Println()
	fmt.Println("   ================================")
	fmt.Println("       快速启动环境")
	fmt.Println("   ================================")
	fmt.Println()
	fmt.Printf("   正在启动: %s\n", strings.Join(envs, " "))
	fmt.Println()
	fmt.Println("   ================================")
	
	// 设置基础路径
	currentPath := os.Getenv("PATH")
	newPath := currentPath
	
	// 添加 mybin 路径
	newPath = myBinPath + string(os.PathListSeparator) + newPath
	
	// 添加 mybin 子目录
	for _, subPath := range myBinSubPaths {
		newPath = subPath + string(os.PathListSeparator) + newPath
	}
	
	// 设置各语言环境
	for _, env := range envs {
		parts := strings.Split(env, "_")
		if len(parts) < 2 {
			continue
		}
		
		lang := parts[0]
		version := strings.Join(parts[1:], "_")
		
		fmt.Printf("[设置 %s 环境: %s]...\n", lang, version)
		
		// 从配置获取语言设置
		langConfig, exists := greenDirConfig.Environments[lang]
		if !exists {
			continue
		}
		
		fullPath := filepath.Join(basePath, langConfig.BaseDir, version)
		
		// 设置环境变量
		for envVar, valueTemplate := range langConfig.EnvVars {
			value := strings.Replace(valueTemplate, "{full_path}", fullPath, -1)
			os.Setenv(envVar, value)
		}
		
		// 添加 PATH
		for _, pathDir := range langConfig.PathDirs {
			pathToAdd := fullPath
			if pathDir != "" {
				pathToAdd = filepath.Join(fullPath, pathDir)
			}
			newPath = pathToAdd + string(os.PathListSeparator) + newPath
		}
	}
	
	os.Setenv("PATH", newPath)
	
	// 设置 clink 环境变量
	tempDir := filepath.Join(basePath, "data", "temp")
	os.Setenv("CLINK_PROFILE", tempDir)
}

// 修改：命令验证函数
func validateCommands() {
	fmt.Println()
	fmt.Println("================================")
	fmt.Println("   环境变量设置完成：")
	fmt.Println("================================")
	
	// 显示设置的环境变量
	for _, env := range selectedEnvironments {
		parts := strings.Split(env, "_")
		if len(parts) < 1 {
			continue
		}
		langKey := parts[0]
		
		if langConfig, exists := greenDirConfig.Environments[langKey]; exists {
			for envVar := range langConfig.EnvVars {
				if value := os.Getenv(envVar); value != "" {
					fmt.Printf("%s: %s\n", envVar, value)
				}
			}
		}
	}
	
	fmt.Println()
	fmt.Println("PATH:", os.Getenv("PATH"))
	fmt.Println()
	
	// 调用镜像源设置
	mirrorBat := filepath.Join(myBinPath, "cn_mirror.bat")
	if _, err := os.Stat(mirrorBat); err == nil {
		fmt.Println("设置镜像源...")
		
		cmd := exec.Command(mirrorBat)
		cmd.Stdout = os.Stdout  // 显示批处理的输出
		cmd.Stderr = os.Stderr  // 显示错误信息
		
		err := cmd.Run()
		if err != nil {
			fmt.Printf("镜像源设置执行失败: %v\n", err)
		}
	} else {
		fmt.Println("cn_mirror.bat 文件不存在，使用默认源")
	}
	
	fmt.Println("================================")
	fmt.Println("   验证命令可用性：")
	fmt.Println("================================")
	
	// 验证命令
	for _, env := range selectedEnvironments {
		parts := strings.Split(env, "_")
		if len(parts) < 1 {
			continue
		}
		langKey := parts[0]
		
		if langConfig, exists := greenDirConfig.Environments[langKey]; exists && len(langConfig.ValidationCommand) > 0 {
			cmd := exec.Command(langKey, langConfig.ValidationCommand...)
			if err := cmd.Run(); err == nil {
				fmt.Printf("✓ %s 命令可用\n", langConfig.DisplayName)
			} else {
				fmt.Printf("✗ %s 命令不可用\n", langConfig.DisplayName)
			}
		}
	}
	
	fmt.Println()
}

func startEnvironment() {
/* 	fmt.Println("================================")
	fmt.Println("   启动开发环境")
	fmt.Println("================================")
	
	// 显示当前设置的环境
	fmt.Println("已设置的环境:")
	for _, env := range selectedEnvironments {
		parts := strings.Split(env, "_")
		if len(parts) < 1 {
			continue
		}
		langKey := parts[0]
		
		if langConfig, exists := greenDirConfig.Environments[langKey]; exists {
			fmt.Printf("  %s: %s\n", langConfig.DisplayName, strings.Join(parts[1:], "_"))
		}
	} */
	fmt.Println()
	
	// 切换到工作目录
	workDir := filepath.Join(os.Getenv("USERPROFILE"), "Desktop")
	if _, err := os.Stat(workDir); os.IsNotExist(err) {
		workDir, _ = os.Getwd()
	}
	os.Chdir(workDir)
	fmt.Printf("工作目录: %s\n", workDir)
	fmt.Println()
	
	// 设置 Clink 环境变量（保持与原批处理一致）
	tempDir := filepath.Join(basePath, "data", "temp")
	os.Setenv("CLINK_PROFILE", tempDir)
	
	// 清理 Clink 临时文件
	cleanupClinkTempFiles(tempDir)
	
	// 检查并启动 Clink
	clinkPath := filepath.Join(myBinPath, "sub_clink", "clink.bat")
	if _, err := os.Stat(clinkPath); err == nil {
		fmt.Println("正在启动 Clink 增强命令行...")
		fmt.Println()
		
		// 给用户一点时间阅读信息
		//time.Sleep(2 * time.Second)
		
		// 使用 clink.bat 启动增强命令行
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
		fmt.Printf("Clink 路径: %s\n", clinkPath)
		fmt.Println("提示: 在新窗口中可以使用设置好的所有开发环境")
		fmt.Println("      输入 exit 可以退出该环境")
		fmt.Println()
		
		//time.Sleep(2 * time.Second)
		
		// Fallback: 启动普通命令行
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

// 清理 Clink 临时文件函数
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
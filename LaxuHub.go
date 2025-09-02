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
)

const (
	ConfigFileName     = "laxuhub_config.ini"
	GreenDirConfigFile = "green_dir.json"
	ConfigVersion      = "1.0"
)

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
            fmt.Printf("工作目录设置为: %s\n", targetPath)
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
            fmt.Println("错误: 无上次配置记录，无法静默启动")
            fmt.Println("请先以交互模式运行并选择环境配置")
            fmt.Println("按回车键退出...")
            bufio.NewReader(os.Stdin).ReadBytes('\n')
            return
        }
        selectedEnvironments = configLastEnvironments
        fmt.Println("静默模式启动，使用上次配置...")
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

	file, err := os.Open(configPath)
	if err != nil {
		fmt.Printf("读取 %s 失败: %v\n", GreenDirConfigFile, err)
		os.Exit(1)
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&greenDirConfig); err != nil {
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
		lowerLang := strings.ToLower(langKey)

		for _, file := range files {
			if file.IsDir() {
				dirName := file.Name()
				lowerDirName := strings.ToLower(dirName)

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

	fmt.Print("请输入要选择的环境编号: ")
	reader := bufio.NewReader(os.Stdin)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(input)

	if input == "0" {
		saveConfig()
		return
	}

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

	if len(selectedEnvironments) == 0 {
		fmt.Println("错误：未选择任何环境！")
		showEnvironmentSelection()
		return
	}

	saveConfig()
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

	mirrorBat := filepath.Join(myBinPath, "cn_mirror.bat")
	if _, err := os.Stat(mirrorBat); err == nil {
		fmt.Println("设置镜像源...")

		cmd := exec.Command(mirrorBat)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr

		err := cmd.Run()
		if err != nil {
			fmt.Printf("镜像源设置执行失败: %v\n", err)
		}
	} else {
		fmt.Println("cn_mirror.bat 文件不存在，使用默认源")
	}

	fmt.Println("================================")
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
		fmt.Println("提示: 在新窗口中可以使用设置好的所有开发环境")
		fmt.Println("      输入 exit 可以退出该环境")
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

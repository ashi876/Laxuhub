//go build -ldflags="-s -w"
package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

var (
	level    int
	sortFlag bool
	sysFlag  bool  // 只显示系统程序
	allFlag  bool  // 显示所有程序（用户+系统）
	helpFlag bool
	pathFlag bool // 显示完整路径的标志
	exeFilesSet map[string]bool
	batFilesSet map[string]bool
	exeFilesPathSet map[string]string // 存储完整路径的映射
	batFilesPathSet map[string]string // 存储完整路径的映射
)

func shouldSkipDir(dirpath, systemDrive string) bool {
	// 如果显示所有程序或者只显示系统程序，则不跳过任何目录
	if allFlag || sysFlag {
		return false
	}
	
	skipPatterns := []string{"Windows", "Program Files", "Program Files (x86)", "Users"}
	fullPath := strings.ToLower(filepath.Clean(dirpath))
	systemDriveLower := strings.ToLower(systemDrive)

	// 检查是否在系统盘下
	if strings.HasPrefix(fullPath, systemDriveLower) {
		// 分割路径为各部分
		dirParts := strings.Split(fullPath, string(os.PathSeparator))
		for _, part := range dirParts {
			for _, pattern := range skipPatterns {
				if strings.Contains(part, strings.ToLower(pattern)) {
					return true
				}
			}
		}
	}
	return false
}

func isSystemDir(dirpath, systemDrive string) bool {
	systemPatterns := []string{"Windows", "Program Files", "Program Files (x86)"}
	fullPath := strings.ToLower(filepath.Clean(dirpath))
	systemDriveLower := strings.ToLower(systemDrive)

	// 检查是否在系统盘下
	if strings.HasPrefix(fullPath, systemDriveLower) {
		// 分割路径为各部分
		dirParts := strings.Split(fullPath, string(os.PathSeparator))
		for _, part := range dirParts {
			for _, pattern := range systemPatterns {
				if strings.Contains(part, strings.ToLower(pattern)) {
					return true
				}
			}
		}
	}
	return false
}

func showHelp() {
	fmt.Println("lspath - PATH环境变量exe和bat搜索工具")
	fmt.Println("作者:b站_碎辰a")
	fmt.Println("")
	fmt.Println("用法: lspath [选项]")
	fmt.Println("")
	fmt.Println("选项:")
	fmt.Println("  -l, -level int    搜索层级深度 (默认: 1)")
	fmt.Println("  -sort             按字母顺序排序并只显示文件名")
	fmt.Println("  -sys              只显示系统程序目录")
	fmt.Println("  -all              显示所有程序（用户+系统）")
	fmt.Println("  -path             显示完整路径排序")
	fmt.Println("  -h, -help         显示帮助信息")
	fmt.Println("")
	fmt.Println("示例:")
	fmt.Println("  lspath                     # 默认显示（用户+层级1）")
	fmt.Println("  lspath -sys                # 显示（系统）")
	fmt.Println("  lspath -all                # 显示所有程序（用户+系统）")
	fmt.Println("  lspath -path               # 显示完整路径(此参数默认排序)")	
	fmt.Println("  lspath -l 2                # 层级2,显示目录结构，有缩进和分类")
	fmt.Println("  lspath -l 2 -sort          # 只排序显示文件名，不显示目录结构")
	fmt.Println("  lspath -l 2 -path          # 排序显示完整路径")
	fmt.Println("  lspath -all -sort          # 排序显示所有程序名")
	fmt.Println("")
	fmt.Println("注意: 默认会跳过系统目录（Windows/Program Files等）")
}

func searchPath(maxDepth int) {
	systemDrive := os.Getenv("SystemDrive")
	if systemDrive == "" {
		systemDrive = "C:"
	}
	systemDrive = systemDrive + string(os.PathSeparator)

	pathEnv := os.Getenv("PATH")
	if pathEnv == "" {
		fmt.Println("PATH环境变量为空")
		return
	}

	// 如果是排序模式，初始化集合
	if sortFlag {
		exeFilesSet = make(map[string]bool)
		batFilesSet = make(map[string]bool)
		if pathFlag {
			exeFilesPathSet = make(map[string]string)
			batFilesPathSet = make(map[string]string)
		}
	}

	pathDirs := strings.Split(pathEnv, string(os.PathListSeparator))
	for _, dirpath := range pathDirs {
		dirpath = os.ExpandEnv(dirpath)
		if dirpath == "" {
			continue
		}

		// 检查目录是否存在
		if info, err := os.Stat(dirpath); err != nil || !info.IsDir() {
			continue
		}

		// 检查是否应该跳过该目录
		if shouldSkipDir(dirpath, systemDrive) {
			continue
		}

		// 如果只显示系统程序，跳过非系统目录
		if sysFlag && !isSystemDir(dirpath, systemDrive) {
			continue
		}

		// 非排序模式显示路径标题
		if !sortFlag {
			fmt.Printf("\n%s:\n", dirpath)
		}

		processDirectory(dirpath, maxDepth, 1, systemDrive)
	}

	// 如果是排序模式，将集合转换为切片，排序并输出
	if sortFlag {
		if pathFlag {
			// 显示完整路径模式
			outputFullPaths()
		} else {
			// 只显示文件名模式
			outputFilenamesOnly()
		}
	}
}

func outputFullPaths() {
	// 收集所有路径并排序
	allPaths := make([]string, 0)
	
	// 添加exe文件路径
	for path := range exeFilesPathSet {
		allPaths = append(allPaths, path)
	}
	
	// 添加bat文件路径
	for path := range batFilesPathSet {
		allPaths = append(allPaths, path)
	}
	
	// 按路径排序
	sort.Strings(allPaths)
	
	// 输出所有路径
	for _, path := range allPaths {
		fmt.Println(path)
	}
}

func outputFilenamesOnly() {
	// 转换exe文件集合为切片
	exeFiles := make([]string, 0, len(exeFilesSet))
	for filename := range exeFilesSet {
		exeFiles = append(exeFiles, filename)
	}
	
	// 转换bat文件集合为切片
	batFiles := make([]string, 0, len(batFilesSet))
	for filename := range batFilesSet {
		batFiles = append(batFiles, filename)
	}
	
	// 排序
	sort.Strings(exeFiles)
	sort.Strings(batFiles)
	
	// 先输出exe文件
	for _, filename := range exeFiles {
		fmt.Println(filename)
	}
	// 再输出bat文件
	for _, filename := range batFiles {
		fmt.Println(filename)
	}
}

func processDirectory(dirpath string, maxDepth, currentDepth int, systemDrive string) {
	entries, err := os.ReadDir(dirpath)
	if err != nil {
		if !sortFlag { // 只在非排序模式显示错误信息
			printIndent(currentDepth)
			if os.IsPermission(err) {
				fmt.Printf("无权限访问: %s\n", dirpath)
			} else {
				fmt.Printf("访问错误: %s - %s\n", dirpath, err.Error())
			}
		}
		return
	}

	for _, entry := range entries {
		fullPath := filepath.Join(dirpath, entry.Name())
		
		if entry.IsDir() {
			if maxDepth > 1 && !shouldSkipDir(fullPath, systemDrive) {
				// 如果只显示系统程序，跳过非系统目录
				if sysFlag && !isSystemDir(fullPath, systemDrive) {
					continue
				}
				
				if !sortFlag { // 只在非排序模式显示目录
					printIndent(currentDepth)
					fmt.Printf("%s/\n", entry.Name())
				}
				processDirectory(fullPath, maxDepth-1, currentDepth+1, systemDrive)
			}
		} else {
			// 检查文件扩展名
			lowerName := strings.ToLower(entry.Name())
			if strings.HasSuffix(lowerName, ".exe") {
				if sortFlag {
					if pathFlag {
						// 存储完整路径
						exeFilesPathSet[fullPath] = fullPath
					} else {
						// 存储文件名
						exeFilesSet[entry.Name()] = true
					}
				} else {
					// 非排序模式：正常显示
					printIndent(currentDepth)
					if pathFlag {
						fmt.Printf("%s\n", fullPath)
					} else {
						fmt.Printf("%s\n", entry.Name())
					}
				}
			} else if strings.HasSuffix(lowerName, ".bat") {
				if sortFlag {
					if pathFlag {
						// 存储完整路径
						batFilesPathSet[fullPath] = fullPath
					} else {
						// 存储文件名
						batFilesSet[entry.Name()] = true
					}
				} else {
					// 非排序模式：正常显示
					printIndent(currentDepth)
					if pathFlag {
						fmt.Printf("%s\n", fullPath)
					} else {
						fmt.Printf("%s\n", entry.Name())
					}
				}
			}
		}
	}
}

func printIndent(depth int) {
	for i := 0; i < depth; i++ {
		fmt.Print("  ")
	}
}

func main() {
	// 使用flag.IntVar和flag.BoolVar来支持参数不分先后
	fmt.Println("")
	flag.IntVar(&level, "l", 1, "搜索层级深度 (默认: 1)")
	flag.IntVar(&level, "level", 1, "搜索层级深度 (默认: 1)")
	flag.BoolVar(&sortFlag, "sort", false, "按字母顺序排序并只显示文件名")
	flag.BoolVar(&sysFlag, "sys", false, "只显示系统程序目录")
	flag.BoolVar(&allFlag, "all", false, "显示所有程序（用户+系统）")
	flag.BoolVar(&pathFlag, "path", false, "显示完整路径")
	flag.BoolVar(&helpFlag, "h", false, "显示帮助信息")
	flag.BoolVar(&helpFlag, "help", false, "显示帮助信息")
	flag.Parse()

	// -path 自动启用排序和去重(map自动去重)功能
	if pathFlag {
		sortFlag = true
	}
	
	// 显示帮助信息
	if helpFlag {
		showHelp()
		return
	}

	if level < 1 {
		fmt.Println("错误: 层级深度必须大于0")
		os.Exit(1)
	}

	searchPath(level)
}
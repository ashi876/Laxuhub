package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	// Get program directory
	exePath, err := os.Executable()
	if err != nil {
		fmt.Printf("Error: Cannot get program path - %v\n", err)
		return
	}
	exeDir := filepath.Dir(exePath)

	// Model file path (in program directory)
	modelFilePath := filepath.Join(exeDir, "laxusave_model.bat")

	// Check if model file exists
	if _, err := os.Stat(modelFilePath); os.IsNotExist(err) {
		fmt.Printf("Error: Model file %s does not exist\n", modelFilePath)
		return
	}

	// Read model file content
	content, err := os.ReadFile(modelFilePath)
	if err != nil {
		fmt.Printf("Error: Cannot read model file - %v\n", err)
		return
	}

	// Get all environment variables
	envVars := os.Environ()

	// Build set commands for batch file
	var setCommands []string
	for _, env := range envVars {
		// Split variable name and value
		pair := strings.SplitN(env, "=", 2)
		if len(pair) != 2 {
			continue
		}
		key, value := pair[0], pair[1]
		
		// Filter invalid environment variables
		if shouldIgnoreEnvVar(key) {
			continue
		}
		
		// Escape value
		value = strings.ReplaceAll(value, `"`, `""`)
		// Build set command
		setCommands = append(setCommands, fmt.Sprintf(`set "%s=%s"`, key, value))
	}

	// Convert content to string
	fileContent := string(content)

	// Check if ##swap## marker exists
	if !strings.Contains(fileContent, "##swap##") {
		fmt.Printf("Error: ##swap## marker not found in model file\n")
		return
	}

	// Build environment variables section
	envSection := strings.Join(setCommands, "\n")

	// Replace ##swap## marker with environment variables
	newContent := strings.Replace(fileContent, "##swap##", envSection, 1)

	// Determine target filename
	targetFilePath := getTargetFileName()
	if targetFilePath == "" {
		fmt.Println("Error: Cannot find available filename (01.bat to 99.bat all exist)")
		return
	}

	// Write new file (in current working directory)
	err = os.WriteFile(targetFilePath, []byte(newContent), 0644)
	if err != nil {
		fmt.Printf("Error: Cannot write file %s - %v\n", targetFilePath, err)
		return
	}

	fmt.Printf("Successfully generated: %s\n", targetFilePath)
	fmt.Printf("Restored environment variables (%d variables, filtered invalid ones)\n", len(setCommands))
}

// shouldIgnoreEnvVar determines if an environment variable should be ignored
func shouldIgnoreEnvVar(key string) bool {
	// Ignore empty variable names
	if key == "" {
		return true
	}
	
	// Ignore variables starting with = (like "=C:", "=ExitCode", etc.)
	if strings.HasPrefix(key, "=") {
		return true
	}
	
	// Ignore PROMPT environment variable (often displays as garbled text)
	if strings.EqualFold(key, "PROMPT") {
		return true
	}
	
	// Check if variable name contains invalid characters
	for _, char := range key {
		if !isValidEnvVarChar(char) {
			return true
		}
	}
	
	return false
}

// isValidEnvVarChar checks if a character is valid for environment variable names
func isValidEnvVarChar(c rune) bool {
	// Allow letters, numbers, underscore
	if (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || 
	   (c >= '0' && c <= '9') || c == '_' {
		return true
	}
	return false
}

// getTargetFileName returns available target filename
func getTargetFileName() string {
	// If command line arguments exist, use specified filename
	if len(os.Args) >= 2 {
		fileName := os.Args[1]
		if !strings.HasSuffix(strings.ToLower(fileName), ".bat") {
			fileName += ".bat"
		}
		return fileName
	}

	// Without arguments, automatically find available filename from 01.bat to 99.bat
	for i := 1; i <= 99; i++ {
		// Format as two digits
		fileName := fmt.Sprintf("%02d.bat", i)

		// Check if file exists
		if _, err := os.Stat(fileName); os.IsNotExist(err) {
			return fileName
		}
	}

	return "" // All files exist
}
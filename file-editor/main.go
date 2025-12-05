package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"regexp"
	"strconv"
	"strings"
)

type FileEditor struct {
	filename string
	lines    []string
	modified bool
}

func NewFileEditor(filename string) (*FileEditor, error) {
	editor := &FileEditor{
		filename: filename,
		lines:    []string{},
		modified: false,
	}

	if err := editor.loadFile(); err != nil {
		return nil, fmt.Errorf("failed to load file: %w", err)
	}

	return editor, nil
}

func (fe *FileEditor) loadFile() error {
	if _, err := os.Stat(fe.filename); os.IsNotExist(err) {
		log.Printf("INFO: File %s does not exist, creating new file", fe.filename)
		return nil
	}

	file, err := os.Open(fe.filename)
	if err != nil {
		return fmt.Errorf("cannot open file: %w", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		fe.lines = append(fe.lines, scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		return fmt.Errorf("error reading file: %w", err)
	}

	log.Printf("INFO: Loaded %d lines from %s", len(fe.lines), fe.filename)
	return nil
}

func (fe *FileEditor) save() error {
	file, err := os.Create(fe.filename)
	if err != nil {
		return fmt.Errorf("cannot create file: %w", err)
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	for _, line := range fe.lines {
		if _, err := writer.WriteString(line + "\n"); err != nil {
			return fmt.Errorf("error writing line: %w", err)
		}
	}

	if err := writer.Flush(); err != nil {
		return fmt.Errorf("error flushing writer: %w", err)
	}

	fe.modified = false
	log.Printf("INFO: Saved %d lines to %s", len(fe.lines), fe.filename)
	return nil
}

func (fe *FileEditor) display() {
	fmt.Printf("\n=== File: %s ===\n", fe.filename)
	for i, line := range fe.lines {
		fmt.Printf("%4d: %s\n", i+1, line)
	}
	fmt.Printf("=== Total lines: %d ===\n", len(fe.lines))
}

func (fe *FileEditor) insertLine(lineNum int, text string) error {
	if lineNum < 1 || lineNum > len(fe.lines)+1 {
		return fmt.Errorf("invalid line number: %d", lineNum)
	}

	index := lineNum - 1
	fe.lines = append(fe.lines[:index], append([]string{text}, fe.lines[index:]...)...)
	fe.modified = true
	log.Printf("INFO: Inserted line at %d", lineNum)
	return nil
}

func (fe *FileEditor) deleteLine(lineNum int) error {
	if lineNum < 1 || lineNum > len(fe.lines) {
		return fmt.Errorf("invalid line number: %d", lineNum)
	}

	index := lineNum - 1
	fe.lines = append(fe.lines[:index], fe.lines[index+1:]...)
	fe.modified = true
	log.Printf("INFO: Deleted line %d", lineNum)
	return nil
}

func (fe *FileEditor) replaceLine(lineNum int, text string) error {
	if lineNum < 1 || lineNum > len(fe.lines) {
		return fmt.Errorf("invalid line number: %d", lineNum)
	}

	fe.lines[lineNum-1] = text
	fe.modified = true
	log.Printf("INFO: Replaced line %d", lineNum)
	return nil
}

func (fe *FileEditor) searchAndReplace(pattern, replacement string, global bool) error {
	regex, err := regexp.Compile(pattern)
	if err != nil {
		return fmt.Errorf("invalid regex pattern: %w", err)
	}

	count := 0
	for i, line := range fe.lines {
		if global {
			newLine := regex.ReplaceAllString(line, replacement)
			if newLine != line {
				fe.lines[i] = newLine
				count++
			}
		} else {
			if regex.MatchString(line) {
				fe.lines[i] = regex.ReplaceAllString(line, replacement)
				count++
				break
			}
		}
	}

	if count > 0 {
		fe.modified = true
		log.Printf("INFO: Replaced %d occurrences", count)
	}
	return nil
}

func (fe *FileEditor) search(pattern string) ([]int, error) {
	regex, err := regexp.Compile(pattern)
	if err != nil {
		return nil, fmt.Errorf("invalid regex pattern: %w", err)
	}

	var matches []int
	for i, line := range fe.lines {
		if regex.MatchString(line) {
			matches = append(matches, i+1)
		}
	}

	return matches, nil
}

func (fe *FileEditor) appendLine(text string) {
	fe.lines = append(fe.lines, text)
	fe.modified = true
	log.Printf("INFO: Appended line")
}

func (fe *FileEditor) copyLines(start, end int) ([]string, error) {
	if start < 1 || end < 1 || start > len(fe.lines) || end > len(fe.lines) || start > end {
		return nil, fmt.Errorf("invalid line range: %d-%d", start, end)
	}

	copied := make([]string, end-start+1)
	copy(copied, fe.lines[start-1:end])
	log.Printf("INFO: Copied lines %d-%d", start, end)
	return copied, nil
}

func (fe *FileEditor) pasteLines(lineNum int, lines []string) error {
	if lineNum < 1 || lineNum > len(fe.lines)+1 {
		return fmt.Errorf("invalid line number: %d", lineNum)
	}

	index := lineNum - 1
	fe.lines = append(fe.lines[:index], append(lines, fe.lines[index:]...)...)
	fe.modified = true
	log.Printf("INFO: Pasted %d lines at line %d", len(lines), lineNum)
	return nil
}

func printUsage() {
	fmt.Println(`
File Editor Tool - Production Grade File Operations

USAGE:
    file-editor <filename>

COMMANDS:
    display, d                    - Display file contents
    insert <line> <text>         - Insert text at line number
    delete <line>                - Delete line number
    replace <line> <text>        - Replace line with text
    append <text>                - Append text to end of file
    search <pattern>             - Search for regex pattern
    substitute <pattern> <repl>  - Replace first match of pattern
    global <pattern> <repl>      - Replace all matches of pattern
    copy <start> <end>           - Copy lines to clipboard
    paste <line>                 - Paste clipboard at line
    save, w                      - Save file
    quit, q                      - Quit (warns if unsaved)
    help, h                      - Show this help

EXAMPLES:
    insert 5 "Hello World"       - Insert "Hello World" at line 5
    delete 10                    - Delete line 10
    search "func.*main"          - Find lines matching regex
    substitute "old" "new"       - Replace first "old" with "new"
    global "TODO" "DONE"         - Replace all "TODO" with "DONE"
`)
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "ERROR: Usage: %s <filename>\n", os.Args[0])
		os.Exit(1)
	}

	filename := os.Args[1]
	editor, err := NewFileEditor(filename)
	if err != nil {
		log.Fatalf("ERROR: %v", err)
	}

	var clipboard []string
	scanner := bufio.NewScanner(os.Stdin)

	fmt.Printf("File Editor - Editing: %s\n", filename)
	fmt.Println("Type 'help' for commands")

	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}

		input := strings.TrimSpace(scanner.Text())
		if input == "" {
			continue
		}

		parts := strings.Fields(input)
		command := parts[0]

		switch command {
		case "display", "d":
			editor.display()

		case "insert":
			if len(parts) < 3 {
				fmt.Println("ERROR: Usage: insert <line> <text>")
				continue
			}
			lineNum, err := strconv.Atoi(parts[1])
			if err != nil {
				fmt.Printf("ERROR: Invalid line number: %s\n", parts[1])
				continue
			}
			text := strings.Join(parts[2:], " ")
			if err := editor.insertLine(lineNum, text); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			}

		case "delete":
			if len(parts) != 2 {
				fmt.Println("ERROR: Usage: delete <line>")
				continue
			}
			lineNum, err := strconv.Atoi(parts[1])
			if err != nil {
				fmt.Printf("ERROR: Invalid line number: %s\n", parts[1])
				continue
			}
			if err := editor.deleteLine(lineNum); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			}

		case "replace":
			if len(parts) < 3 {
				fmt.Println("ERROR: Usage: replace <line> <text>")
				continue
			}
			lineNum, err := strconv.Atoi(parts[1])
			if err != nil {
				fmt.Printf("ERROR: Invalid line number: %s\n", parts[1])
				continue
			}
			text := strings.Join(parts[2:], " ")
			if err := editor.replaceLine(lineNum, text); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			}

		case "append":
			if len(parts) < 2 {
				fmt.Println("ERROR: Usage: append <text>")
				continue
			}
			text := strings.Join(parts[1:], " ")
			editor.appendLine(text)

		case "search":
			if len(parts) != 2 {
				fmt.Println("ERROR: Usage: search <pattern>")
				continue
			}
			matches, err := editor.search(parts[1])
			if err != nil {
				fmt.Printf("ERROR: %v\n", err)
				continue
			}
			if len(matches) == 0 {
				fmt.Println("No matches found")
			} else {
				fmt.Printf("Found matches at lines: %v\n", matches)
			}

		case "substitute":
			if len(parts) != 3 {
				fmt.Println("ERROR: Usage: substitute <pattern> <replacement>")
				continue
			}
			if err := editor.searchAndReplace(parts[1], parts[2], false); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			}

		case "global":
			if len(parts) != 3 {
				fmt.Println("ERROR: Usage: global <pattern> <replacement>")
				continue
			}
			if err := editor.searchAndReplace(parts[1], parts[2], true); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			}

		case "copy":
			if len(parts) != 3 {
				fmt.Println("ERROR: Usage: copy <start> <end>")
				continue
			}
			start, err1 := strconv.Atoi(parts[1])
			end, err2 := strconv.Atoi(parts[2])
			if err1 != nil || err2 != nil {
				fmt.Println("ERROR: Invalid line numbers")
				continue
			}
			copied, err := editor.copyLines(start, end)
			if err != nil {
				fmt.Printf("ERROR: %v\n", err)
			} else {
				clipboard = copied
			}

		case "paste":
			if len(parts) != 2 {
				fmt.Println("ERROR: Usage: paste <line>")
				continue
			}
			if len(clipboard) == 0 {
				fmt.Println("ERROR: Clipboard is empty")
				continue
			}
			lineNum, err := strconv.Atoi(parts[1])
			if err != nil {
				fmt.Printf("ERROR: Invalid line number: %s\n", parts[1])
				continue
			}
			if err := editor.pasteLines(lineNum, clipboard); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			}

		case "save", "w":
			if err := editor.save(); err != nil {
				fmt.Printf("ERROR: %v\n", err)
			} else {
				fmt.Println("File saved successfully")
			}

		case "quit", "q":
			if editor.modified {
				fmt.Print("File has unsaved changes. Save before quitting? (y/n): ")
				if scanner.Scan() {
					response := strings.ToLower(strings.TrimSpace(scanner.Text()))
					if response == "y" || response == "yes" {
						if err := editor.save(); err != nil {
							fmt.Printf("ERROR: Failed to save: %v\n", err)
							continue
						}
					}
				}
			}
			fmt.Println("Goodbye!")
			os.Exit(0)

		case "help", "h":
			printUsage()

		default:
			fmt.Printf("ERROR: Unknown command: %s (type 'help' for commands)\n", command)
		}
	}

	if err := scanner.Err(); err != nil {
		log.Fatalf("ERROR: Input error: %v", err)
	}
}
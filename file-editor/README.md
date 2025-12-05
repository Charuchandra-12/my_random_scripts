# File Editor Tool

A production-grade Go binary that provides comprehensive file editing operations similar to vi/vim/nano editors.

## Features

- **File Operations**: Create, load, save files with proper error handling
- **Line Editing**: Insert, delete, replace, append lines with validation
- **Search & Replace**: Regex-based search with global/single replacement
- **Copy/Paste**: Internal clipboard for line operations
- **Interactive Shell**: Command-line interface with help system
- **Safety**: Warns about unsaved changes before quitting

## Installation

```bash
cd file-editor
go build -o file-editor main.go
```

## Usage

```bash
./file-editor <filename>
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `display`, `d` | Show file contents | `display` |
| `insert <line> <text>` | Insert text at line | `insert 5 "Hello World"` |
| `delete <line>` | Delete line | `delete 10` |
| `replace <line> <text>` | Replace line | `replace 3 "New content"` |
| `append <text>` | Add line to end | `append "Footer text"` |
| `search <pattern>` | Find regex matches | `search "func.*main"` |
| `substitute <pattern> <repl>` | Replace first match | `substitute "old" "new"` |
| `global <pattern> <repl>` | Replace all matches | `global "TODO" "DONE"` |
| `copy <start> <end>` | Copy lines to clipboard | `copy 1 5` |
| `paste <line>` | Paste at line | `paste 10` |
| `save`, `w` | Save file | `save` |
| `quit`, `q` | Exit (warns if unsaved) | `quit` |
| `help`, `h` | Show help | `help` |

## Example Session

```bash
$ ./file-editor test.txt
File Editor - Editing: test.txt
Type 'help' for commands
> append "First line"
> append "Second line"
> display
=== File: test.txt ===
   1: First line
   2: Second line
=== Total lines: 2 ===
> insert 2 "Middle line"
> substitute "First" "Initial"
> save
File saved successfully
> quit
Goodbye!
```

## Design Decisions

- **Memory-based editing**: Loads entire file into memory for fast operations
- **Regex support**: Uses Go's regexp package for powerful search/replace
- **Error handling**: Comprehensive validation with descriptive error messages
- **Interactive mode**: REPL-style interface for ease of use
- **Safety features**: Unsaved change warnings and input validation
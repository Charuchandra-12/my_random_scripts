# GitOps - Interactive Git Operations Tool

A production-grade Go binary for performing Git operations through an interactive menu interface.

## Features

- **Interactive Menu**: Easy-to-use numbered menu system
- **Comprehensive Git Operations**: Covers all common Git commands
- **Colored Output**: Enhanced terminal visibility with color-coded logs
- **Error Handling**: Robust error handling with meaningful messages
- **Input Validation**: Validates required parameters before execution
- **Structured Logging**: Timestamped logs with different severity levels

## Supported Operations

1. **Repository Management**
   - Clone Repository
   - Initialize Repository
   - Add Remote
   - Show Remotes

2. **File Operations**
   - Add Files
   - Commit Changes
   - Show Status
   - Show Diff

3. **Branch Management**
   - Create Branch
   - Switch Branch
   - Merge Branch
   - Delete Branch
   - Show Branches

4. **Remote Operations**
   - Push Changes
   - Pull Changes
   - Fetch

5. **Advanced Operations**
   - Reset (soft/mixed/hard)
   - Stash/Apply Stash
   - Show Log

## Prerequisites

- Go 1.21 or higher
- Git installed and available in PATH

## Build & Run

```bash
# Build the binary
go build -o gitops main.go

# Run the tool
./gitops
```

## Usage Examples

### Clone a Repository
```
Select operation: 1
Enter repository URL: https://github.com/user/repo.git
Enter directory name (optional): my-project
```

### Create and Switch to New Branch
```
Select operation: 7
Enter new branch name: feature/new-feature
Checkout new branch? (y/n): y
```

### Commit Changes
```
Select operation: 3
Enter files to add (. for all): .

Select operation: 4
Enter commit message: Add new feature implementation
```

### Push to Remote
```
Select operation: 5
Enter remote name (default: origin): origin
Enter branch name (leave empty for current): 
```

## Design Decisions

- **Single Binary**: No external dependencies, easy deployment
- **Interactive Interface**: Reduces command-line complexity
- **Color-Coded Logs**: Improves user experience and error identification
- **Modular Functions**: Each Git operation has dedicated handler
- **Input Validation**: Prevents common user errors
- **Error Propagation**: Clear error messages with context

## Security Considerations

- No credential storage or handling
- Uses system Git configuration
- Validates input parameters
- Proper error handling prevents information leakage

## Exit Codes

- `0`: Success
- `1`: Git not found in PATH
- `>1`: Git command execution errors
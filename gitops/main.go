package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"time"
)

const (
	ColorReset  = "\033[0m"
	ColorRed    = "\033[31m"
	ColorGreen  = "\033[32m"
	ColorYellow = "\033[33m"
	ColorBlue   = "\033[34m"
	ColorPurple = "\033[35m"
	ColorCyan   = "\033[36m"
)

type GitOps struct {
	scanner *bufio.Scanner
}

func NewGitOps() *GitOps {
	return &GitOps{
		scanner: bufio.NewScanner(os.Stdin),
	}
}

func (g *GitOps) logInfo(msg string) {
	fmt.Printf("%s[INFO]%s %s %s\n", ColorGreen, ColorReset, time.Now().Format("15:04:05"), msg)
}

func (g *GitOps) logError(msg string) {
	fmt.Printf("%s[ERROR]%s %s %s\n", ColorRed, ColorReset, time.Now().Format("15:04:05"), msg)
}

func (g *GitOps) logWarn(msg string) {
	fmt.Printf("%s[WARN]%s %s %s\n", ColorYellow, ColorReset, time.Now().Format("15:04:05"), msg)
}

func (g *GitOps) prompt(message string) string {
	fmt.Printf("%s%s:%s ", ColorCyan, message, ColorReset)
	g.scanner.Scan()
	return strings.TrimSpace(g.scanner.Text())
}

func (g *GitOps) executeGit(args ...string) error {
	cmd := exec.Command("git", args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	
	g.logInfo(fmt.Sprintf("Executing: git %s", strings.Join(args, " ")))
	
	if err := cmd.Run(); err != nil {
		g.logError(fmt.Sprintf("Git command failed: %v", err))
		return err
	}
	
	g.logInfo("Command completed successfully")
	return nil
}

func (g *GitOps) showMenu() {
	fmt.Printf("\n%s=== Git Operations Tool ===%s\n", ColorBlue, ColorReset)
	fmt.Println("1.  Clone Repository")
	fmt.Println("2.  Initialize Repository")
	fmt.Println("3.  Add Files")
	fmt.Println("4.  Commit Changes")
	fmt.Println("5.  Push Changes")
	fmt.Println("6.  Pull Changes")
	fmt.Println("7.  Create Branch")
	fmt.Println("8.  Switch Branch")
	fmt.Println("9.  Merge Branch")
	fmt.Println("10. Delete Branch")
	fmt.Println("11. Show Status")
	fmt.Println("12. Show Log")
	fmt.Println("13. Show Branches")
	fmt.Println("14. Show Remotes")
	fmt.Println("15. Add Remote")
	fmt.Println("16. Fetch")
	fmt.Println("17. Reset")
	fmt.Println("18. Stash")
	fmt.Println("19. Apply Stash")
	fmt.Println("20. Show Diff")
	fmt.Println("0.  Exit")
	fmt.Printf("%s=========================%s\n", ColorBlue, ColorReset)
}

func (g *GitOps) handleClone() error {
	url := g.prompt("Enter repository URL")
	if url == "" {
		return fmt.Errorf("repository URL is required")
	}
	
	dir := g.prompt("Enter directory name (optional)")
	if dir != "" {
		return g.executeGit("clone", url, dir)
	}
	return g.executeGit("clone", url)
}

func (g *GitOps) handleInit() error {
	dir := g.prompt("Enter directory path (. for current)")
	if dir == "" {
		dir = "."
	}
	return g.executeGit("init", dir)
}

func (g *GitOps) handleAdd() error {
	files := g.prompt("Enter files to add (. for all)")
	if files == "" {
		files = "."
	}
	return g.executeGit("add", files)
}

func (g *GitOps) handleCommit() error {
	message := g.prompt("Enter commit message")
	if message == "" {
		return fmt.Errorf("commit message is required")
	}
	return g.executeGit("commit", "-m", message)
}

func (g *GitOps) handlePush() error {
	remote := g.prompt("Enter remote name (default: origin)")
	if remote == "" {
		remote = "origin"
	}
	
	branch := g.prompt("Enter branch name (leave empty for current)")
	if branch != "" {
		return g.executeGit("push", remote, branch)
	}
	return g.executeGit("push", remote)
}

func (g *GitOps) handlePull() error {
	remote := g.prompt("Enter remote name (default: origin)")
	if remote == "" {
		remote = "origin"
	}
	
	branch := g.prompt("Enter branch name (leave empty for current)")
	if branch != "" {
		return g.executeGit("pull", remote, branch)
	}
	return g.executeGit("pull", remote)
}

func (g *GitOps) handleCreateBranch() error {
	name := g.prompt("Enter new branch name")
	if name == "" {
		return fmt.Errorf("branch name is required")
	}
	
	checkout := g.prompt("Checkout new branch? (y/n)")
	if strings.ToLower(checkout) == "y" {
		return g.executeGit("checkout", "-b", name)
	}
	return g.executeGit("branch", name)
}

func (g *GitOps) handleSwitchBranch() error {
	name := g.prompt("Enter branch name")
	if name == "" {
		return fmt.Errorf("branch name is required")
	}
	return g.executeGit("checkout", name)
}

func (g *GitOps) handleMerge() error {
	branch := g.prompt("Enter branch to merge")
	if branch == "" {
		return fmt.Errorf("branch name is required")
	}
	return g.executeGit("merge", branch)
}

func (g *GitOps) handleDeleteBranch() error {
	branch := g.prompt("Enter branch to delete")
	if branch == "" {
		return fmt.Errorf("branch name is required")
	}
	
	force := g.prompt("Force delete? (y/n)")
	if strings.ToLower(force) == "y" {
		return g.executeGit("branch", "-D", branch)
	}
	return g.executeGit("branch", "-d", branch)
}

func (g *GitOps) handleAddRemote() error {
	name := g.prompt("Enter remote name")
	if name == "" {
		return fmt.Errorf("remote name is required")
	}
	
	url := g.prompt("Enter remote URL")
	if url == "" {
		return fmt.Errorf("remote URL is required")
	}
	
	return g.executeGit("remote", "add", name, url)
}

func (g *GitOps) handleReset() error {
	mode := g.prompt("Enter reset mode (soft/mixed/hard)")
	commit := g.prompt("Enter commit hash (HEAD for last commit)")
	
	if commit == "" {
		commit = "HEAD"
	}
	
	switch strings.ToLower(mode) {
	case "soft":
		return g.executeGit("reset", "--soft", commit)
	case "hard":
		return g.executeGit("reset", "--hard", commit)
	default:
		return g.executeGit("reset", commit)
	}
}

func (g *GitOps) handleStash() error {
	message := g.prompt("Enter stash message (optional)")
	if message != "" {
		return g.executeGit("stash", "push", "-m", message)
	}
	return g.executeGit("stash")
}

func (g *GitOps) run() {
	g.logInfo("Git Operations Tool started")
	
	for {
		g.showMenu()
		choice := g.prompt("Select operation")
		
		var err error
		
		switch choice {
		case "1":
			err = g.handleClone()
		case "2":
			err = g.handleInit()
		case "3":
			err = g.handleAdd()
		case "4":
			err = g.handleCommit()
		case "5":
			err = g.handlePush()
		case "6":
			err = g.handlePull()
		case "7":
			err = g.handleCreateBranch()
		case "8":
			err = g.handleSwitchBranch()
		case "9":
			err = g.handleMerge()
		case "10":
			err = g.handleDeleteBranch()
		case "11":
			err = g.executeGit("status")
		case "12":
			err = g.executeGit("log", "--oneline", "-10")
		case "13":
			err = g.executeGit("branch", "-a")
		case "14":
			err = g.executeGit("remote", "-v")
		case "15":
			err = g.handleAddRemote()
		case "16":
			err = g.executeGit("fetch")
		case "17":
			err = g.handleReset()
		case "18":
			err = g.handleStash()
		case "19":
			err = g.executeGit("stash", "pop")
		case "20":
			err = g.executeGit("diff")
		case "0":
			g.logInfo("Exiting Git Operations Tool")
			return
		default:
			g.logWarn("Invalid choice. Please try again.")
			continue
		}
		
		if err != nil {
			g.logError(fmt.Sprintf("Operation failed: %v", err))
		}
		
		fmt.Printf("\n%sPress Enter to continue...%s", ColorPurple, ColorReset)
		g.scanner.Scan()
	}
}

func main() {
	if _, err := exec.LookPath("git"); err != nil {
		log.Fatal("Git is not installed or not in PATH")
	}
	
	gitOps := NewGitOps()
	gitOps.run()
}
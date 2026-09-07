package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

func main() {
	if err := build(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
func build() error {
	root, err := os.Getwd()
	if err != nil {
		return err
	}
	for {
		if _, err := os.Stat(filepath.Join(root, "go.mod")); err == nil {
			break
		}
		parent := filepath.Dir(root)
		if parent == root {
			return fmt.Errorf("compiler go.mod not found")
		}
		root = parent
	}
	lab := filepath.Dir(root)
	web := filepath.Join(lab, "web")
	cmd := exec.Command("pnpm", "--dir", web, "run", "build")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err = cmd.Run(); err != nil {
		return err
	}
	for _, pair := range []struct{ source, target string }{{filepath.Join(web, "dist"), "assets"}, {filepath.Join(lab, "examples"), "presets"}, {filepath.Join(lab, "runtime"), "runtime"}} {
		dest := filepath.Join(root, "internal", "webui", pair.target)
		if err = os.RemoveAll(dest); err != nil {
			return err
		}
		if err = os.CopyFS(dest, os.DirFS(pair.source)); err != nil {
			return err
		}
	}
	return nil
}

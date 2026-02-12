#!/usr/bin/env python3
"""
Terminal - Command-line interface for ScutoidOS
"""

try:
    import neonpulse
    HAS_NEONPULSE = True
except ImportError:
    HAS_NEONPULSE = False

import os
import sys

class Terminal:
    def __init__(self):
        self.command_buffer = ""
        self.history = []
        self.history_index = 0
        self.running = True
        self.current_dir = "/Users/Default"
        self.apps_dir = None  # Set from env or default
        
    def _get_apps_dir(self):
        if self.apps_dir is None:
            base = os.environ.get("SCUTOIDOS_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.apps_dir = os.path.join(base, "Apps")
        return self.apps_dir
    
    def _list_installed_apps(self):
        """List app names from Apps/ (directories with info.json)"""
        apps_path = self._get_apps_dir()
        if not os.path.isdir(apps_path):
            return []
        out = []
        for name in sorted(os.listdir(apps_path)):
            path = os.path.join(apps_path, name)
            if os.path.isdir(path) and os.path.isfile(os.path.join(path, "info.json")):
                out.append(name)
        return out
    
    def print_prompt(self):
        """Display command prompt"""
        if HAS_NEONPULSE:
            neonpulse.set_color(0x0A)  # Green
            neonpulse.print(f"{self.current_dir} ")
            neonpulse.set_color(0x0F)  # White
            neonpulse.print(": ")
            neonpulse.set_color(0x07)  # Light grey
        else:
            print(f"{self.current_dir} : ", end='')
    
    def execute_command(self, cmd):
        """Execute a shell command"""
        parts = cmd.strip().split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command == "help":
            self.cmd_help()
        elif command == "clear" or command == "cls":
            self.cmd_clear()
        elif command == "ls":
            self.cmd_ls(args)
        elif command == "cd":
            self.cmd_cd(args)
        elif command == "pwd":
            self.cmd_pwd()
        elif command == "echo":
            self.cmd_echo(args)
        elif command == "uname":
            self.cmd_uname()
        elif command == "date":
            self.cmd_date()
        elif command == "apps":
            self.cmd_apps()
        elif command == "exit" or command == "quit":
            self.running = False
        else:
            self.print_output(f"Command not found: {command}\n")
            self.print_output("Type 'help' for available commands\n")
    
    def print_output(self, text):
        """Print command output"""
        if HAS_NEONPULSE:
            neonpulse.set_color(0x07)
            neonpulse.print(text)
        else:
            print(text, end='')
    
    def cmd_help(self):
        """Show help"""
        help_text = """
Available commands:
  help      - Show this help
  clear     - Clear screen
  ls        - List directory contents
  cd <dir>  - Change directory
  pwd       - Print working directory
  echo      - Echo text
  uname     - Show system information
  date      - Show current date
  apps      - List installed applications
  exit      - Exit terminal

"""
        self.print_output(help_text)
    
    def cmd_clear(self):
        """Clear screen"""
        if HAS_NEONPULSE:
            neonpulse.clear()
        else:
            os.system('clear' if os.name == 'posix' else 'cls')
    
    def cmd_ls(self, args):
        """List directory"""
        if self.current_dir == "/":
            items = ["Users/", "Apps/", "Other/", "installer/", "programs/"]
        elif self.current_dir == "/Apps" or self.current_dir.endswith("/Apps"):
            items = [d + "/" for d in self._list_installed_apps()]
            if not items:
                items = ["(no apps installed)"]
        elif self.current_dir.startswith("/Users"):
            items = ["Documents/", "Downloads/", "Desktop/"]
        else:
            items = ["(empty)"]
        
        for item in items:
            self.print_output(f"{item}\n")
    
    def cmd_cd(self, args):
        """Change directory"""
        if not args:
            self.current_dir = "/Users/Default"
        elif args[0] == "..":
            if self.current_dir != "/":
                parts = self.current_dir.rstrip('/').split('/')
                self.current_dir = '/'.join(parts[:-1]) or '/'
        elif args[0] == "/":
            self.current_dir = "/"
        else:
            if args[0].startswith('/'):
                self.current_dir = args[0]
            else:
                self.current_dir = f"{self.current_dir}/{args[0]}".replace('//', '/')
    
    def cmd_pwd(self):
        """Print working directory"""
        self.print_output(f"{self.current_dir}\n")
    
    def cmd_echo(self, args):
        """Echo text"""
        text = ' '.join(args)
        self.print_output(f"{text}\n")
    
    def cmd_uname(self):
        """System information"""
        self.print_output("ScutoidOS 0.1 (x86)\n")
    
    def cmd_date(self):
        """Show date"""
        self.print_output("2026-02-12 13:40:00\n")
    
    def cmd_apps(self):
        """List installed apps"""
        for name in self._list_installed_apps():
            self.print_output(f"  {name}\n")
    
    def handle_keyboard(self, char):
        """Process keyboard input"""
        if char == '\n':
            if HAS_NEONPULSE:
                neonpulse.print("\n")
            else:
                print()
            
            if self.command_buffer:
                self.history.append(self.command_buffer)
                self.execute_command(self.command_buffer)
                self.command_buffer = ""
            
            if self.running:
                self.print_prompt()
        elif char == '\b':
            if self.command_buffer:
                self.command_buffer = self.command_buffer[:-1]
                if HAS_NEONPULSE:
                    neonpulse.print("\r")
                    self.print_prompt()
                    neonpulse.print(self.command_buffer)
                    neonpulse.print(" \b")
        else:
            self.command_buffer += char
            if HAS_NEONPULSE:
                neonpulse.print(char)
            else:
                print(char, end='', flush=True)
    
    def run(self):
        """Main terminal loop"""
        if HAS_NEONPULSE:
            neonpulse.clear()
            neonpulse.set_color(0x0B)  # Cyan
            neonpulse.print("ScutoidOS Terminal v1.0\n")
            neonpulse.set_color(0x07)
            neonpulse.print("Type 'help' for available commands\n\n")
        else:
            print("ScutoidOS Terminal v1.0")
            print("Type 'help' for available commands\n")
        
        self.print_prompt()
        
        if not HAS_NEONPULSE:
            while self.running:
                try:
                    cmd = input()
                    self.execute_command(cmd)
                    if self.running:
                        self.print_prompt()
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting...")
                    break
        else:
            while self.running:
                if neonpulse.keyboard_available():
                    scancode = neonpulse.keyboard_read()
                    if scancode < 128:
                        char = neonpulse.scancode_to_ascii(scancode)
                        if char:
                            self.handle_keyboard(char)
                
                neonpulse.halt()

def main():
    term = Terminal()
    term.run()

if __name__ == "__main__":
    main()

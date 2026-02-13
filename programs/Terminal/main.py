#!/usr/bin/env python3
# terminal shell for scutoidos

try:
    import scutoid
    HW = True
except ImportError:
    HW = False

import os

class Terminal:
    def __init__(self):
        self.buf = ""
        self.history = []
        self.running = True
        self.cwd = "/Users/Default"

    def prompt(self):
        if HW:
            scutoid.set_color(0x0A)
            scutoid.print(self.cwd + " ")
            scutoid.set_color(0x07)
            scutoid.print("$ ")
        else:
            print(f"{self.cwd} $ ", end='')

    def out(self, text):
        if HW:
            scutoid.set_color(0x07)
            scutoid.print(text)
        else:
            print(text, end='')

    def exec(self, raw):
        parts = raw.strip().split()
        if not parts: return

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "help":
            self.out("  help, clear, ls, cd, pwd, echo, uname, apps, exit\n")
        elif cmd in ("clear", "cls"):
            if HW: scutoid.clear()
            else: os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd == "ls":
            self.do_ls()
        elif cmd == "cd":
            self.do_cd(args)
        elif cmd == "pwd":
            self.out(self.cwd + "\n")
        elif cmd == "echo":
            self.out(' '.join(args) + "\n")
        elif cmd == "uname":
            self.out("ScutoidOS 0.1 (x86)\n")
        elif cmd == "apps":
            for a in ["TextEdit.sce", "Calculator.sce", "Terminal.sce"]:
                self.out(f"  {a}\n")
        elif cmd in ("exit", "quit"):
            self.running = False
        else:
            self.out(f"? {cmd}\n")

    def do_ls(self):
        if self.cwd == "/":
            items = ["Users/", "Apps/", "Other/", "programs/"]
        elif self.cwd == "/Apps":
            items = ["TextEdit.sce/", "Calculator.sce/", "Terminal.sce/"]
        elif "Users" in self.cwd:
            items = ["Documents/", "Downloads/", "Desktop/"]
        else:
            items = ["(empty)"]
        for i in items:
            self.out(f"{i}\n")

    def do_cd(self, args):
        if not args:
            self.cwd = "/Users/Default"
        elif args[0] == "..":
            if self.cwd != "/":
                self.cwd = '/'.join(self.cwd.rstrip('/').split('/')[:-1]) or '/'
        elif args[0] == "/":
            self.cwd = "/"
        elif args[0].startswith('/'):
            self.cwd = args[0]
        else:
            self.cwd = f"{self.cwd}/{args[0]}".replace('//', '/')

    def on_key(self, ch):
        if ch == '\n':
            if HW: scutoid.print("\n")
            else: print()
            if self.buf:
                self.history.append(self.buf)
                self.exec(self.buf)
                self.buf = ""
            if self.running:
                self.prompt()
        elif ch == '\b':
            if self.buf:
                self.buf = self.buf[:-1]
                if HW:
                    scutoid.print("\b \b")
        else:
            self.buf += ch
            if HW: scutoid.print(ch)
            else: print(ch, end='', flush=True)

    def run(self):
        if HW:
            scutoid.clear()
            scutoid.set_color(0x0B)
            scutoid.print("ScutoidOS Terminal\n")
            scutoid.set_color(0x07)
            scutoid.print("type 'help'\n\n")
        else:
            print("ScutoidOS Terminal (test mode)")
            print("type 'help'\n")

        self.prompt()

        if not HW:
            while self.running:
                try:
                    cmd = input()
                    self.exec(cmd)
                    if self.running: self.prompt()
                except (KeyboardInterrupt, EOFError):
                    break
        else:
            while self.running:
                if scutoid.keyboard_available():
                    sc = scutoid.keyboard_read()
                    if sc < 128:
                        ch = scutoid.scancode_to_ascii(sc)
                        if ch: self.on_key(ch)
                scutoid.halt()

def main():
    Terminal().run()

if __name__ == "__main__":
    main()

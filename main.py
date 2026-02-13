#!/usr/bin/env python3
# scutoidos main loop - runs after kernel hands off to micropython

import sys

try:
    import scutoid
except ImportError:
    print("no scutoid module, running in test mode")
    scutoid = None

class Shell:
    def __init__(self):
        self.running = True
        self.buf = ""

    def on_key(self, ch):
        if ch == '\n':
            self.dispatch(self.buf)
            self.buf = ""
            if scutoid:
                scutoid.print("> ")
        elif ch == '\b':
            if self.buf:
                self.buf = self.buf[:-1]
        else:
            self.buf += ch

    def dispatch(self, cmd):
        cmd = cmd.strip().lower()
        if not cmd:
            return

        if cmd == "help":
            self.show_help()
        elif cmd == "about":
            self.show_about()
        elif cmd == "mem":
            self.show_mem()
        elif cmd == "clear":
            if scutoid: scutoid.clear()
        elif cmd == "colors":
            self.show_colors()
        elif cmd.startswith("echo "):
            if scutoid:
                scutoid.print(cmd[5:] + "\n")
        elif cmd == "shutdown":
            if scutoid:
                scutoid.print("bye.\n")
            self.running = False
        else:
            if scutoid:
                scutoid.print(f"? {cmd}\n")

    def show_help(self):
        if not scutoid: return
        scutoid.set_color(0x0E)
        scutoid.print("commands:\n")
        scutoid.set_color(0x07)
        for line in [
            "  help      - this",
            "  about     - system info",
            "  mem       - memory",
            "  clear     - wipe screen",
            "  colors    - palette test",
            "  echo X    - print X",
            "  shutdown  - halt",
        ]:
            scutoid.print(line + "\n")

    def show_about(self):
        if not scutoid: return
        scutoid.set_color(0x0B)
        scutoid.print("ScutoidOS v0.1\n")
        scutoid.set_color(0x07)
        scutoid.print("python on bare metal, x86\n")

    def show_mem(self):
        if not scutoid: return
        sp = scutoid.get_stack_pointer()
        scutoid.print(f"stack:  0x{sp:08X}\n")
        scutoid.print(f"kernel: 0x00010000\n")
        scutoid.print(f"vga:    0x000B8000\n")

    def show_colors(self):
        if not scutoid: return
        names = [
            "black", "blue", "green", "cyan",
            "red", "magenta", "brown", "grey",
            "dk grey", "lt blue", "lt green", "lt cyan",
            "lt red", "lt magenta", "yellow", "white"
        ]
        for i, name in enumerate(names):
            scutoid.set_color(i)
            scutoid.print(f"  {name}\n")
        scutoid.set_color(0x07)

    def run(self):
        if scutoid:
            scutoid.clear()
            scutoid.set_color(0x0B)
            scutoid.print("ScutoidOS shell\n")
            scutoid.set_color(0x07)
            scutoid.print("type 'help'\n\n> ")
        
        while self.running:
            if scutoid:
                if scutoid.keyboard_available():
                    sc = scutoid.keyboard_read()
                    ch = scutoid.scancode_to_ascii(sc)
                    if ch:
                        self.on_key(ch)
                scutoid.halt()
            else:
                print("shell ready (test mode)")
                break

def main():
    sh = Shell()
    sh.run()

if __name__ == "__main__":
    main()

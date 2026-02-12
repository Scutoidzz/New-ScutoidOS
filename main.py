#!/usr/bin/env python3
# scutoidos main loop - runs after kernel hands off to micropython

import sys

try:
    import neonpulse
except ImportError:
    print("no neonpulse module, running in test mode")
    neonpulse = None

class Shell:
    def __init__(self):
        self.running = True
        self.buf = ""

    def on_key(self, ch):
        if ch == '\n':
            self.dispatch(self.buf)
            self.buf = ""
            if neonpulse:
                neonpulse.print("> ")
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
            if neonpulse: neonpulse.clear()
        elif cmd == "colors":
            self.show_colors()
        elif cmd.startswith("echo "):
            if neonpulse:
                neonpulse.print(cmd[5:] + "\n")
        elif cmd == "shutdown":
            if neonpulse:
                neonpulse.print("bye.\n")
            self.running = False
        else:
            if neonpulse:
                neonpulse.print(f"? {cmd}\n")

    def show_help(self):
        if not neonpulse: return
        neonpulse.set_color(0x0E)
        neonpulse.print("commands:\n")
        neonpulse.set_color(0x07)
        for line in [
            "  help      - this",
            "  about     - system info",
            "  mem       - memory",
            "  clear     - wipe screen",
            "  colors    - palette test",
            "  echo X    - print X",
            "  shutdown  - halt",
        ]:
            neonpulse.print(line + "\n")

    def show_about(self):
        if not neonpulse: return
        neonpulse.set_color(0x0B)
        neonpulse.print("ScutoidOS v0.1\n")
        neonpulse.set_color(0x07)
        neonpulse.print("python on bare metal, x86\n")

    def show_mem(self):
        if not neonpulse: return
        sp = neonpulse.get_stack_pointer()
        neonpulse.print(f"stack:  0x{sp:08X}\n")
        neonpulse.print(f"kernel: 0x00010000\n")
        neonpulse.print(f"vga:    0x000B8000\n")

    def show_colors(self):
        if not neonpulse: return
        names = [
            "black", "blue", "green", "cyan",
            "red", "magenta", "brown", "grey",
            "dk grey", "lt blue", "lt green", "lt cyan",
            "lt red", "lt magenta", "yellow", "white"
        ]
        for i, name in enumerate(names):
            neonpulse.set_color(i)
            neonpulse.print(f"  {name}\n")
        neonpulse.set_color(0x07)

    def run(self):
        if neonpulse:
            neonpulse.clear()
            neonpulse.set_color(0x0B)
            neonpulse.print("ScutoidOS shell\n")
            neonpulse.set_color(0x07)
            neonpulse.print("type 'help'\n\n> ")
        
        while self.running:
            if neonpulse:
                if neonpulse.keyboard_available():
                    sc = neonpulse.keyboard_read()
                    ch = neonpulse.scancode_to_ascii(sc)
                    if ch:
                        self.on_key(ch)
                neonpulse.halt()
            else:
                print("shell ready (test mode)")
                break

def main():
    sh = Shell()
    sh.run()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# simple text editor for scutoidos

try:
    import neonpulse
    HW = True
except ImportError:
    HW = False

class TextEdit:
    def __init__(self):
        self.lines = []
        self.cur = 0
        self.fname = "untitled.txt"

    def draw(self):
        if HW:
            neonpulse.clear()
            neonpulse.set_color(0x0E)
            neonpulse.print(f"textedit - {self.fname}\n")
            neonpulse.set_color(0x08)
            neonpulse.print("-" * 50 + "\n")
            neonpulse.set_color(0x07)
            for i, line in enumerate(self.lines):
                marker = "> " if i == self.cur else "  "
                neonpulse.print(f"{marker}{line}\n")
            neonpulse.set_color(0x08)
            neonpulse.print("-" * 50 + "\n")
            neonpulse.set_color(0x0B)
            neonpulse.print("ctrl+s save | ctrl+q quit\n")
        else:
            print(f"\n-- {self.fname} --")
            for i, line in enumerate(self.lines):
                marker = "> " if i == self.cur else "  "
                print(f"{marker}{line}")
            print("-" * 30)

    def insert(self, ch):
        if not self.lines:
            self.lines.append("")
        if ch == '\n':
            self.cur += 1
            self.lines.insert(self.cur, "")
        elif ch == '\b':
            if self.lines[self.cur]:
                self.lines[self.cur] = self.lines[self.cur][:-1]
        else:
            self.lines[self.cur] += ch

    def save(self):
        if HW:
            neonpulse.set_color(0x0A)
            neonpulse.print(f"saved {self.fname}\n")
        else:
            with open(self.fname, 'w') as f:
                f.write('\n'.join(self.lines))
            print(f"saved {self.fname}")

    def run(self):
        if not HW:
            self.lines = ["hello from scutoidos", "this is a text editor", ""]
            self.draw()
            return

        self.draw()
        while True:
            if neonpulse.keyboard_available():
                sc = neonpulse.keyboard_read()
                if sc == 0x1F:    # ctrl+s
                    self.save()
                elif sc == 0x10:  # ctrl+q
                    return
                else:
                    ch = neonpulse.scancode_to_ascii(sc)
                    if ch:
                        self.insert(ch)
                        self.draw()
            neonpulse.halt()

def main():
    TextEdit().run()

if __name__ == "__main__":
    main()

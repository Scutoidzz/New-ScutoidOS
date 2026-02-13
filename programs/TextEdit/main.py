#!/usr/bin/env python3
# simple text editor for scutoidos

try:
    import scutoid
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
            scutoid.clear()
            scutoid.set_color(0x0E)
            scutoid.print(f"textedit - {self.fname}\n")
            scutoid.set_color(0x08)
            scutoid.print("-" * 50 + "\n")
            scutoid.set_color(0x07)
            for i, line in enumerate(self.lines):
                marker = "> " if i == self.cur else "  "
                scutoid.print(f"{marker}{line}\n")
            scutoid.set_color(0x08)
            scutoid.print("-" * 50 + "\n")
            scutoid.set_color(0x0B)
            scutoid.print("ctrl+s save | ctrl+q quit\n")
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
            scutoid.set_color(0x0A)
            scutoid.print(f"saved {self.fname}\n")
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
            if scutoid.keyboard_available():
                sc = scutoid.keyboard_read()
                if sc == 0x1F:    # ctrl+s
                    self.save()
                elif sc == 0x10:  # ctrl+q
                    return
                else:
                    ch = scutoid.scancode_to_ascii(sc)
                    if ch:
                        self.insert(ch)
                        self.draw()
            scutoid.halt()

def main():
    TextEdit().run()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# calculator for scutoidos

try:
    import scutoid
    HW = True
except ImportError:
    HW = False

class Calc:
    def __init__(self):
        self.display = "0"
        self.op = None
        self.stored = 0
        self.fresh = True

    def draw(self):
        if HW:
            scutoid.clear()
            scutoid.set_color(0x0E)
            scutoid.print("calculator\n")
            scutoid.set_color(0x0F)
            scutoid.print(f"  {self.display}\n\n")
            scutoid.set_color(0x07)
            scutoid.print("7 8 9 /\n4 5 6 *\n1 2 3 -\n0 . = +\n")
            scutoid.set_color(0x08)
            scutoid.print("\nc=clear q=quit\n")
        else:
            print(f"\n[ {self.display} ]")
            print("7 8 9 / | 4 5 6 * | 1 2 3 - | 0 . = +")
            print("c=clear q=quit")

    def digit(self, d):
        if self.fresh:
            self.display = d
            self.fresh = False
        elif len(self.display) < 15:
            self.display = d if self.display == "0" else self.display + d

    def decimal(self):
        if '.' not in self.display:
            if self.fresh:
                self.display = "0."
                self.fresh = False
            else:
                self.display += "."

    def operate(self, new_op):
        try:
            cur = float(self.display)
            if self.op and not self.fresh:
                if self.op == '+': r = self.stored + cur
                elif self.op == '-': r = self.stored - cur
                elif self.op == '*': r = self.stored * cur
                elif self.op == '/':
                    if cur == 0:
                        self.display = "err"
                        self.fresh = True
                        self.op = None
                        return
                    r = self.stored / cur
                self.display = str(r)
                self.stored = r
            else:
                self.stored = cur
            self.op = new_op
            self.fresh = True
        except ValueError:
            self.display = "err"
            self.fresh = True

    def equals(self):
        if self.op:
            self.operate(None)
            self.op = None

    def clear(self):
        self.display = "0"
        self.op = None
        self.stored = 0
        self.fresh = True

    def handle(self, ch):
        if ch in '0123456789': self.digit(ch)
        elif ch == '.': self.decimal()
        elif ch in '+-*/': self.operate(ch)
        elif ch in ('=', '\n'): self.equals()
        elif ch in ('c', 'C'): self.clear()
        elif ch in ('q', 'Q'): return False
        return True

    def run(self):
        self.draw()
        if not HW:
            while True:
                try:
                    ch = input("> ").strip()
                    if ch and not self.handle(ch[0]):
                        break
                    self.draw()
                except KeyboardInterrupt:
                    break
            return

        while True:
            if scutoid.keyboard_available():
                sc = scutoid.keyboard_read()
                ch = scutoid.scancode_to_ascii(sc)
                if ch:
                    if not self.handle(ch):
                        return
                    self.draw()
            scutoid.halt()

def main():
    Calc().run()

if __name__ == "__main__":
    main()

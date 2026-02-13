# wanna build a scutoidos app?

# app dev guide (for ai or humans idc)
note: 3rd party devs only!!

## whats needed
- command name
- app name (styled)
- version number
- app type (use "application" for apps)
- main file (usually main.py)
- description
- author name (cant be scutoid/scutoidos related)
- category (cant be "system")
! has to be json

### example app.json
``` json 
{
    "name": "gator",
    "display_name": "Gator",
    "version": "1.2.1",
    "type": "application",
    "main": "main.py",
    "description": "simple golf game",
    "author": "arc games",
    "category": "games"
} 
```

versions follow semver.

## app code

apps are python (micropython). no pip packages.

every app needs a main() function:
```python
def main():
    # your code
    
if __name__ == "__main__":
    main()
```

## the scutoid api

### detecting hw vs test mode
```python
try:
    import scutoid
    HW = True
except ImportError:
    HW = False
```

use `HW` to branch between real hardware and local testing.

### display stuff

`scutoid.clear()` - clears screen

`scutoid.print(text)` - prints text. use \n for newlines

`scutoid.set_color(code)` - sets text color

colors:
- 0x07 = light grey (default)
- 0x08 = dark grey (borders)
- 0x0A = green (success)
- 0x0B = cyan (headers)
- 0x0C = red (errors)
- 0x0E = yellow (titles)
- 0x0F = white (important stuff)

### keyboard stuff

`scutoid.keyboard_available()` - returns true if key waiting

`scutoid.keyboard_read()` - gets scancode from buffer

special scancodes:
- 0x1F = ctrl+s
- 0x10 = ctrl+q
- below 128 = regular keys

`scutoid.scancode_to_ascii(code)` - converts scancode to char

common chars:
- '\n' = enter
- '\b' = backspace
- '0'-'9' = numbers
- 'a'-'z' = letters
- '+-*/' = operators

### system

`scutoid.halt()` - yields cpu. call this in your loop or you'll hog everything.

```python
while running:
    if scutoid.keyboard_available():
        # do stuff
        pass
    scutoid.halt()  # important
```

## basic app structure

```python
#!/usr/bin/env python3

try:
    import scutoid
    HW = True
except ImportError:
    HW = False

class App:
    def __init__(self):
        self.running = True
    
    def draw(self):
        if HW:
            scutoid.clear()
            scutoid.set_color(0x0E)
            scutoid.print("app name\n")
            scutoid.set_color(0x07)
            # render ui
        else:
            print("test mode")
    
    def handle(self, ch):
        if ch in ('q', 'Q'):
            return False
        return True
    
    def run(self):
        if not HW:
            self.draw()
            return
        
        self.draw()
        while self.running:
            if scutoid.keyboard_available():
                sc = scutoid.keyboard_read()
                ch = scutoid.scancode_to_ascii(sc)
                if ch:
                    if not self.handle(ch):
                        break
                    self.draw()
            scutoid.halt()

def main():
    App().run()

if __name__ == "__main__":
    main()
```

## testing

when HW=False:
- use print() not scutoid.print()
- use input() for keyboard
- handle ctrl+c gracefully

```python
def run(self):
    if not HW:
        while True:
            try:
                cmd = input("> ").strip()
                if cmd == 'q':
                    break
                self.process(cmd)
            except (KeyboardInterrupt, EOFError):
                break
        return
    
    # hw mode below
```

## tips

ui:
- clear before redraw
- yellow/cyan headers, white content, grey borders
- text only
- show which keys do what

performance:
- call scutoid.halt() in loops
- only redraw when needed
- batch prints

code:
- short names (draw, handle, exec)
- compact
- minimal comments
- class based

errors:
- catch exceptions
- show simple errors ("err")
- dont crash

keyboard:
- check availability first
- handle ctrl+q (quit) and ctrl+s (save)
- support upper and lower ('q' and 'Q')
- handle backspace

## patterns

input buffer:
```python
def on_key(self, ch):
    if ch == '\n':
        self.process(self.buf)
        self.buf = ""
    elif ch == '\b':
        if self.buf:
            self.buf = self.buf[:-1]
    else:
        self.buf += ch
```

state machine:
```python
self.state = "idle"
if self.state == "input":
    # input mode
elif self.state == "result":
    # result mode
```

borders:
```python
scutoid.set_color(0x08)
scutoid.print("=" * 50 + "\n")
```

## limits

cant do:
- pip packages
- filesystem on hw
- networking
- graphics beyond text
- mouse
- threading
- high precision floats

can do:
- text ui
- keyboard i/o
- colors
- state management
- strings
- math
- lists/dicts/sets
- file simulation in test mode

## examples

check out:
- calculator (programs/Calculator/) - math, input
- terminal (programs/Terminal/) - commands, dirs
- textedit (programs/TextEdit/) - line editing

## debugging

1. test with python3 first
2. use test mode
3. print debug stuff
4. print scancodes to see input
5. build ui first, features second

## publishing

1. make directory in programs/yourapp/
2. add app.json
3. add main.py
4. test both modes
5. category cant be "system"
6. author cant be scutoid/scutoidos

gl hf
#!/usr/bin/env python3
"""
TextEdit - Simple Text Editor for ScutoidOS
"""

try:
    import neonpulse
    HAS_NEONPULSE = True
except ImportError:
    HAS_NEONPULSE = False

class TextEdit:
    def __init__(self):
        self.buffer = []
        self.current_line = 0
        self.filename = "untitled.txt"
        
    def display(self):
        """Display the text buffer"""
        if HAS_NEONPULSE:
            neonpulse.clear()
            neonpulse.set_color(0x0E)  # Yellow
            neonpulse.print(f"TextEdit - {self.filename}\n")
            neonpulse.set_color(0x08)  # Dark grey
            neonpulse.print("=" * 60 + "\n")
            neonpulse.set_color(0x07)  # Light grey
            
            for i, line in enumerate(self.buffer):
                prefix = "> " if i == self.current_line else "  "
                neonpulse.print(f"{prefix}{line}\n")
            
            neonpulse.set_color(0x08)
            neonpulse.print("=" * 60 + "\n")
            neonpulse.set_color(0x0B)  # Cyan
            neonpulse.print("Ctrl+S: Save | Ctrl+Q: Quit\n")
        else:
            print(f"\n=== TextEdit - {self.filename} ===")
            for i, line in enumerate(self.buffer):
                prefix = "> " if i == self.current_line else "  "
                print(f"{prefix}{line}")
            print("=" * 40)
    
    def insert_char(self, char):
        """Insert character at current position"""
        if len(self.buffer) == 0:
            self.buffer.append("")
        
        if char == '\n':
            # New line
            self.current_line += 1
            self.buffer.insert(self.current_line, "")
        elif char == '\b':
            # Backspace
            if len(self.buffer[self.current_line]) > 0:
                self.buffer[self.current_line] = self.buffer[self.current_line][:-1]
        else:
            self.buffer[self.current_line] += char
    
    def save(self):
        """Save to file"""
        try:
            content = '\n'.join(self.buffer)
            # In real OS, would save to filesystem
            if HAS_NEONPULSE:
                neonpulse.set_color(0x0A)  # Green
                neonpulse.print(f"Saved to {self.filename}\n")
            else:
                print(f"Saved to {self.filename}")
                with open(self.filename, 'w') as f:
                    f.write(content)
        except Exception as e:
            if HAS_NEONPULSE:
                neonpulse.set_color(0x0C)  # Red
                neonpulse.print(f"Error saving: {e}\n")
            else:
                print(f"Error: {e}")
    
    def run(self):
        """Main editor loop"""
        if not HAS_NEONPULSE:
            print("TextEdit - Demo Mode")
            print("Running in test mode without hardware access")
            self.buffer = ["Hello, ScutoidOS!", "This is a text editor", ""]
            self.display()
            return
        
        self.display()
        
        while True:
            if neonpulse.keyboard_available():
                scancode = neonpulse.keyboard_read()
                
                # Check for special keys
                if scancode == 0x1F:  # Ctrl+S
                    self.save()
                elif scancode == 0x10:  # Ctrl+Q  
                    return
                else:
                    char = neonpulse.scancode_to_ascii(scancode)
                    if char:
                        self.insert_char(char)
                        self.display()
            
            neonpulse.halt()

def main():
    editor = TextEdit()
    editor.run()

if __name__ == "__main__":
    main()

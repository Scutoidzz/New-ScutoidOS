#!/usr/bin/env python3
"""
Calculator - Basic Calculator for ScutoidOS
"""

try:
    import neonpulse
    HAS_NEONPULSE = True
except ImportError:
    HAS_NEONPULSE = False

class Calculator:
    def __init__(self):
        self.display_text = "0"
        self.current_value = 0
        self.operation = None
        self.stored_value = 0
        self.new_number = True
        
    def display(self):
        """Show calculator interface"""
        if HAS_NEONPULSE:
            neonpulse.clear()
            neonpulse.set_color(0x0E)  # Yellow
            neonpulse.print("╔══════════════════════════════╗\n")
            neonpulse.print("║       CALCULATOR v1.0        ║\n")
            neonpulse.print("╠══════════════════════════════╣\n")
            
            # Display
            neonpulse.set_color(0x0F)  # White
            display_line = f"║ {self.display_text:>27} ║\n"
            neonpulse.print(display_line)
            
            neonpulse.set_color(0x0E)
            neonpulse.print("╠══════════════════════════════╣\n")
            
            # Buttons
            neonpulse.set_color(0x07)  # Light grey
            neonpulse.print("║  7    8    9    /            ║\n")
            neonpulse.print("║  4    5    6    *            ║\n")
            neonpulse.print("║  1    2    3    -            ║\n")
            neonpulse.print("║  0    .    =    +            ║\n")
            
            neonpulse.set_color(0x0E)
            neonpulse.print("╚══════════════════════════════╝\n")
            
            neonpulse.set_color(0x0B)  # Cyan
            neonpulse.print("\nType numbers and operators, Enter for =\n")
            neonpulse.print("Press 'c' to clear, 'q' to quit\n")
        else:
            print("\n" + "="*32)
            print(f"  CALCULATOR: {self.display_text}")
            print("="*32)
            print("7 8 9 /")
            print("4 5 6 *")
            print("1 2 3 -")
            print("0 . = +")
            print("c=clear, q=quit")
    
    def handle_digit(self, digit):
        """Handle number input"""
        if self.new_number:
            self.display_text = digit
            self.new_number = False
        else:
            if len(self.display_text) < 15:
                if self.display_text == "0":
                    self.display_text = digit
                else:
                    self.display_text += digit
    
    def handle_decimal(self):
        """Handle decimal point"""
        if '.' not in self.display_text:
            if self.new_number:
                self.display_text = "0."
                self.new_number = False
            else:
                self.display_text += "."
    
    def handle_operation(self, op):
        """Handle operator (+, -, *, /)"""
        try:
            current = float(self.display_text)
            
            if self.operation and not self.new_number:
                # Complete previous operation
                if self.operation == '+':
                    result = self.stored_value + current
                elif self.operation == '-':
                    result = self.stored_value - current
                elif self.operation == '*':
                    result = self.stored_value * current
                elif self.operation == '/':
                    if current != 0:
                        result = self.stored_value / current
                    else:
                        self.display_text = "Error: Div by 0"
                        self.new_number = True
                        self.operation = None
                        return
                
                self.display_text = str(result)
                self.stored_value = result
            else:
                self.stored_value = current
            
            self.operation = op
            self.new_number = True
            
        except ValueError:
            self.display_text = "Error"
            self.new_number = True
    
    def handle_equals(self):
        """Calculate result"""
        if self.operation:
            self.handle_operation(None)
            self.operation = None
    
    def handle_clear(self):
        """Clear calculator"""
        self.display_text = "0"
        self.current_value = 0
        self.operation = None
        self.stored_value = 0
        self.new_number = True
    
    def handle_input(self, char):
        """Process input character"""
        if char in '0123456789':
            self.handle_digit(char)
        elif char == '.':
            self.handle_decimal()
        elif char in '+-*/':
            self.handle_operation(char)
        elif char == '=' or char == '\n':
            self.handle_equals()
        elif char == 'c' or char == 'C':
            self.handle_clear()
        elif char == 'q' or char == 'Q':
            return False
        
        return True
    
    def run(self):
        """Main calculator loop"""
        if not HAS_NEONPULSE:
            print("Calculator - Demo Mode")
            self.display()
            
            while True:
                try:
                    char = input("> ").strip()
                    if char:
                        if not self.handle_input(char[0]):
                            break
                        self.display()
                except KeyboardInterrupt:
                    break
            return
        
        self.display()
        
        while True:
            if neonpulse.keyboard_available():
                scancode = neonpulse.keyboard_read()
                char = neonpulse.scancode_to_ascii(scancode)
                
                if char:
                    if not self.handle_input(char):
                        return
                    self.display()
            
            neonpulse.halt()

def main():
    calc = Calculator()
    calc.run()

if __name__ == "__main__":
    main()

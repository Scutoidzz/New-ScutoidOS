/*
 * minimal test kernel - just print and halt
 */

#define VGA_MEMORY 0xB8000

__attribute__((section(".text.entry")))
void kernel_main(void) {
    unsigned short *vga = (unsigned short*)0xB8000;
    
    // write "HELLO" in white on black
    vga[0] = 0x0F48;  // H
    vga[1] = 0x0F45;  // E
    vga[2] = 0x0F4C;  // L
    vga[3] = 0x0F4C;  // L
    vga[4] = 0x0F4F;  // O
    
    // halt forever
    while(1) {
        __asm__ volatile("hlt");
    }
}

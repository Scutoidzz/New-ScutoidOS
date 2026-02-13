#ifndef IDT_H
#define IDT_H

/*
 * IDT configuration (must match bootloader.asm)
 *   IDT base: 0xA000
 *   256 entries, 8 bytes each
 *   Keyboard IRQ1 -> interrupt 0x21
 *   PIC1 remapped to 0x20-0x27
 *   PIC2 remapped to 0x28-0x2F
 */
#define IDT_BASE     0xA000
#define IDT_ENTRIES  256
#define IRQ_TIMER    0x20
#define IRQ_KEYBOARD 0x21

#endif

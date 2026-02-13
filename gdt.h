#ifndef GDT_H
#define GDT_H

/*
 * GDT segment selectors (must match bootloader.asm)
 *   0x00 = Null descriptor
 *   0x08 = Code segment (Ring 0, executable, readable, 4GB flat)
 *   0x10 = Data segment (Ring 0, writable, 4GB flat)
 */
#define GDT_NULL_SEG 0x00
#define GDT_CODE_SEG 0x08
#define GDT_DATA_SEG 0x10

#endif

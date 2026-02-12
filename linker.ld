/* linker script for ScutoidOS kernel */

ENTRY(kernel_main)

SECTIONS
{
    . = 0x10000;
    
    .text : {
        *(.text.entry)
        *(.text)
        *(.text.*)
    }
    
    .rodata : {
        *(.rodata)
        *(.rodata.*)
    }
    
    .data : {
        *(.data)
    }
    
    .bss : {
        *(.bss)
        *(COMMON)
    }
}

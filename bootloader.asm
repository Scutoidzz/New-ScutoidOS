; ============================================================================
; NEON-PULSE OS BOOTLOADER
; ============================================================================
; A complete bootloader that:
; 1. Sets up a 16KB stack
; 2. Configures GDT for protected mode
; 3. Loads kernel from disk
; 4. Sets up keyboard interrupt handler with shared buffer
; 5. Jumps to C/MicroPython kernel
; ============================================================================

[BITS 16]
[ORG 0x7C00]

; Entry point - BIOS loads us here
start:
    ; Clear interrupts during setup
    cli
    
    ; Set up segments for real mode
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    
    ; Set up initial stack (we'll move it later in protected mode)
    mov sp, 0x7C00
    
    ; Re-enable interrupts
    sti
    
    ; Print boot message
    mov si, boot_msg
    call print_string
    
    ; Load kernel from disk
    call load_kernel
    
    ; Enter protected mode
    call enter_protected_mode
    
    ; We should never return here
    jmp $

; ============================================================================
; PRINT STRING (Real Mode)
; Input: SI = pointer to null-terminated string
; ============================================================================
print_string:
    pusha
.loop:
    lodsb                   ; Load byte from SI into AL
    or al, al               ; Check if null terminator
    jz .done
    mov ah, 0x0E            ; BIOS teletype function
    mov bh, 0x00            ; Page number
    mov bl, 0x07            ; Text attribute
    int 0x10                ; BIOS video interrupt
    jmp .loop
.done:
    popa
    ret

; ============================================================================
; LOAD KERNEL FROM DISK
; Loads sectors 2-20 (kernel binary) to 0x10000
; ============================================================================
load_kernel:
    pusha
    
    mov si, loading_msg
    call print_string
    
    ; Reset disk system
    mov ah, 0x00
    mov dl, 0x80            ; First hard disk
    int 0x13
    jc disk_error
    
    ; Read kernel sectors
    ; AH = 0x02 (read sectors)
    ; AL = number of sectors to read (18 sectors = ~9KB)
    ; CH = cylinder number (0)
    ; CL = sector number (2, first sector after bootloader)
    ; DH = head number (0)
    ; DL = drive number (0x80)
    ; ES:BX = buffer address (0x1000:0x0000 = 0x10000)
    
    mov ax, 0x1000
    mov es, ax
    xor bx, bx              ; ES:BX = 0x1000:0x0000
    
    mov ah, 0x02            ; Read sectors function
    mov al, 18              ; Number of sectors
    mov ch, 0               ; Cylinder 0
    mov cl, 2               ; Start from sector 2
    mov dh, 0               ; Head 0
    mov dl, 0x80            ; First hard disk
    int 0x13
    jc disk_error
    
    mov si, loaded_msg
    call print_string
    
    popa
    ret

disk_error:
    mov si, disk_error_msg
    call print_string
    jmp $

; ============================================================================
; ENTER PROTECTED MODE
; ============================================================================
enter_protected_mode:
    cli                     ; Disable interrupts
    
    ; Load GDT
    lgdt [gdt_descriptor]
    
    ; Enable protected mode by setting PE bit in CR0
    mov eax, cr0
    or eax, 1
    mov cr0, eax
    
    ; Far jump to flush pipeline and load CS with 32-bit code segment
    jmp CODE_SEG:protected_mode_start

; ============================================================================
; GDT (Global Descriptor Table)
; ============================================================================
gdt_start:
    ; Null descriptor (required)
    dq 0x0000000000000000

gdt_code:
    ; Code segment descriptor
    ; Base = 0x0, Limit = 0xFFFFF
    ; Present, Ring 0, Code segment, Executable, Readable
    ; Granularity = 4KB, 32-bit
    dw 0xFFFF               ; Limit (bits 0-15)
    dw 0x0000               ; Base (bits 0-15)
    db 0x00                 ; Base (bits 16-23)
    db 10011010b            ; Access byte: Present, Ring 0, Code, Executable, Readable
    db 11001111b            ; Flags + Limit (bits 16-19)
    db 0x00                 ; Base (bits 24-31)

gdt_data:
    ; Data segment descriptor
    ; Base = 0x0, Limit = 0xFFFFF
    ; Present, Ring 0, Data segment, Writable
    ; Granularity = 4KB, 32-bit
    dw 0xFFFF               ; Limit (bits 0-15)
    dw 0x0000               ; Base (bits 0-15)
    db 0x00                 ; Base (bits 16-23)
    db 10010010b            ; Access byte: Present, Ring 0, Data, Writable
    db 11001111b            ; Flags + Limit (bits 16-19)
    db 0x00                 ; Base (bits 24-31)

gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1  ; Size of GDT
    dd gdt_start                 ; Address of GDT

; GDT segment selectors
CODE_SEG equ gdt_code - gdt_start
DATA_SEG equ gdt_data - gdt_start

; ============================================================================
; 32-BIT PROTECTED MODE CODE
; ============================================================================
[BITS 32]

protected_mode_start:
    ; Set up data segments
    mov ax, DATA_SEG
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    
    ; ========================================================================
    ; GOTCHA #1: SET UP 16KB STACK
    ; ========================================================================
    ; Stack grows downward, so we set ESP to the end of our stack space
    ; Stack location: 0x90000 - 16KB = 0x8C000 to 0x90000
    mov esp, 0x90000
    
    ; Clear the stack area (optional but good practice)
    mov edi, 0x8C000
    mov ecx, 4096           ; 16KB / 4 bytes = 4096 dwords
    xor eax, eax
    rep stosd
    
    ; ========================================================================
    ; GOTCHA #3: SET UP KEYBOARD INTERRUPT HANDLER & SHARED BUFFER
    ; ========================================================================
    
    ; Initialize the shared keyboard buffer at 0x9000
    ; Buffer structure:
    ; [0x9000] = write index (1 byte)
    ; [0x9001] = read index (1 byte)
    ; [0x9002-0x9101] = circular buffer (256 bytes)
    
    mov byte [0x9000], 0    ; Write index = 0
    mov byte [0x9001], 0    ; Read index = 0
    
    ; Remap PIC (Programmable Interrupt Controller)
    ; By default, IRQ0-7 map to interrupts 0x08-0x0F (conflicts with CPU exceptions)
    ; We remap: IRQ0-7 -> 0x20-0x27, IRQ8-15 -> 0x28-0x2F
    
    ; Remap PIC1 (Master)
    mov al, 0x11            ; ICW1: Initialize + ICW4 needed
    out 0x20, al
    out 0x80, al            ; IO delay
    mov al, 0x20            ; ICW2: PIC1 offset to 0x20
    out 0x21, al
    out 0x80, al
    mov al, 0x04            ; ICW3: IRQ2 connects to PIC2
    out 0x21, al
    out 0x80, al
    mov al, 0x01            ; ICW4: 8086 mode
    out 0x21, al
    out 0x80, al
    
    ; Remap PIC2 (Slave)
    mov al, 0x11
    out 0xA0, al
    out 0x80, al
    mov al, 0x28            ; ICW2: PIC2 offset to 0x28
    out 0xA1, al
    out 0x80, al
    mov al, 0x02            ; ICW3: Connect to IRQ2 of PIC1
    out 0xA1, al
    out 0x80, al
    mov al, 0x01
    out 0xA1, al
    out 0x80, al
    
    ; Set PIC masks: enable only IRQ1 (keyboard) on PIC1, mask all on PIC2
    mov al, 0xFD            ; Bit 1 clear = IRQ1 (keyboard) enabled, all others masked
    out 0x21, al
    mov al, 0xFF            ; Mask all IRQ8-15
    out 0xA1, al
    
    ; Set up IDT (Interrupt Descriptor Table)
    call setup_idt
    
    lidt [idt_descriptor]
    sti
    ; JUMP TO KERNEL
    ; ========================================================================
    ; Kernel is loaded at 0x10000
    ; Call it as a function
    call 0x10000
    
    ; If kernel returns, halt
    jmp halt

default_idt_handler:
    iret
error_code_idt_handler:
    add esp, 4
    iret
setup_idt:
    mov edi, IDT_BASE
    xor ecx, ecx
    mov ebx, 0x3E00             ; bits 8,10,11,12,13,14,17 = error-code exceptions
.setup_loop:
    mov eax, default_idt_handler
    bt ebx, ecx
    jc .err
    jmp .write
.err:
    mov eax, error_code_idt_handler
.write:
    mov word [edi], ax
    mov word [edi + 2], CODE_SEG
    mov byte [edi + 4], 0
    mov byte [edi + 5], 0x8E
    shr eax, 16
    mov word [edi + 6], ax
    add edi, 8
    inc ecx
    cmp ecx, 256
    jb .setup_loop
    mov edi, IDT_BASE + (0x21 * 8)
    mov eax, keyboard_interrupt_handler
    mov word [edi], ax
    mov word [edi + 2], CODE_SEG
    mov byte [edi + 4], 0
    mov byte [edi + 5], 0x8E
    shr eax, 16
    mov word [edi + 6], ax

    ret

; ============================================================================
; KEYBOARD INTERRUPT HANDLER
; ============================================================================
keyboard_interrupt_handler:
    pushad                  ; Save all registers
    
    ; Read scancode from keyboard
    in al, 0x60
    
    ; Get write index
    movzx ebx, byte [0x9000]
    
    ; Write scancode to buffer
    mov byte [0x9002 + ebx], al
    
    ; Increment write index (wrap around at 256)
    inc bl
    mov byte [0x9000], bl
    
    ; Send EOI (End of Interrupt) to PIC
    mov al, 0x20
    out 0x20, al
    
    popad                   ; Restore all registers
    iret                    ; Return from interrupt

; ============================================================================
; PRINT STRING (Protected Mode)
; Input: ESI = pointer to null-terminated string
; ============================================================================
print_string_pm:
    pushad
    mov edi, 0xB8000        ; VGA text mode buffer
    mov ah, 0x0F            ; White on black
.loop:
    lodsb
    or al, al
    jz .done
    stosw                   ; Write character + attribute
    jmp .loop
.done:
    popad
    ret

; ============================================================================
; HALT SYSTEM
; ============================================================================
halt:
    cli
    hlt
    jmp halt

; ============================================================================
; IDT BASE ADDRESS
; ============================================================================
IDT_BASE equ 0xA000

idt_descriptor:
    dw 256 * 8 - 1          ; Size of IDT (256 entries * 8 bytes)
    dd IDT_BASE             ; Address of IDT

boot_msg:       db 'Boot...', 0x0D, 0x0A, 0
loading_msg:    db 'load...', 0x0D, 0x0A, 0
loaded_msg:     db 'ok', 0x0D, 0x0A, 0
disk_error_msg: db 'DISK ERR', 0x0D, 0x0A, 0

; ============================================================================
; BOOT SIGNATURE
; Pad to 510 bytes and add boot signature (0xAA55)
; ============================================================================
times 510-($-$$) db 0
dw 0xAA55

; ============================================================================
; KERNEL SPACE (this is where your kernel binary will be appended)
; ============================================================================
; The Python stitching script will append the kernel binary after this point

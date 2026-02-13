// ============================================================================
// NEON-PULSE OS KERNEL WITH MICROPYTHON
// This is the next evolution - integrates MicroPython interpreter
// ============================================================================

#include "py/compile.h"
#include "py/runtime.h"
#include "py/repl.h"
#include "py/gc.h"
#include "py/mperrno.h"

// VGA text mode buffer
#define VGA_MEMORY 0xB8000
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

// Shared keyboard buffer (set up by bootloader)
#define KEYBOARD_BUFFER_WRITE_INDEX ((volatile unsigned char*)0x9000)
#define KEYBOARD_BUFFER_READ_INDEX  ((volatile unsigned char*)0x9001)
#define KEYBOARD_BUFFER             ((volatile unsigned char*)0x9002)

// Colors
#define COLOR_BLACK         0x0
#define COLOR_WHITE         0xF
#define COLOR_LIGHT_CYAN    0xB
#define COLOR_YELLOW        0xE

static int cursor_x = 0;
static int cursor_y = 0;
static unsigned char current_color = (COLOR_BLACK << 4) | COLOR_LIGHT_CYAN;

// ============================================================================
// VGA Functions (same as before)
// ============================================================================

void clear_screen(void) {
    unsigned short* vga = (unsigned short*)VGA_MEMORY;
    unsigned short blank = (current_color << 8) | ' ';
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga[i] = blank;
    }
    cursor_x = 0;
    cursor_y = 0;
}

void scroll_screen(void) {
    unsigned short* vga = (unsigned short*)VGA_MEMORY;
    unsigned short blank = (current_color << 8) | ' ';
    for (int i = 0; i < (VGA_HEIGHT - 1) * VGA_WIDTH; i++) {
        vga[i] = vga[i + VGA_WIDTH];
    }
    for (int i = (VGA_HEIGHT - 1) * VGA_WIDTH; i < VGA_HEIGHT * VGA_WIDTH; i++) {
        vga[i] = blank;
    }
    cursor_y = VGA_HEIGHT - 1;
}

void putchar(char c) {
    unsigned short* vga = (unsigned short*)VGA_MEMORY;
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else if (c == '\r') {
        cursor_x = 0;
    } else {
        vga[cursor_y * VGA_WIDTH + cursor_x] = (current_color << 8) | c;
        cursor_x++;
    }
    if (cursor_x >= VGA_WIDTH) {
        cursor_x = 0;
        cursor_y++;
    }
    if (cursor_y >= VGA_HEIGHT) {
        scroll_screen();
    }
}

void print(const char* str) {
    for (int i = 0; str[i] != '\0'; i++) {
        putchar(str[i]);
    }
}

void set_color(unsigned char color) {
    current_color = color;
}

// ============================================================================
// Python Module: "scutoid" - Hardware interface exposed to Python
// ============================================================================

// scutoid.print(str)
STATIC mp_obj_t scutoid_print(mp_obj_t str_obj) {
    const char *str = mp_obj_str_get_str(str_obj);
    print(str);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(scutoid_print_obj, scutoid_print);

// scutoid.clear()
STATIC mp_obj_t scutoid_clear(void) {
    clear_screen();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(scutoid_clear_obj, scutoid_clear);

// scutoid.set_color(color)
STATIC mp_obj_t scutoid_set_color(mp_obj_t color_obj) {
    unsigned char color = mp_obj_get_int(color_obj);
    set_color(color);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(scutoid_set_color_obj, scutoid_set_color);

// scutoid.keyboard_available()
STATIC mp_obj_t scutoid_keyboard_available(void) {
    unsigned char write_idx = *KEYBOARD_BUFFER_WRITE_INDEX;
    unsigned char read_idx = *KEYBOARD_BUFFER_READ_INDEX;
    return mp_obj_new_bool(write_idx != read_idx);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(scutoid_keyboard_available_obj, scutoid_keyboard_available);

// scutoid.keyboard_read()
STATIC mp_obj_t scutoid_keyboard_read(void) {
    unsigned char read_idx = *KEYBOARD_BUFFER_READ_INDEX;
    unsigned char scancode = KEYBOARD_BUFFER[read_idx];
    *KEYBOARD_BUFFER_READ_INDEX = read_idx + 1;
    return mp_obj_new_int(scancode);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(scutoid_keyboard_read_obj, scutoid_keyboard_read);

// scutoid.scancode_to_ascii(scancode)
STATIC mp_obj_t scutoid_scancode_to_ascii(mp_obj_t scancode_obj) {
    static const char scancode_table[] = {
        0, 0, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
        '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
        0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',
        0, '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0,
        '*', 0, ' '
    };
    
    unsigned char scancode = mp_obj_get_int(scancode_obj);
    if (scancode < sizeof(scancode_table) && scancode_table[scancode]) {
        char str[2] = {scancode_table[scancode], 0};
        return mp_obj_new_str(str, 1);
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(scutoid_scancode_to_ascii_obj, scutoid_scancode_to_ascii);

// scutoid.halt()
STATIC mp_obj_t scutoid_halt(void) {
    __asm__ volatile("hlt");
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(scutoid_halt_obj, scutoid_halt);

// scutoid.get_stack_pointer()
STATIC mp_obj_t scutoid_get_stack_pointer(void) {
    unsigned int esp;
    __asm__ volatile("mov %%esp, %0" : "=r"(esp));
    return mp_obj_new_int(esp);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(scutoid_get_stack_pointer_obj, scutoid_get_stack_pointer);

// Define module
STATIC const mp_rom_map_elem_t scutoid_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_scutoid) },
    { MP_ROM_QSTR(MP_QSTR_print), MP_ROM_PTR(&scutoid_print_obj) },
    { MP_ROM_QSTR(MP_QSTR_clear), MP_ROM_PTR(&scutoid_clear_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_color), MP_ROM_PTR(&scutoid_set_color_obj) },
    { MP_ROM_QSTR(MP_QSTR_keyboard_available), MP_ROM_PTR(&scutoid_keyboard_available_obj) },
    { MP_ROM_QSTR(MP_QSTR_keyboard_read), MP_ROM_PTR(&scutoid_keyboard_read_obj) },
    { MP_ROM_QSTR(MP_QSTR_scancode_to_ascii), MP_ROM_PTR(&scutoid_scancode_to_ascii_obj) },
    { MP_ROM_QSTR(MP_QSTR_halt), MP_ROM_PTR(&scutoid_halt_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_stack_pointer), MP_ROM_PTR(&scutoid_get_stack_pointer_obj) },
};
STATIC MP_DEFINE_CONST_DICT(scutoid_module_globals, scutoid_module_globals_table);

const mp_obj_module_t scutoid_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&scutoid_module_globals,
};

// Register module
MP_REGISTER_MODULE(MP_QSTR_scutoid, scutoid_module);

// ============================================================================
// MicroPython Setup
// ============================================================================

// Allocate memory for Python heap
static char heap[16384];  // 16KB heap for Python objects

void mp_init(void) {
    // Initialize MicroPython
    mp_init();
    
    // Set up heap for garbage collector
    gc_init(heap, heap + sizeof(heap));
    
    // Initialize modules
    mp_obj_list_init(mp_sys_path, 0);
    mp_obj_list_init(mp_sys_argv, 0);
}

// ============================================================================
// Error Handling
// ============================================================================

void nlr_jump_fail(void *val) {
    print("\n*** FATAL: Uncaught Python exception ***\n");
    while (1) {
        __asm__ volatile("hlt");
    }
}

// MicroPython needs this
void __assert_func(const char *file, int line, const char *func, const char *expr) {
    print("\n*** ASSERTION FAILED ***\n");
    print(file);
    print("\n");
    while (1) {
        __asm__ volatile("hlt");
    }
}

// ============================================================================
// Main Kernel Entry Point
// ============================================================================

// This would be your frozen main.py compiled to bytecode
// For now, we'll use a simple inline Python string
const char *python_main = 
"print('Python kernel starting...')\n"
"import scutoid\n"
"scutoid.clear()\n"
"scutoid.set_color(0x0E)\n"
"scutoid.print('PYTHON IS RUNNING!\\n')\n"
"scutoid.set_color(0x07)\n"
"while True:\n"
"    if scutoid.keyboard_available():\n"
"        sc = scutoid.keyboard_read()\n"
"        if sc < 128:\n"  // Make code only
"            ch = scutoid.scancode_to_ascii(sc)\n"
"            if ch:\n"
"                scutoid.print(ch)\n"
"    scutoid.halt()\n";

void kernel_main(void) {
    // Hardware initialization
    clear_screen();
    current_color = (COLOR_BLACK << 4) | COLOR_YELLOW;
    print("Initializing MicroPython...\n");
    
    // Initialize MicroPython
    mp_init();
    
    current_color = (COLOR_BLACK << 4) | COLOR_LIGHT_CYAN;
    print("Executing Python code...\n\n");
    
    // Execute Python code
    mp_lexer_t *lex = mp_lexer_new_from_str_len(MP_QSTR__lt_stdin_gt_, 
                                                  python_main, 
                                                  strlen(python_main), 
                                                  false);
    
    mp_parse_tree_t parse_tree = mp_parse(lex, MP_PARSE_FILE_INPUT);
    mp_obj_t module_fun = mp_compile(&parse_tree, lex->source_name, true);
    
    // Run the Python code
    mp_call_function_0(module_fun);
    
    // Should never reach here if Python runs forever
    print("\nPython exited\n");
    while (1) {
        __asm__ volatile("hlt");
    }
}

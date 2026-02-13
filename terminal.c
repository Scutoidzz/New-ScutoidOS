#include "terminal.h"
#include "interrupt.h"

#define VGA_MEMORY 0xB8000
#define KB_BUFFER_ADDR ((volatile terminal_buffer_t*)0x9000)

volatile terminal_buffer_t* kb_buffer = KB_BUFFER_ADDR;

static int cursor_x = 0;
static int cursor_y = 0;
static unsigned char current_color = 0x07;

static void outb(unsigned short port, unsigned char value) {
    __asm__ volatile("outb %b0, %w1" : : "a"(value), "Nd"(port));
}

static void update_cursor(void) {
    unsigned int pos = cursor_y * TERMINAL_WIDTH + cursor_x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (unsigned char)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (unsigned char)((pos >> 8) & 0xFF));
}

void terminal_init(void) {
    cursor_x = 0;
    cursor_y = 0;
    current_color = 0x07;
}

int terminal_has_input(void) {
    return kb_buffer->write_idx != kb_buffer->read_idx;
}

unsigned char terminal_read_char(void) {
    unsigned char idx = kb_buffer->read_idx;
    unsigned char ch = kb_buffer->buffer[idx];
    kb_buffer->read_idx = idx + 1;
    return ch;
}

void terminal_write_char(char c) {
    volatile unsigned short *vga = (volatile unsigned short*)VGA_MEMORY;

    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else if (c == '\r') {
        cursor_x = 0;
    } else if (c == '\t') {
        cursor_x = (cursor_x + 4) & ~3;
    } else if (c == '\b') {
        if (cursor_x > 0) {
            cursor_x--;
            vga[cursor_y * TERMINAL_WIDTH + cursor_x] = (current_color << 8) | ' ';
        }
    } else {
        vga[cursor_y * TERMINAL_WIDTH + cursor_x] = (current_color << 8) | c;
        cursor_x++;
    }

    if (cursor_x >= TERMINAL_WIDTH) {
        cursor_x = 0;
        cursor_y++;
    }
    if (cursor_y >= TERMINAL_HEIGHT) {
        terminal_scroll();
    }

    update_cursor();
}

void terminal_write_string(const char *s) {
    while (*s) {
        terminal_write_char(*s++);
    }
}

void terminal_clear(void) {
    volatile unsigned short *vga = (volatile unsigned short*)VGA_MEMORY;
    unsigned short blank = (current_color << 8) | ' ';

    for (int i = 0; i < TERMINAL_WIDTH * TERMINAL_HEIGHT; i++) {
        vga[i] = blank;
    }

    cursor_x = 0;
    cursor_y = 0;
    update_cursor();
}

void terminal_set_color(unsigned char color) {
    current_color = color;
}

void terminal_scroll(void) {
    volatile unsigned short *vga = (volatile unsigned short*)VGA_MEMORY;
    unsigned short blank = (current_color << 8) | ' ';

    for (int i = 0; i < (TERMINAL_HEIGHT - 1) * TERMINAL_WIDTH; i++) {
        vga[i] = vga[i + TERMINAL_WIDTH];
    }

    for (int i = (TERMINAL_HEIGHT - 1) * TERMINAL_WIDTH; i < TERMINAL_HEIGHT * TERMINAL_WIDTH; i++) {
        vga[i] = blank;
    }

    cursor_y = TERMINAL_HEIGHT - 1;
    update_cursor();
}

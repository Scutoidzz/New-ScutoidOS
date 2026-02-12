/*
 * ScutoidOS kernel
 * boots to a command shell on VGA text mode
 *
 * kernel_main MUST be first so it sits at 0x10000
 * where the bootloader jumps to
 */

#define VGA_MEMORY 0xB8000
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

#define KB_WRITE_IDX ((volatile unsigned char*)0x9000)
#define KB_READ_IDX  ((volatile unsigned char*)0x9001)
#define KB_BUFFER    ((volatile unsigned char*)0x9002)

static int cx = 0;
static int cy = 0;
static unsigned char color = 0x07;

// forward declarations
static void outb(unsigned short port, unsigned char value);
static void update_cursor(void);
void clear_screen(void);
void scroll(void);
void putchar(char c);
void kprint(const char *s);
void print_hex(unsigned int val);
int kb_available(void);
unsigned char kb_read(void);
char sc_to_ascii(unsigned char sc);
void prompt(void);
void cmd_help(void);
void cmd_about(void);
void cmd_mem(void);
void cmd_colors(void);
void run_command(void);

#define CMD_MAX 256
static char cmdbuf[CMD_MAX];
static int cmdlen = 0;

// -- entry point (MUST be first function) --

__attribute__((section(".text.entry")))
void kernel_main(void) {
    clear_screen();

    color = 0x0B;
    kprint("ScutoidOS v0.1\n");
    color = 0x07;

    kprint("kernel @ "); print_hex(0x10000); kprint("\n");
    unsigned int esp;
    __asm__ volatile("mov %%esp, %0" : "=r"(esp));
    kprint("stack  @ "); print_hex(esp); kprint("\n");
    kprint("type 'help' for commands\n\n");

    prompt();

    while (1) {
        if (kb_available()) {
            unsigned char sc = kb_read();

            if (sc & 0x80) goto next;

            char ch = sc_to_ascii(sc);
            if (!ch) goto next;

            if (ch == '\n') {
                kprint("\n");
                run_command();
                cmdlen = 0;
                prompt();
            } else if (ch == '\b') {
                if (cmdlen > 0) {
                    cmdlen--;
                    putchar('\b');
                }
            } else {
                if (cmdlen < CMD_MAX - 1) {
                    cmdbuf[cmdlen++] = ch;
                    putchar(ch);
                }
            }
        }
next:
        __asm__ volatile("hlt");
    }
}

// -- display: VGA hardware cursor (so blinking cursor aligns with > prompt) --

static void outb(unsigned short port, unsigned char value) {
    __asm__ volatile("outb %b0, %w1" : : "a"(value), "Nd"(port));
}

static void update_cursor(void) {
    unsigned int pos = cy * VGA_WIDTH + cx;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (unsigned char)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (unsigned char)((pos >> 8) & 0xFF));
}

void clear_screen(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    unsigned short blank = (color << 8) | ' ';
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++)
        vga[i] = blank;
    cx = 0;
    cy = 0;
    update_cursor();
}

void scroll(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    unsigned short blank = (color << 8) | ' ';
    for (int i = 0; i < (VGA_HEIGHT - 1) * VGA_WIDTH; i++)
        vga[i] = vga[i + VGA_WIDTH];
    for (int i = (VGA_HEIGHT - 1) * VGA_WIDTH; i < VGA_HEIGHT * VGA_WIDTH; i++)
        vga[i] = blank;
    cy = VGA_HEIGHT - 1;
    update_cursor();
}

void putchar(char c) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    if (c == '\n') {
        cx = 0;
        cy++;
    } else if (c == '\r') {
        cx = 0;
    } else if (c == '\t') {
        cx = (cx + 4) & ~3;
    } else if (c == '\b') {
        if (cx > 0) {
            cx--;
            vga[cy * VGA_WIDTH + cx] = (color << 8) | ' ';
        }
    } else {
        vga[cy * VGA_WIDTH + cx] = (color << 8) | c;
        cx++;
    }
    if (cx >= VGA_WIDTH) { cx = 0; cy++; }
    if (cy >= VGA_HEIGHT) scroll();
    update_cursor();
}

void kprint(const char *s) {
    while (*s) putchar(*s++);
}

void print_hex(unsigned int val) {
    char hex[] = "0123456789ABCDEF";
    kprint("0x");
    for (int i = 28; i >= 0; i -= 4)
        putchar(hex[(val >> i) & 0xF]);
}

// -- keyboard --

int kb_available(void) {
    return *KB_WRITE_IDX != *KB_READ_IDX;
}

unsigned char kb_read(void) {
    unsigned char idx = *KB_READ_IDX;
    unsigned char sc = KB_BUFFER[idx];
    *KB_READ_IDX = idx + 1;
    return sc;
}

char sc_to_ascii(unsigned char sc) {
    static const char table[] = {
        0, 0, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
        '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
        0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',
        0, '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0,
        '*', 0, ' '
    };
    if (sc < sizeof(table)) return table[sc];
    return 0;
}

// -- string helpers --

int kstrcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return *a - *b;
}

int kstrncmp(const char *a, const char *b, int n) {
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) return a[i] - b[i];
        if (!a[i]) return 0;
    }
    return 0;
}

// -- shell commands --

void prompt(void) {
    unsigned char old = color;
    color = 0x0A;
    kprint("scutoidos");
    color = 0x07;
    kprint("> ");
    color = old;
    update_cursor();
}

void cmd_help(void) {
    kprint("commands:\n");
    kprint("  help      show this\n");
    kprint("  about     system info\n");
    kprint("  mem       memory layout\n");
    kprint("  clear     clear screen\n");
    kprint("  colors    color test\n");
    kprint("  echo ...  print text\n");
    kprint("  reboot    restart\n");
}

void cmd_about(void) {
    color = 0x0E;
    kprint("ScutoidOS v0.1\n");
    color = 0x07;
    kprint("x86 kernel, hand-rolled from scratch\n");
    kprint("bootloader -> protected mode -> this shell\n");
}

void cmd_mem(void) {
    unsigned int esp;
    __asm__ volatile("mov %%esp, %0" : "=r"(esp));
    kprint("stack:    "); print_hex(esp); kprint("\n");
    kprint("kernel:   "); print_hex(0x10000); kprint("\n");
    kprint("vga:      "); print_hex(0xB8000); kprint("\n");
    kprint("kb buf:   "); print_hex(0x9000); kprint("\n");
}

void cmd_colors(void) {
    const char *names[] = {
        "black", "blue", "green", "cyan",
        "red", "magenta", "brown", "grey",
        "dark grey", "lt blue", "lt green", "lt cyan",
        "lt red", "lt magenta", "yellow", "white"
    };
    for (int i = 0; i < 16; i++) {
        color = i;
        kprint("  "); kprint(names[i]); kprint("\n");
    }
    color = 0x07;
}

void run_command(void) {
    cmdbuf[cmdlen] = 0;

    char *cmd = cmdbuf;
    while (*cmd == ' ') cmd++;
    if (!*cmd) return;

    if (kstrcmp(cmd, "help") == 0)
        cmd_help();
    else if (kstrcmp(cmd, "about") == 0)
        cmd_about();
    else if (kstrcmp(cmd, "mem") == 0)
        cmd_mem();
    else if (kstrcmp(cmd, "clear") == 0)
        clear_screen();
    else if (kstrcmp(cmd, "colors") == 0)
        cmd_colors();
    else if (kstrncmp(cmd, "echo ", 5) == 0) {
        kprint(cmd + 5);
        kprint("\n");
    }
    else if (kstrcmp(cmd, "reboot") == 0) {
        __asm__ volatile("lidt (%%eax)" :: "a"(0));
        __asm__ volatile("int $3");
    }
    else {
        kprint("? ");
        kprint(cmd);
        kprint("\n");
    }
}

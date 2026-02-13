#ifndef TERMINAL_H
#define TERMINAL_H

#define TERMINAL_WIDTH 80
#define TERMINAL_HEIGHT 25
#define TERMINAL_BUFFER_SIZE 256

typedef struct {
    unsigned char write_idx;
    unsigned char read_idx;
    unsigned char buffer[TERMINAL_BUFFER_SIZE];
} terminal_buffer_t;

extern volatile terminal_buffer_t* kb_buffer;

void terminal_init(void);
int terminal_has_input(void);
unsigned char terminal_read_char(void);
void terminal_write_char(char c);
void terminal_write_string(const char *s);
void terminal_clear(void);
void terminal_set_color(unsigned char color);
void terminal_scroll(void);

#endif

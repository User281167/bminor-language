#include <stdio.h>
#include <stdint.h>

void print_int(int32_t value) {
    printf("%d", value);
}

void print_float(float value) {
    printf("%f", value);
}

void print_char(char value) {
    printf("%c", value);
}

void print_bool(int8_t value) {
    if (value) {
        printf("true");
    } else {
        printf("false");
    }
}
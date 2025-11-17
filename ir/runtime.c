#include <stdio.h>
#include <stdint.h>
#include <math.h>

void print_int(int32_t value) {
    printf("%d", value);
}

void print_float(float value) {
    printf("%f", value);
}

void print_char(char value) {
    printf("%c", value);
}

void print_string(const char* value) {
    printf("%s", value);
}

void print_bool(int8_t value) {
    if (value) {
        printf("true");
    } else {
        printf("false");
    }
}

int32_t pow_int(int32_t base, int32_t exponent) {
    return pow(base, exponent);
}
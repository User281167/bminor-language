#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void _bminor_print_int(int32_t value) {
    printf("%d", value);
}

void _bminor_print_float(float value) {
    printf("%f", value);
}

void _bminor_print_char(char value) {
    printf("%c", value);
}

void _bminor_print_string(const char* value) {
    printf("%s", value);
}

void _bminor_print_bool(int8_t value) {
    if (value) {
        printf("true");
    } else {
        printf("false");
    }
}

// ================= Math =================

int32_t _bminor_pow_int(int32_t base, int32_t exponent) {
    return pow(base, exponent);
}

// ================= Strings =================

// Concatena dos strings simples y devuelve un nuevo puntero al Heap
char* _bminor_string_concat(char* s1, char* s2) {
    if (!s1) s1 = "";
    if (!s2) s2 = "";

    size_t len1 = strlen(s1);
    size_t len2 = strlen(s2);

    char* result = (char*)malloc(len1 + len2 + 1);

    if (!result) return NULL;

    strcpy(result, s1);
    strcat(result, s2);

    return result;
}

char* _bminor_string_copy(char* s) {
    if (s == NULL) return strdup("");

    return strdup(s);
}

void _bminor_string_free(char* s) {
    if (!s) return;

    free(s);
    s = NULL;
}
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
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

// ================= Math =================

int32_t pow_int(int32_t base, int32_t exponent) {
    return pow(base, exponent);
}

// ================= BMinorString =================

typedef struct {
    int length;
    char* chars; // Con terminal '\0'
} BMinorString;

// Devuelve un puntero a un BMinorString en el heap.
BMinorString* _bminor_string_from_literal(const char* literal) {
    BMinorString* new_str = (BMinorString*)malloc(sizeof(BMinorString));
    if (!new_str) return NULL; // Manejo de error de memoria

    new_str->length = strlen(literal);

    // Asignamos nueva memoria para los caracteres para que cada string sea independiente.
    new_str->chars = (char*)malloc(new_str->length + 1);
    if (!new_str->chars) {
        free(new_str);
        return NULL;
    }
    strcpy(new_str->chars, literal);

    return new_str;
}

// Función para imprimir nuestro tipo de string.
void print_bminor_string(const BMinorString* str) {
    if (str != NULL && str->chars != NULL) {
        printf("%s", str->chars);
    } else {
        printf("");
    }
}

BMinorString* _bminor_string_concat(const BMinorString* s1, const BMinorString* s2) {
    int len1 = s1 != NULL ? s1->length : 0;
    int len2 = s2 != NULL ? s2->length : 0;

    // Crear el nuevo string resultado
    BMinorString* result = (BMinorString*)malloc(sizeof(BMinorString));
    result->length = len1 + len2;
    result->chars = (char*)malloc(result->length + 1);

    // Copiar los datos
    if (s1)
        strcpy(result->chars, s1->chars);
    if (s2)
        strcat(result->chars, s2->chars);

    return result;
}

BMinorString* _bminor_string_copy(const BMinorString* source) {
    // Si el string fuente es nulo, devolvemos nulo.
    if (!source || !source->chars) {
        return NULL;
    }

    // Reservar memoria para la nueva estructura
    BMinorString* new_str = malloc(sizeof(BMinorString));
    if (!new_str) return NULL;

    new_str->length = source->length;

    // Reservar memoria para la copia de los caracteres
    new_str->chars = malloc(new_str->length + 1);
    if (!new_str->chars) {
        free(new_str); // Limpieza si falla la segunda asignación
        return NULL;
    }

    // Copiar los caracteres usando memcpy, que es rápido y seguro
    memcpy(new_str->chars, source->chars, new_str->length + 1);

    return new_str;
}

void _bminor_string_free(BMinorString* str) {
    if (str != NULL) {
        free(str->chars);
        str->chars = NULL;

        free(str);
        str = NULL;
    }
}
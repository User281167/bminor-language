#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
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

// ================= Arrays =================

struct _bminor_array {
    void* data;
    int32_t element_size;
    int32_t size;
    bool is_string;
};

void _bminor_runtime_error(const char* msg) {
    fprintf(stderr, "Runtime Error: %s\n", msg);
    exit(1);
}

struct _bminor_array* _bminor_array_new(int32_t size, int32_t list_size, int32_t type, bool is_string) {
    if (size <= 0 || size > list_size || list_size < 0) {
        _bminor_runtime_error("Invalid array size");
        return NULL;
    }

    if (list_size > 0 && (list_size != size)) {
        _bminor_runtime_error("Invalid array size");
        return NULL;
    }

    struct _bminor_array* array = (struct _bminor_array*)malloc(sizeof(struct _bminor_array));

    if (!array) return NULL;

    array->data = calloc(size, type);

    if (!array->data) {
        free(array);
        return NULL;
    }

    array->size = size;
    array->element_size = type;
    array->is_string = is_string;
    return array;
}

void _bminor_array_free(struct _bminor_array* array) {
    if (!array) return;

    if (array->is_string) {
        for (int32_t i = 0; i < array->size; i++) {
            _bminor_string_free(((char**)array->data)[i]);
        }
    } else {
        free(array->data);
        array->data = NULL;
    }

    free(array);
    array = NULL;
}

int32_t _bminor_array_size(struct _bminor_array* array) {
    if (!array) return 0;

    return array->size;
}

void _bminor_array_set(struct _bminor_array* array, int32_t index, void* value_ptr) {
    if (!array || !array->data) {
        _bminor_runtime_error("Cannot set value in null array.");
        return;
    }
    if (index < 0 || index >= array->size) {
        _bminor_runtime_error("Array index out of bounds.");
        return;
    }

    // Calcular la ubicación de destino (donde queremos escribir)
    char* base_ptr = (char*)array->data;
    size_t offset = index * array->element_size;
    void* destination_ptr = base_ptr + offset; // Puntero a la celda del array

    if (array->is_string) {
        // liberar y copiar nuevo
        char** old_string_loc = (char**)destination_ptr;

        if (*old_string_loc != NULL) {
            free(*old_string_loc);
        }

        // Duplicar la nueva cadena y almacenar el puntero
        char* new_string = _bminor_string_copy((char*)value_ptr);
        *old_string_loc = new_string; // Almacenar el puntero DEEP COPY
    } else {
        // value_ptr es el puntero al alloca temporal del stack que contiene el valor (i32, i1, etc.)
        memcpy(destination_ptr, value_ptr, array->element_size);
    }
}

void _bminor_array_get(struct _bminor_array* array, int32_t index, void* destination_ptr) {
    if (!array || !array->data) {
        _bminor_runtime_error("Cannot get value from null array.");
        return;
    }
    if (index < 0 || index >= array->size) {
        _bminor_runtime_error("Array index out of bounds.");
        return;
    }

    // Calcular la dirección de la fuente (Source)
    // Usamos (char*) para garantizar la aritmética por bytes.
    char* base_ptr = (char*)array->data;
    size_t offset = index * array->element_size;
    void* source_ptr = base_ptr + offset;

    // Copiar los bytes
    // Copia array->element_size bytes desde source_ptr (el array)
    // hasta destination_ptr (el puntero temporal que viene de LLVM).
    memcpy(destination_ptr, source_ptr, array->element_size);
}

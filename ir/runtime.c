#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

// Errores comunes
typedef enum {
    OK = 0,
    ALLOCATION_ERROR,
    ARRAY_SIZE_ERROR,
    ARRAY_SIZE_MISMATCH,
    ARRAY_INDEX_OUT_OF_BOUNDS,
    ARRAY_NULL_ERROR
} _bminor_error_type;

void _bminor_runtime_error(const char* msg, _bminor_error_type code) {
    fprintf(stderr, "Runtime Error: %s\n", msg);
    exit(code);
}

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

    if (!result) {
        _bminor_runtime_error("Failed to allocate memory.", ALLOCATION_ERROR);
        return NULL;
    };

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

typedef struct _bminor_array {
    void* data;
    int32_t data_size;
    int32_t size;
    bool is_string;
    int32_t reference_count;
} _bminor_array;



_bminor_array* _bminor_array_new(int32_t size, int32_t list_size, int32_t type, bool is_string) {
    if (size <= 0 || ((list_size != 0) && (size > list_size || list_size < 0))) {
        _bminor_runtime_error("Invalid array size, size must be > 0 and <= list size.", ARRAY_SIZE_ERROR);
        return NULL;
    }

    if ((list_size > 0) && (list_size != size)) {
        _bminor_runtime_error("Invalid array size, size must be equal to list size.", ARRAY_SIZE_MISMATCH);
        return NULL;
    }

    _bminor_array* array = (_bminor_array*)malloc(sizeof(_bminor_array));

    if (!array) {
        _bminor_runtime_error("Failed to allocate memory.", ALLOCATION_ERROR);
        return NULL;
    };

    array->data = calloc(size, type);

    if (!array->data) {
        _bminor_runtime_error("Failed to allocate memory.", ALLOCATION_ERROR);
        free(array);
        return NULL;
    }

    array->size = size;
    array->data_size = type;
    array->is_string = is_string;
    array->reference_count = 1;
    return array;
}

void _bminor_array_free(_bminor_array* array) {
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

int32_t _bminor_array_size(_bminor_array* array) {
    if (!array) return 0;

    return array->size;
}

void _bminor_array_set(_bminor_array* array, int32_t index, void* value_ptr) {
    if (!array || !array->data) {
        _bminor_runtime_error("Cannot set value in null array.", ARRAY_NULL_ERROR);
        return;
    }
    if (index < 0 || index >= array->size) {
        _bminor_runtime_error("Array index out of bounds.", ARRAY_INDEX_OUT_OF_BOUNDS);
        return;
    }

    // Calcular la ubicación de destino (donde queremos escribir)
    char* base_ptr = (char*)array->data;
    size_t offset = index * array->data_size;
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
        memcpy(destination_ptr, value_ptr, array->data_size);
    }
}

void _bminor_array_get(_bminor_array* array, int32_t index, void* destination_ptr) {
    if (!array || !array->data) {
        _bminor_runtime_error("Cannot get value from null array.", ARRAY_NULL_ERROR);
        return;
    }
    if (index < 0 || index >= array->size) {
        _bminor_runtime_error("Array index out of bounds.", ARRAY_INDEX_OUT_OF_BOUNDS);
        return;
    }

    // Calcular la dirección de la fuente (Source)
    // Usamos (char*) para garantizar la aritmética por bytes.
    char* base_ptr = (char*)array->data;
    size_t offset = index * array->data_size;
    void* source_ptr = base_ptr + offset;

    // Copiar los bytes
    // Copia array->data_size bytes desde source_ptr (el array)
    // hasta destination_ptr (el puntero temporal que viene de LLVM).
    memcpy(destination_ptr, source_ptr, array->data_size);
}

void _bminor_array_incref(_bminor_array* array) {
    if (array)
    {
        array->reference_count += 1;
    }
}

void _bminor_array_decref(_bminor_array* array) {
    if (array && (--array->reference_count == 0)) {
        _bminor_array_free(array);
    }
}
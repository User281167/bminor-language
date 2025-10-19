# 🧬 bminor — Lenguaje de Programación Experimental en Python con SLY

**bminor** es un lenguaje de programación inspirado en C, diseñado para explorar conceptos de compiladores, análisis léxico, sintáctico y semántico usando Python y la biblioteca [SLY](https://github.com/dabeaz/sly). Este proyecto incluye escaneo, parsing, análisis semántico y ejecución de código fuente `.bminor`.

---

## 📘 Documentación del Lenguaje

Para una descripción más detallada de la gramática, reglas de sintaxis, semántica y ejemplos de uso del lenguaje **bminor**, consulta el archivo [bminor.md](docs/bminor.md).

Este documento incluye:

- 📐 Definición formal de la gramática en estilo BNF
- 🧠 Reglas semánticas y tipos de datos
- 🧪 Ejemplos de código válidos e inválidos
- 🛠️ Detalles sobre el diseño del lexer y parser con SLY
- 🔍 Explicación de operadores y precedencia
- 📚 Guía para escribir funciones, arreglos y estructuras de control

---


## 📦 Estructura del Lenguaje

bminor soporta:

- **Declaraciones** de variables, arreglos y funciones
- **Sentencias de control**: `if`, `for`, `while`, `do-while`
- **Bloques** y expresiones anidadas
- **Tipos primitivos**: `INTEGER`, `FLOAT`, `BOOLEAN`, `CHAR`, `STRING`, `VOID`
- **Arreglos** de una dimensión y funciones
- **Operadores**: aritméticos, lógicos, relacionales, incremento/decremento, negación

---

## ⚙️ Instalación

Antes de ejecutar bminor, asegúrate de tener Python 3.8 o superior y los siguientes paquetes instalados:

```bash
pip install -r requirements.txt
```
---

## 🧪 Ejecución de Componentes

El archivo `bminor.py` permite ejecutar tres fases del compilador:

- **Escaneo léxico** (`--scan`)
- **Parsing / análisis sintáctico** (`--parser`)
- **Análisis semántico** (`--semantic`)

### 📍 Sintaxis general

```bash
python bminor.py --scan|--parser|--semantic [test | archivo.bminor | test/.../*.py]
```

---

### 🔍 `run_scan(filename)`

Analiza el archivo `.bminor` y muestra los tokens generados por el lexer.

#### Ejemplos:

```bash
python bminor.py --scan ejemplo.bminor
python bminor.py --scan ejemplo.bminor --table
```

- `--table`: muestra los tokens en una tabla con `rich`.

También puedes ejecutar pruebas unitarias:

```bash
python bminor.py --scan test/scanner/good1.py
python bminor.py --scan test
```

---

### 🧩 `run_parser(filename)`

Genera el árbol de sintaxis abstracta (AST) a partir del código fuente.

#### Ejemplos:

```bash
python bminor.py --parser ejemplo.bminor
python bminor.py --parser ejemplo.bminor --pretty
python bminor.py --parser ejemplo.bminor --json
```

- `--print`: imprime el AST en consola.
- `--pretty`: imprime el AST con formato.
- `--json`: exporta el AST en formato JSON.

También puedes ejecutar pruebas unitarias:

```bash
python bminor.py --parser test/parser/good1.py
python bminor.py --parser test
```

---

### 🧠 `run_semantic(filename)`

Realiza el análisis semántico sobre el AST generado.

#### Ejemplos:

```bash
python bminor.py --semantic ejemplo.bminor
```

También puedes ejecutar pruebas semánticas:

```bash
python bminor.py --semantic test/semantic/good1.py
python bminor.py --semantic test
```

---

## 🧪 Estructura de Pruebas

El proyecto incluye pruebas unitarias organizadas por fase:

```
test/
├── scanner/
├── parser/
└── semantic/
```

Puedes ejecutar todas las pruebas de una fase con:

```bash
python bminor.py --scan test
python bminor.py --parser test
python bminor.py --semantic test
```

Proceso completo para crear, modificar y usar tu extensión de VSCode para el lenguaje **bminor**, incluyendo la parte de la expresión regular (`regex`) y la instalación del `.vsix`:

---

## 🛠️ 1. Generar el proyecto base

Puedes usar el generador oficial de extensiones de VSCode:

```bash
npm install -g yo generator-code
yo code
```

- Elige **New Language Support**.
- Nombre del lenguaje: `bminor`
- Identificador: `bminor`
- Extensión de archivo: `.bminor`
- Esto crea una carpeta con tu proyecto base.

---

## ✏️ 2. Modificar la expresión regular (`regex`) para resaltar palabras clave

Dentro del archivo `syntaxes/bminor.tmLanguage.json`:

- Busca la sección `"patterns"` y localiza el bloque que contiene `"match"` con una expresión regular.
- Modifica la expresión para incluir tus palabras clave. Ejemplo:

```json
{
  "name": "keyword.control.bminor",
  "match": "\\b(if|else|while|return|print|int|bool|string)\\b"
}
```

- Asegúrate de que las palabras estén separadas por `|` y rodeadas por `\\b` para que coincidan como palabras completas.

---

## 📦 3. Empaquetar la extensión como `.vsix`

Primero instala `vsce` si no lo tienes:

```bash
npm install -g vsce
```

Luego, desde la raíz del proyecto:

```bash
vsce package
```

Esto genera un archivo como `bminor-0.0.1.vsix`.

---

## 💻 4. Instalar la extensión en VSCode

1. Abre VSCode.
2. Presiona `Ctrl+Shift+P` (o `Cmd+Shift+P` en Mac).
3. Escribe: `Extensions: Install from VSIX...`
4. Selecciona el archivo `bminor-0.0.1.vsix`.
5. ¡Listo! Tu extensión está instalada.

---

## ✅ 5. Verificar funcionamiento

- Abre un archivo con extensión `.bminor`.
- Deberías ver el resaltado de sintaxis aplicado según tu configuración.
- Puedes seguir ajustando colores, estilos y reglas en el archivo `tmLanguage.json`.

---

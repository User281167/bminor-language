# ejecutar cada archivo en /typechecker
import glob
import os
import sys

# Agrega la carpeta raíz al sys.path
base_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(base_dir, ".."))
sys.path.insert(0, project_root)

from parser import Parser

from scanner import Lexer
from semantic import Check
from utils import clear_errors, errors_detected

print("Ejecutando run_bminor_test.py...")

# Ruta absoluta relativa al script
base_dir = os.path.dirname(__file__)


def run_good():
    pattern = os.path.join(base_dir, "typechecker", "good*.bminor")
    files = glob.glob(pattern)

    print("Archivos encontrados:", len(files))

    for file in files:
        print("Ejecutando", file)

        with open(file) as f:
            code = f.read()

        tokens = Lexer().tokenize(code)
        ast = Parser().parse(tokens)
        env = Check.checker(ast)

        if errors_detected():
            print("Errores detectados en", file)
            sys.exit(1)


def run_bad():
    pattern = os.path.join(base_dir, "typechecker", "bad*.bminor")
    files = glob.glob(pattern)

    print("Archivos encontrados:", len(files))

    for file in files:
        print("Ejecutando", file)

        with open(file) as f:
            code = f.read()

        tokens = Lexer().tokenize(code)
        ast = Parser().parse(tokens)
        env = Check.checker(ast)

        if not errors_detected():
            print("Errores detectados en", file)
            sys.exit(1)

        clear_errors()


run_good()
run_bad()

import importlib.util
import os
import re
import sys
import unittest
from parser import ASTPrinter, Parser

import rich
from rich.table import Table

from ir import IRGenerator, run_llvm_ir
from scanner import Lexer
from semantic import Check
from utils import print_json


def run_scan(filename):
    if filename.endswith(".bminor"):
        try:
            lex = Lexer()
            tokens = list(lex.tokenize(open(filename).read()))

            if "--table" in sys.argv:
                t = Table(show_header=True, header_style="blue")
                t.add_column("Type")
                t.add_column("Value")

                for token in tokens:
                    t.add_row(token.type, str(token.value))

                rich.print(t)
        except Exception as e:
            print(e)
            sys.exit(1)
    elif filename.endswith(".py"):
        match = re.match(r"test[\\/]{1}scanner[\\/]{1}(good|bad)([0-9]+)\.py", filename)
        if not match:
            print("Invalid test file name. Use test/scanner/(good|bad)[0-9].py")
            sys.exit(1)
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module)
        )
    elif filename == "test":
        test_dir = os.path.join(os.path.dirname(__file__), "test", "scanner")
        suite = unittest.TestLoader().discover(test_dir, pattern="*.py")
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print("Invalid file type for scan. Use .bminor or .py files")
        sys.exit(1)


def run_parser(filename):
    if filename.endswith(".bminor"):
        try:
            parser = Parser()
            code = open(filename).read()

            tokens = Lexer().tokenize(code)
            ast = parser.parse(tokens)

            if "--json" in sys.argv:
                print_json(ast)
            if "--print" in sys.argv:
                print(ast)
            if "--pretty" in sys.argv:
                ast.pretty()
            if "--graph" in sys.argv:
                dot = ASTPrinter.render(ast)

                if "-svg" in sys.argv:
                    dot.format = "svg"
                else:
                    dot.format = "png"

                dot.render(filename + "_ast", view=False)
        except Exception as e:
            print(e)
            sys.exit(1)
    elif filename.endswith(".py"):
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module)
        )
    elif filename == "test":
        test_dir = os.path.join(os.path.dirname(__file__), "test", "parser")
        suite = unittest.TestLoader().discover(test_dir, pattern="*.py")
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print("Invalid file type for parser. Use .bminor or .py files")
        sys.exit(1)


def run_semantic(filename):
    if filename.endswith(".bminor"):
        try:
            parser = Parser()
            code = open(filename).read()

            tokens = Lexer().tokenize(code)
            ast = parser.parse(tokens)
            env = Check.checker(ast)

            if "--table" in sys.argv:
                env.print()
        except Exception as e:
            print(e)
            sys.exit(1)
    elif filename.endswith(".py"):
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module)
        )
    elif filename == "test":
        test_dir = os.path.join(os.path.dirname(__file__), "test", "semantic")
        suite = unittest.TestLoader().discover(test_dir, pattern="*.py")
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print("Invalid file type for parser. Use .bminor or .py files")
        sys.exit(1)


def run_ir(filename):
    if filename.endswith(".bminor"):
        try:
            gen = IRGenerator().generate_from_code(open(filename).read())

            if "--lli" in sys.argv:
                run_llvm_ir(gen)
        except Exception as e:
            print(e)
            sys.exit(1)
    elif filename.endswith(".py"):
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module)
        )
    elif filename == "test":
        test_dir = os.path.join(os.path.dirname(__file__), "test", "ir")
        suite = unittest.TestLoader().discover(test_dir, pattern="*.py")
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print("Invalid file type for parser. Use .bminor or .py files")
        sys.exit(1)


if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    if len(sys.argv) < 3:
        print(
            "Usage: bminor.py --scan|--parser|--semantic [test | filename.bminor | test/.../*.py]"
        )
        print("Example: bminor.py --scan test/scanner/good1.bminor")
        print("\nparser flags: --print | --pretty | --json | --graph")
        print("Example: bminor.py --parser code.bminor --json")
        print("\nscan flags: --table")
        print("Example: bminor.py --scan code.bminor --table")
        print("\nsemantic flags: --table")
        print("Example: bminor.py --semantic code.bminor --table")
        sys.exit(1)

    mode = sys.argv[1]
    filename = sys.argv[2]

    if mode == "--scan":
        run_scan(filename)
    elif mode == "--parser":
        run_parser(filename)
    elif mode == "--semantic":
        run_semantic(filename)
    elif mode == "--ir":
        run_ir(filename)
    else:
        print("Invalid mode. Use --scan, --parser or --semantic")
        sys.exit(1)
        print("Invalid mode. Use --scan, --parser or --semantic")
        sys.exit(1)

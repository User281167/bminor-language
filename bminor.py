import sys
import importlib.util
import unittest
import re
import os
from scanner import Lexer
from parser import Parser
from utils import save_ast_to_json, print_json
import rich
from rich.table import Table


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
        match = re.match(
            r'test[\\/]{1}scanner[\\/]{1}(good|bad)([0-9]+)\.py', filename)
        if not match:
            print(
                "Invalid test file name. Use test/scanner/(good|bad)[0-9].py")
            sys.exit(1)
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module))
    elif filename == "test":
        test_dir = os.path.join(
            os.path.dirname(__file__), 'test', 'scanner')
        suite = unittest.TestLoader().discover(test_dir, pattern='*.py')
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
        except Exception as e:
            print(e)
            sys.exit(1)
    elif filename.endswith(".py"):
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module))
    elif filename == "test":
        test_dir = os.path.join(
            os.path.dirname(__file__), 'test', 'parser')
        suite = unittest.TestLoader().discover(test_dir, pattern='*.py')
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print("Invalid file type for parser. Use .bminor or .py files")
        sys.exit(1)


if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    if len(sys.argv) < 3:
        print(
            "Usage: bminor.py --scan|--parser [test | filename.bminor | test/.../*.py]")
        print("Example: bminor.py --scan test/scanner/good1.bminor")
        print("\nparser flags: --print | --pretty | --json")
        print("Example: bminor.py --parser code.bminor --json")
        print("\nscan flags: --table")
        print("Example: bminor.py --scan code.bminor --table")
        sys.exit(1)

    mode = sys.argv[1]
    filename = sys.argv[2]

    if mode == "--scan":
        run_scan(filename)
    elif mode == "--parser":
        run_parser(filename)
    else:
        print("Invalid mode. Use --scan or --parser")
        sys.exit(1)

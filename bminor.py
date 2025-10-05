from utils import save_ast_to_json

if __name__ == "__main__":
    import sys
    import importlib.util
    import unittest
    import re
    import os

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    from scanner import Lexer
    from parser import Parser

    def run_scan(filename):
        if filename.endswith(".bminor"):
            try:
                lex = Lexer()
                tokens = list(lex.tokenize(open(filename).read()))
                # for token in tokens:
                #     print(token)
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

                if "json" in sys.argv:
                    save_ast_to_json(ast)
                if "print" in sys.argv:
                    print(ast.pretty())
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

    if len(sys.argv) < 3:
        print(
            "Usage: bminor.py --scan|--parser [test | filename.bminor | test/.../*.py]")
        print("Example: bminor.py --scan test/scanner/good1.bminor")
        print("parser flags: --print | --json")
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

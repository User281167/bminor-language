
def save_json(ast, code=""):
    import json

    with open("ast.json", "w") as f:
        def ast_to_dict(node):
            if isinstance(node, list):
                return [ast_to_dict(item) for item in node]
            elif hasattr(node, "__dict__"):
                result = {
                    "_type": node.__class__.__name__  # ← Aquí agregas el nombre de clase
                }
                for key, value in node.__dict__.items():
                    result[key] = ast_to_dict(value)
                return result
            else:
                return node

        f.write(json.dumps({
            'code': code,
            'ast': ast_to_dict(ast)
        }, indent=2))


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
                save_json(ast)
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

if __name__ == "__main__":
    import sys
    import importlib.util
    import unittest
    import re
    import os

    # Add the root directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    from scanner import Lexer

    # options for console input
    # bminor.py --scan [filename.bminor | test/scan/filename.py]

    if len(sys.argv) < 3 or sys.argv[1] != "--scan":
        print(
            "Usage: bminor.py --scan [filename.bminor | test/scan/filename.py]")
        sys.exit(1)

    filename = sys.argv[2]

    if filename.endswith(".bminor"):
        try:
            lex = Lexer()
            tokens = list(lex.tokenize(open(filename).read()))
            for token in tokens:
                print(token)
        except Exception as e:
            print(e)
            sys.exit(1)
    elif filename.endswith(".py"):
        # run test
        # regex for test test//scanner//(good|bad)[0-9].py
        match = re.match(
            r'test[\\/]{1}scanner[\\/]{1}(good|bad)([0-9]+)\.py', filename)
        if not match:
            print(
                "Invalid test file name. Use test/scanner/(good|bad)[0-9].py")
            sys.exit(1)

        # import test module
        path = os.path.abspath(filename)
        spec = importlib.util.spec_from_file_location("dynamic_test", path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        # run unittest with output
        unittest.TextTestRunner(verbosity=2).run(
            unittest.TestLoader().loadTestsFromModule(test_module))
    else:
        print("Invalid file type. Use .bminor or .py files")
        sys.exit(1)

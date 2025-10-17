def ast_to_dict(node):
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif hasattr(node, "__dict__"):
        result = {"_type": node.__class__.__name__}  # ← Aquí agregas el nombre de clase
        for key, value in node.__dict__.items():
            result[key] = ast_to_dict(value)
        return result
    else:
        return node


def save_ast_to_json(ast, code="", filename="ast.json"):
    import json

    with open(filename, "w") as f:
        f.write(json.dumps({"code": code, "ast": ast_to_dict(ast)}, indent=2))


def print_json(ast, code=""):
    import json

    print(json.dumps({"code": code, "ast": ast_to_dict(ast)}, indent=2))

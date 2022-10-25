import ast


def Parse(content, filename, vars_override=None, builtin_vars=None):
    local_scope = {}
    deps = []
    node_or_string = ast.parse(content, filename=filename, mode='exec')
    for node in node_or_string.body:
        if isinstance(node, ast.Assign):
            if len(node.targets) > 0:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    if target.id == 'deps':
                        if isinstance(node.value, ast.List):
                            for i in node.value.elts:
                                if isinstance(i, ast.Constant):
                                    deps.append(i.value)
    local_scope['deps'] = deps
    return local_scope
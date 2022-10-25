import ast


def Parse(content, filename, vars_override=None, builtin_vars=None):
    local_scope = {}
    deps = []
    sync_url = None
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
                    if target.id == 'sync_url':
                        if isinstance(node.value, ast.Constant):
                            sync_url = node.value.value
    local_scope['deps'] = deps
    local_scope['sync_url'] = sync_url
    return local_scope

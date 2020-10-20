from iris.lib.built import pybindings


class Context:
    def __init__(self):
        self.variables = pybindings

    def new(self, name, value):
        self.variables[name] = value

    def delete(self, name):
        self.variables.pop(name)

    def __getitem__(self, item):
        if '.' in item:
            return get_var(item, mainspace_context, self)
        else:
            return self.variables[item]

    def __setitem__(self, key, value):
        if '.' in key:
            set_var(key, value, mainspace_context, self)
        else:
            self.variables[key] = value

    def __contains__(self, item):
        return item in self.variables

    def __str__(self):
        return f'Context(vars={self.variables})'

    __repr__ = __str__


mainspace_context = Context()


"""
NEVER USE FUNCTIONS BELOW! NEVER! NEVER EVER!
THEY ARE RAISING RECURSION ERROR
THEY ARE ABSOLUTELY LOCAL FUNCTIONS

NEEEVEEER UUUSEEE THEEEEM
"""


def set_var(var, val, global_context=None, local_context=None, set_to_local=False, set_to_global=False):
    """
    if both if set_to_local and set_to_global are False, destination context will be chosen automatically
    """
    if set_to_local:
        return _set_var(var, val, local_context)
    if set_to_global:
        return _set_var(var, val, global_context)

    split_var_name = var.split('.')

    if len(split_var_name) == 1:
        local_context[var] = val
        return

    if split_var_name[0] in local_context:
        context = local_context
    else:
        context = global_context

    _set_var(split_var_name, val, context)


def _set_var(var: list, val: any, context):
    # var[:-1] cause we need to get a context, not variable value
    dest_context = _get_var(var[:-1], context)

    dest_context[var[-1]] = val


def get_var(var, global_context, local_context):
    split_var = var.split('.')

    if split_var[0] in local_context:
        context = local_context
    else:
        context = global_context

    return _get_var(split_var, context)


def _get_var(var: list, context):
    result = context[var[0]]

    for link in var[1:]:
        result = result[link]

    return result

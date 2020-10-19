from iris.core.composer import compose
from iris.core.textutils import cut_blocks
from iris.core.blocks import ConditionBranch
from iris.core.maincore.parser import parser
from iris.core.context import mainspace_context
from iris.core.blockscompiler import compile_block
from iris.core.constants import (IF_STMNT, ELIF_STMNT, ELSE_STMNT, CONDITION,
                                 CLASS_ASSIGN, FUNC_ASSIGN, VAR_ASSIGN,
                                 EXPRESSION, FUNCTION)


def compile_from_source(raw, curr_eid=None, curr_context=None):
    if curr_eid is None:
        curr_eid = 0
    if curr_context is None:
        curr_context = mainspace_context

    source = compose(raw)
    raw_blocks = cut_blocks(source)
    cooked_blocks = []

    for block in raw_blocks:
        compiled_block = compile_block(curr_eid, block, curr_context, execute_block)

        if compiled_block.type in (CLASS_ASSIGN, FUNCTION):
            curr_context[compiled_block.name] = compiled_block

        if compiled_block.type in (CLASS_ASSIGN, FUNCTION, IF_STMNT, ELIF_STMNT, ELSE_STMNT):    # we need to parse block's body
            use_context = curr_context[compiled_block.name] if compiled_block.type in (CLASS_ASSIGN, FUNC_ASSIGN) else curr_context
            compiled_block.body, curr_eid = compile_from_source(compiled_block.body, curr_eid=curr_eid, curr_context=use_context)
            curr_eid -= 1

        curr_eid += 1
        cooked_blocks.append(compiled_block)

    return conditions2condition_objects(cooked_blocks), curr_eid


def conditions2condition_objects(blocks):
    curr_condition = None
    cooked_blocks = []

    for block in blocks:
        if block.type in (ELIF_STMNT, ELSE_STMNT) and curr_condition is None:
            raise SyntaxError('found elif/else condition without if condition')

        if block.type == IF_STMNT:
            if curr_condition:
                cooked_blocks.append(curr_condition)

            curr_condition = ConditionBranch(block)
        elif block.type == ELIF_STMNT:
            curr_condition.elif_expr.append(block)
        elif block.type == ELSE_STMNT:
            curr_condition.else_expr = block
            cooked_blocks.append(curr_condition)
            curr_condition = None
        else:
            cooked_blocks.append(block)

    if curr_condition:
        cooked_blocks.append(curr_condition)

    return cooked_blocks


def execute_block(block, context):
    if block.type == VAR_ASSIGN:
        context[block.name] = parser.execute(block.value, context=context)
    elif block.type == FUNC_ASSIGN:
        context[block.name] = block
    elif block.type == CONDITION:
        condition = block.get_branch(context)

        if condition is None:
            return

        execute_blocks(condition.body, context)
    elif block.type == EXPRESSION:
        parser.execute(block.value, context=context)


def execute_blocks(blocks, context=mainspace_context):
    for block in blocks:
        execute_block(block, context)


def interpret(source):
    blocks, _ = compile_from_source(source)

    execute_blocks(blocks)

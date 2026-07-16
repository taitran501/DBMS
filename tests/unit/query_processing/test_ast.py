from dbms.query_processing.ast import AST


def test_ast_can_be_created():
    ast = AST("root")
    assert ast.root_node == "root"


def test_traverse():
    ast = AST("root")
    assert ast.traverse() == []

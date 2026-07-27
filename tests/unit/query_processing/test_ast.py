from dbms.query_processing.ast import AST, LiteralNode


def test_ast_can_be_created():
    ast = AST("root")
    assert ast.root_node == "root"


def test_traverse():
    root = LiteralNode("root")
    ast = AST(root)

    assert ast.traverse() == [root]

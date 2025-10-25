# type: ignore

from services import generator


# Dummy columns mapping for tests
def columns():
    return {"A": "col1", "B": "col2", "C": "col3"}


def test_binary_maps_add():
    ast = {
        "type": "binary-expression",
        "operator": "+",
        "left": {"type": "cell", "refType": "relative", "key": "A1"},
        "right": {"type": "number", "value": 5},
    }
    result = generator.binary_maps(ast, columns())
    assert result["sql"] == "(col1) + (5)"


def test_function_maps_sum():
    ast = {
        "type": "function",
        "name": "SUM",
        "arguments": [
            {
                "type": "cell-range",
                "left": {"type": "cell", "refType": "relative", "key": "A1"},
                "right": {"type": "cell", "refType": "relative", "key": "B1"},
            }
        ],
    }
    result = generator.function_maps(ast, columns())
    assert result["sql"] == "col1 + col2"


def test_cell_range_maps():
    ast = {
        "type": "cell-range",
        "left": {"type": "cell", "refType": "relative", "key": "A1"},
        "right": {"type": "cell", "refType": "relative", "key": "C1"},
    }
    result = generator.cell_range_maps(ast, columns())
    assert result["columns"] == ["col1", "col2", "col3"]
    assert result["error"] is None


def test_cell_maps_found():
    ast = {"type": "cell", "refType": "relative", "key": "A1"}
    result = generator.cell_maps(ast, columns())
    assert result["sql"] == "col1"
    assert result["error"] is None


def test_cell_maps_not_found():
    ast = {"type": "cell", "refType": "relative", "key": "Z1"}
    result = generator.cell_maps(ast, columns())
    assert result["sql"] == ""
    assert result["error"] is not None


def test_number_maps():
    ast = {"type": "number", "value": 42.5}
    result = generator.number_maps(ast, columns())
    assert result["sql"] == 42.5
    assert result["value"] == 42.5


def test_logical_maps_true():
    ast = {"type": "logical", "value": True}
    result = generator.logical_maps(ast, columns())
    assert result["sql"] == "TRUE"
    assert result["value"] is True


def test_logical_maps_false():
    ast = {"type": "logical", "value": False}
    result = generator.logical_maps(ast, columns())
    assert result["sql"] == "FALSE"
    assert result["value"] is False


def test_text_maps():
    ast = {"type": "text", "value": "Hello, World!"}
    result = generator.text_maps(ast, columns())
    assert result["sql"] == "'Hello, World!'"
    assert result["value"] == "Hello, World!"


def test_unary_maps():
    ast = {
        "type": "unary-expression",
        "operator": "-",
        "operand": {"type": "number", "value": 5},
    }
    result = generator.unary_maps(ast, columns())
    assert result["sql"] == "-(5)"
    assert result["operator"] == "-"


def test_reference_maps_found():
    ast = {
        "type": "reference-node",
        "sheet_name": "Sheet2",
        "key": "A1",
        "refType": "relative",
    }
    result = generator.reference_maps(ast, columns())
    assert result["sql"] == "Sheet2.col1"
    assert result["error"] is None


def test_reference_maps_not_found():
    ast = {
        "type": "reference-node",
        "sheet_name": "Sheet2",
        "key": "Z1",
        "refType": "relative",
    }
    result = generator.reference_maps(ast, columns())
    assert result["sql"] == ""
    assert result["error"] is not None

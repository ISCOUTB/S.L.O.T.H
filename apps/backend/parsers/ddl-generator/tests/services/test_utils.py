from services import utils


def test_get_row_from_cell():
    assert utils.get_row_from_cell("A1") == 1
    assert utils.get_row_from_cell("BC25") == 25
    assert utils.get_row_from_cell("Z999") == 999


def test_get_rows_range():
    assert utils.get_rows_range("A1", "A3") == [1, 2, 3]
    assert utils.get_rows_range("B5", "B7") == [5, 6, 7]
    assert utils.get_rows_range("C10", "C10") == [10]


def test_get_column_from_cell():
    assert utils.get_column_from_cell("A1") == "A"
    assert utils.get_column_from_cell("BC25") == "BC"
    assert utils.get_column_from_cell("Z999") == "Z"


def test_excel_col_to_index():
    assert utils.excel_col_to_index("A") == 1
    assert utils.excel_col_to_index("Z") == 26
    assert utils.excel_col_to_index("AA") == 27
    assert utils.excel_col_to_index("AZ") == 52
    assert utils.excel_col_to_index("BA") == 53
    assert utils.excel_col_to_index("ZZ") == 702
    assert utils.excel_col_to_index("AAA") == 703


def test_index_to_excel_col():
    assert utils.index_to_excel_col(1) == "A"
    assert utils.index_to_excel_col(26) == "Z"
    assert utils.index_to_excel_col(27) == "AA"
    assert utils.index_to_excel_col(52) == "AZ"
    assert utils.index_to_excel_col(53) == "BA"
    assert utils.index_to_excel_col(702) == "ZZ"
    assert utils.index_to_excel_col(703) == "AAA"


def test_get_column_range():
    assert utils.get_column_range("A", "C") == ["A", "B", "C"]
    assert utils.get_column_range("Y", "AA") == ["Y", "Z", "AA"]
    assert utils.get_column_range("AZ", "BB") == ["AZ", "BA", "BB"]
    assert utils.get_column_range("A", "A") == ["A"]


def test_get_all_cells_from_range():
    assert utils.get_all_cells_from_range("A1", "A2") == ["A1", "A2"]
    assert utils.get_all_cells_from_range("A1", "B2") == [
        "A1",
        "A2",
        "B1",
        "B2",
    ]
    assert utils.get_all_cells_from_range("C3", "D4") == [
        "C3",
        "C4",
        "D3",
        "D4",
    ]
    assert utils.get_all_cells_from_range("A1", "A1") == ["A1"]

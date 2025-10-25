# type: ignore

from services import sql


def test_get_sql_from_function_sum():
    args = [{"columns": ["col1", "col2", "col3"]}]
    result = sql.get_sql_from_function("SUM", args)
    assert result == "col1 + col2 + col3"


def test_get_sql_from_function_if():
    args = [{"sql": "col1 > 10"}, {"sql": "'OK'"}, {"sql": "'NO'"}]
    result = sql.get_sql_from_function("IF", args)
    assert result == "CASE WHEN col1 > 10 THEN 'OK' ELSE 'NO' END"


def test_get_sql_from_function_and():
    args = [{"sql": "col1 > 10"}, {"sql": "col2 < 5"}, {"sql": "col3 = 7"}]
    result = sql.get_sql_from_function("AND", args)
    assert result == "col1 > 10 AND col2 < 5 AND col3 = 7"


def test_get_sql_from_function_unsupported():
    result = sql.get_sql_from_function("UNKNOWN", [])
    assert result == "UNSUPPORTED_FUNCTION(UNKNOWN)"

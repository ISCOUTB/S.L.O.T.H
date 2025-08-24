from main import main, generate_sql, SQL_BUILDER_STUB
import sys
import pytest
import os

@pytest.fixture(scope='module')
def file_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_example = os.path.join(base_dir, '../../../../benchmarks/static/acme__users__sample1.xlsx')

    return file_example

def test_exists_file(file_path: str) -> None:
    assert os.path.exists(file_path) == True, "test file should exists"


def test_generate_sql(file_path: str) -> None:
    with open(file_path, 'rb') as file:
        file_bytes = file.read()
    
    file_name = os.path.basename(file_path)
    content = main(filename=file_name, file_bytes=file_bytes)
    result = content['result']
    columns = content['columns']

    ddls = {
        sheet: {
            str(col_name): result[sheet][letter][0]  
            for letter, col_name in columns[sheet].items()
            if isinstance(col_name, str) and result[sheet][letter] and isinstance(result[sheet][letter][0], dict)
        }
        for sheet in columns.keys()
    }

    sys.stdout.write(
        f'{generate_sql(
            SQL_BUILDER_STUB,
            ddls["Sheet1"], # type: ignore
            {
                "id": {"type": "INTEGER", "extra": "PRIMARY KEY"},
                "name": {"type": "TEXT"},
                "age": {"type": "INTEGER"},
                "is_adult": {"type": "TEXT"},
            },
            table_name="test_table",
        )}'
    )

    assert True

    

    
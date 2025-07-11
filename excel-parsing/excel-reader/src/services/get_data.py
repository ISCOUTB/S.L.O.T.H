import services.dtypes as dtypes
from services.utils import (
    open_file_from_bytes,
    extract_formulas,
    convert_csv_to_excel,
    monitor_performance,
)
import logging

logging.basicConfig(level=logging.INFO)


@monitor_performance("get_data_from_spreadsheet")
def get_data_from_spreadsheet(
    filename: str, file_bytes: bytes, limit: int = 50
) -> dtypes.SpreadsheetContent:
    """
    Main function to read an Excel file and extract formulas.

    Args:
        filename (str): The name of the spreadsheet file.
        file_bytes (bytes): The bytes of the Excel file.
        limit (int): The maximum number of cells to extract per column.

    Returns:
        dtypes.SpreadsheetContent: A dictionary containing raw data, columns, and structured data
        extracted from the spreadsheet file.
    """

    if filename.endswith((".xlsx", ".xls")):
        workbook = open_file_from_bytes(file_bytes)
    elif filename.endswith(".csv"):
        workbook = convert_csv_to_excel(file_bytes)
    else:
        raise NotImplementedError(
            "Unsupported file format. Only .xlsx, .xls, and .csv are supported."
        )

    cells = extract_formulas(workbook, limit)
    columns = {
        sheet: dict(map(lambda x: (x[0], x[1][0]["value"]), sheet_data.items()))
        for sheet, sheet_data in cells.items()
    }
    return {
        "raw_data": cells,
        "columns": columns,
        "data": {
            sheet: dict(
                map(
                    lambda x: (x[0], x[1][1:]), zip(columns[sheet], sheet_data.values())
                )
            )
            for sheet, sheet_data in cells.items()
        },
    }


if __name__ == "__main__":
    import json
    import os.path

    file_example = "../../../typechecking/backend/static/acme__users__sample1.xlsx"
    with open(file_example, "rb") as file:
        file_bytes = file.read()

    content = get_data_from_spreadsheet(
        os.path.basename(file_example), file_bytes, limit=-1
    )
    print(json.dumps(content, indent=4))

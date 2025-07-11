# Temporal REST server to communicate with typechecking service

from core.config import settings
from main import main, generate_sql, SQL_BUILDER_STUB

import json
import logging
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, UploadFile, Form

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExcelReader")


app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.post("/excel-parser")
async def read_excel(
    spreadsheet: UploadFile, dtypes_str: str = Form(...)
) -> Dict[str, str]:
    if settings.EXCEL_READER_DEBUG:
        print(f"Received dtypes: {dtypes_str}")
        print(f"Received file: {spreadsheet.filename}")

    file_content = await spreadsheet.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="File content is empty")

    filename = spreadsheet.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    try:
        dtypes = json.loads(dtypes_str)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid dtypes JSON: {str(e)}"
        )

    logger.info(f"Processing file: {filename}")
    content = main(filename, file_content)
    result = content["result"]
    columns = content["columns"]

    ddls = {
        sheet: {
            col_name: result[sheet][letter][0]["sql"]
            for letter, col_name in columns[sheet].items()
        }
        for sheet in columns.keys()
    }

    return {
        sheet: generate_sql(SQL_BUILDER_STUB, ddls[sheet], dtypes[sheet], sheet)
        for sheet in ddls.keys()
    }



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server_rest:app",
        host=settings.EXCEL_READER_HOST,
        port=settings.EXCEL_READER_PORT,
        reload=settings.EXCEL_READER_DEBUG,
    )

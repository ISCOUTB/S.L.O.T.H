import json
from typing import Dict

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from main import SQL_BUILDER_STUB, generate_sql, main
from services.utils import monitor_performance
from utils import logger


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/excel-parser")
@monitor_performance("read_excel")
async def read_excel(
    spreadsheet: UploadFile,
    dtypes_str: str = Form(...),
    table_name: str = Form(...),
    limit: int = 50,
    fill_spaces: str = " ",
) -> Dict[str, str]:
    if settings.EXCEL_READER_DEBUG:
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
        raise HTTPException(status_code=400, detail=f"Invalid dtypes JSON: {str(e)}")

    if not table_name:
        table_name = ""

    logger.info(f"Processing file: {filename}")
    content = main(filename, file_content, limit=limit, fill_spaces=fill_spaces)
    result = content["result"]
    columns = content["columns"]

    ddls = {
        sheet: dict(
            map(lambda x: (x[1], result[sheet][x[0]][0]["sql"]), columns[sheet].items())
        )
        for sheet in columns.keys()
    }

    return {
        sheet: generate_sql(
            SQL_BUILDER_STUB, ddls[sheet], dtypes[sheet], f"{table_name}_{sheet}"
        )
        for sheet in ddls.keys()
    }


if __name__ == "__main__":
    import uvicorn

    # TODO: uvicorn uses his own logger, wich kinda pisses me off
    # cuz, the logs from this service have a different format
    # so..., the custom logger declared in utils has to be used by uvicorn somehow

    uvicorn.run(
        "server_rest:app",
        host=settings.EXCEL_READER_HOST,
        port=settings.EXCEL_READER_PORT,
        reload=settings.EXCEL_READER_DEBUG,
    )

import logging
from typing import List, Optional, Type, Union, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Request(BaseModel):
    headers: List[str] = Field(description="Lista di stringhe che specifica gli header della tabella.")
    rows: List[List[str]] = Field(description="Lista di stringhe che specificano il contenuto delle righe.")
    nameLabel : str = Field(description="Stringa che specifica il nome della tabella.")
    id: str = Field(description="Stringa che specifica l'id della tabella.")

class Response(BaseModel):
    ogg: Dict[str, Union[str, List[Dict[str, Any]]]]

class TableDefinerTool(BaseTool):
    name: str = "table_definer"
    description : str = "Utilizza questa funzione quando c'è bisogno di inserire una tabella. La risposta della funzione è un JSON array con la descrizione della tabella data da 'result', senza specificare 'ogg' iniziale."
    args_schema: Type[BaseModel] = Request

    def _run(self, headers: List[str], rows: List[List[str]],nameLabel:str, id: str) -> dict:
        logger.debug(f"Header: {headers}, Body: {rows}, Name: {nameLabel}, id: {id}")

        element = 'table'
        header_row = {
            "type": "row",
            "name": "Header",
            "components": [{"type": "cell", "name": h, "components": []} for h in headers]
        }
        
        data_rows = []
        for i, riga in enumerate(rows):
            row_obj = {
                "type": "row",
                "name": f"Riga {i + 1}",
                "components": [{"type": "cell", "name": val, "components": []} for val in riga]
            }
            data_rows.append(row_obj) 

        result = {
            'element': element,
            'name': nameLabel,
            'id': id,
            'components': [header_row] + data_rows
        }


        response = Response(ogg=result)
        return response.dict()  

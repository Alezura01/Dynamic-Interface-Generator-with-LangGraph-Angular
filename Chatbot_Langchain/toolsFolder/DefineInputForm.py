import logging
from typing import List, Optional, Type, Union
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from enum import Enum

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TypeValues(str, Enum):
    text = "text"
    password = "password"
    email = "email"
    number = "number"
    date = "date"

class Request(BaseModel):
    nameLabel: str = Field(description="Stringa che specifica quale informazione stiamo chiedendo con l'input field.")
    typology : TypeValues = Field(description="Stringa che specifica il tipo dell'input field.")
    id: str = Field(description="Stringa che specifica l'id dell'input field.")
    required: bool = Field(description="Valore che specifica se il riempimento di questo field è obbligatorio o meno.")

class Response(BaseModel):
    ogg: dict[str, Union[str|bool|List]]
 
class InputFormDefiner(BaseTool):
    name: str = "input_form_function"
    description: str = "Utilizza questa funziona quando bisogna chiedere un'informazione. La risposta della funzione è un JSON array con la descrizione dell'input field data da 'result', senza specificare 'ogg' iniziale."
    args_schema : Type[BaseModel] = Request
    
    def _run(self, nameLabel:str,  typology:str, id: str, required:bool) -> dict:
        logger.debug(f"Name: {nameLabel}, typology: {typology}, id: {id}, required: {required}")

        element = 'input'
        
        result = {
            'element': element,
            'type': typology,
            'name': nameLabel,
            'id': id,
            'required':required,
            'components': []
        }

        response = Response(ogg=result)
        return response.dict()
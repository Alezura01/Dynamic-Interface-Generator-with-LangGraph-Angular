import logging
from typing import List, Optional, Type, Any, Union
from pydantic import BaseModel, Field 
from langchain.tools import BaseTool
from enum import Enum

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TypeValues(str, Enum):
    linea = "linea"
    tendina = "tendina"

class Request(BaseModel):
    nameList : str = Field(description = "Stringa che specifica il nome della lista.")
    values: List[str] = Field(description="Lista di stringhe che rappresentano gli oggetti all'interno della lista che stiamo descrivendo.")
    ordered : bool = Field(description="Un valore booleano che specifica se la lista è ordinata o non ordinata.")
    id: str = Field(description="Stringa che specifica l'id della lista")
    typology: TypeValues = Field(description = "Mostra il tipo della lista. Se il numero di elementi nella lista è maggiore di 4 allora il valore di questo campo è 'tendina'")
    required: bool = Field(description="Un valore booleano che specifica se la scelta di una delle opzioni nella lista è obbligatoria o meno.")
                                 
class Response(BaseModel):
    ogg: dict[str, Union[str|List|bool]]

class ListDefinerTool(BaseTool):
    name: str = "list_definer"
    description : str = "Utilizza questa funzione quando l'utente deve scegliere tra un finito numero di valori. La risposta della funzione è un JSON array con la descrizione della lista data da 'result', senza specificare 'ogg' iniziale."
    args_schema : Type[BaseModel] = Request

    def _run(self, nameList: str, values: List[str], ordered: bool, id: str, typology:str, required:bool) -> dict:
        logger.debug(f"Name: {nameList}, Values: {values}, Ordered: {ordered}, Id: {id}, Type: {typology}, Required:{required}")

        element = "list"
        
        value_obj = [{'values': val} for val in values]

        result = {
            'element': element,
            'name':nameList,
            'type': typology,
            'ordered': ordered,
            'id': id,
            'required':required,
            'components': value_obj
        }

        response = Response(ogg=result)
        return response.dict()

import logging
from typing import List, Type, Union
from pydantic import BaseModel, Field 
from langchain.tools import BaseTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Request(BaseModel):
    nameLabel: str = Field(description="Stringa che specifica il label del bottone.")
    idButton : str = Field(description="Stringa che specifica l'id del bottone.")
    disabled: bool = Field(description="Un valore booleano che specifica se il bottone è disabilitato.")
    
class Response(BaseModel):
    ogg: dict[str, Union[str|bool| List]]

class ButtonDefinerTool(BaseTool):
    name: str = "button_definer"
    description : str = "Utilizza questa funzione quando c'è bisogno di inserire un bottone. La risposta della funzione è un JSON array con la descrizione del bottone data da 'result', senza specificare 'ogg' iniziale."
    args_schema : Type[BaseModel] = Request

    def _run(self, idButton:str, nameLabel:str, disabled:bool) -> dict:
        logger.debug(f" Id: {idButton}, Name: {nameLabel}, Disabled: {disabled}")

        component = []
        element = 'button'

        result = {
            'element': element ,
            'id': idButton,
            'name': nameLabel,
            'disabled': disabled,
            'component': component
        }

        response = Response(ogg=result)

        return response.dict()

import logging
from typing import List, Type, Union
from pydantic import BaseModel, Field 
from langchain.tools import BaseTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Request(BaseModel):
    nameParagraph: str = Field(description="Stringa che specifica il contenuto del paragrafo")
    idParagraph : str = Field(description="Stringa che specifica l'id del paragrafo")
    
class Response(BaseModel):
    ogg: dict[str, Union[str| List]]

class DivDefinerTool(BaseTool):
    name: str = "div_definer"
    description : str = ("Utilizza questa funzione quando devi stampare un messaggio dato da un agente. Devi riportare le esatte parole dell'agente. La risposta della funzione è un JSON array con la descrizione del paragrafo data da 'result', senza specificare 'ogg' iniziale")
    args_schema : Type[BaseModel] = Request

    def _run(self, idParagraph: str, nameParagraph: str) -> dict:
        logger.debug(f" Id: {idParagraph}, Name: {nameParagraph}")

        
        element = 'div'

        result = {
            'element': element ,
            'id': idParagraph,
            'name': nameParagraph,
            'components': []
        }

        response = Response(ogg=result)

        return response

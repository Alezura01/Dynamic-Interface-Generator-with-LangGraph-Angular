import logging
from typing import List, Optional, Type, Union
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Request(BaseModel):
    nameLabel: str = Field(description="Stringa che specifica il nome del Form.")  

class Response(BaseModel):
    ogg: dict[str, Union[str| dict [str, Union[str| List]]]]

class ParentDefiner(BaseTool):
    name: str = "parent_function"
    description: str = "Utilizza questa funzione quando dobbiamo raccogliere diversi input field e liste in un form, inserendoli con un bottone all'interno del dizionario 'component' in 'result'."
    "Esempio di una risposta: '[{'element':'form','name':'Dati Personali','id':'datiPersonaliForm', 'components':[{'element':'input','type':'text','name':'Targa','id':'targaAuto','components':[]}{'element':'button','id':'bottoneInvia','name':'Invia''components':[]}]}]'" 
    "La risposta della funzione è un JSON array con la descrizione del form data da 'result', senza specificare 'ogg' iniziale."
    args_schema : Type[BaseModel] = Request

    def _run(self, nameLabel:str) -> dict:
        logger.debug(f"Name: {nameLabel}")

        component : dict[str, Union[str|List]] = {}
        element = 'form'

        result = {
            'element': element,
            'name': nameLabel,
            'components': component
        }

        response = Response(ogg=result)
        return response.dict()
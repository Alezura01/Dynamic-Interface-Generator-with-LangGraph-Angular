from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START
from langgraph.types import Command
from tools import all_tools
from config import appSet
from dotenv import load_dotenv
from fastapi import  Request
from langchain_core.messages import HumanMessage
from typing import  Literal, Annotated
from pydantic import BaseModel, Field
import json
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
import sqlite3
import uuid
from langgraph.prebuilt.chat_agent_executor import AgentState
import os
from langsmith import Client
from agentevals.graph_trajectory.llm import create_graph_trajectory_llm_as_judge


load_dotenv()
app = appSet()
llm = ChatOpenAI(model = 'gpt-4o')
client = Client()
THREAD_ID = "thread-1"
conv_end = False
config = {"configurable": {"thread_id": THREAD_ID}}

db = SQLDatabase.from_uri("sqlite:///data/database.db")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()

#Dei tools a me interessa 'sql_db_query'
sql_db_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
db_query_func = sql_db_query_tool.run

is_end=False
# ----------------------------------------------- State -------------------------

class AppState(AgentState):
    fase:int

# ------------------------------------------------------ SUPERVISOR ----------------------------------------------


class Supervisor(BaseModel):
    next: Literal["agentCasa", "agentAuto","FINISH"] = Field(
        description="Sei un agente che supervisiona tutto il processo di comunicazione tra il cliente e gli agenti specializzati nei diversi tipi di preventivi.\n"
        "Specifica il prossimo agente nella pipeline:\n"
        " 'agentCasa' quando l'utente richiede un preventivo per la sua casa; \n"
        " 'agentAuto' quando l'utente richiede un preventivo per la sua auto; \n"
        " 'FINISH' quando bisogna terminare il processo"
    )
    reason : str = Field(
        description="SOLO UNA VOLTA, quando vieni chiamato per la PRIMA volta, decidi chi sarà l'agente specializzato per eseguire la pipeline.\n"
        "Quando vieni chiamato a seguito della risposta di AgentUI, fornisci la stessa risposta di agentUI"
    )

def supervisor_node(state: AppState) -> Command[Literal["agentCasa", "agentAuto", "__end__"]]:
    system_prompt = ( '''
        Sei un supervisore che orchestra la comunicazione tra i diversi agenti specializzati e il cliente che sta chiedendo un preventivo.
        I tuoi compiti sono:
            - quando vieni chiamato per la PRIMA VOLTA, e SOLO quella volta, seleziona l'agente specializzato più adatto alla richiesta inviata dall'utente, scegliendo tra:
                1. AgentCasa : per gestire la creazione di un preventivo per case;
                2. AgentAuto : per gestire la creazione di un preventivo per auto.
              E' importante che l'agente specializzato venga deciso solo la prima volta e per una volta sola.
            - Quando vieni invocato per la SECONDA volta e ricevi la risposta da AgentUI, copia l'output prodotto da AgentUI e segnala la fine del processo con 'FINISH'.
        
        Dopo aver raggiunto 'FINISH', se ricevi nuove chiamate o richieste, devi considerarle come nuove conversazioni e ripartire da capo:  
        1. Torna a selezionare l'agente specializzato (solo una volta).  
        2. Poi attendi la risposta da AgentUI e chiudi di nuovo con 'FINISH'.
                     
        La risposta che fornisci deve essere scritta nel campo 'reason' e deve seguire le seguenti regole:                    
            - quando devi selezionare l'agente specializzato deve contenere SOLO il nome dell'agente e deve essere concorde con quello scritto nel campo 'next'. Esempio : 'AgentAuto', 'AgentCasa';
            - quando devi terminare il processo, copia la risposta di AgentUI, quindi un Array JSON con l'interfaccia Angular, senza alcune introduzioni o messaggi. Non devi copiare la risposta di altri agenti, solo quella di AgentUI.
              Esempio di risposta da fornire come output: [{"element":"form","name":"Dati Personali","id":"datiPersonaliForm","components":[{"element":"input","type":"text","name":"Targa","id":"targaAuto","components":[]},{"element":"button","id":"bottoneInvia","name":"Invia","components":[]}]}]
            - quando ricevi la risposta di AgentUI, non puoi rispondere con 'AgentCasa' o 'AgentAuto', ma solo con FINISH.
                     
        Routing Guidelines:
            1. 'AgentCasa' : SOLO LA PRIMA VOLTA per gestire la creazione di un preventivo per casa;
            2. 'AgentAuto' : SOLO LA PRIMA VOLTA per gestire la creazione di un preventivo per auto;
            3. Rispondi con 'FINISH' negli altri casi o quando ricevi la risposta di AgentUI. La tua risposta finale deve essere uguale all'output di AgentUI, senza alcuna introduzione.                     
        ''')
    
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]

    response = llm.with_structured_output(Supervisor).invoke(messages)
    
    goto = response.next
    reason = response.reason

    fase_attuale = state.get("fase",1)

    return Command(
        update = {
            "fase":fase_attuale,
            "messages": [
                HumanMessage(content=reason, name="supervisor")
            ]
        },
        goto = goto
    )

# ------------------------------------------------------ AgentCasa  ------------------------------------------------------

@tool
def run_query_tool(query:str) -> str:
    """
        Utilizza questo tool per eseguire una query SQL sul database collegato.
        Esempio di output: '[('Metri Quadri', 'numero'), ('Tipologia Abitazione', 'scelta (Appartamento, Villa, Bilocale)')]'
        Fornisci come risposta solo le informazioni risultanti dalla query, come nell'esempio.

        Le regole che devi seguire sono:
         - Quando la query non trova alcun valore, termina il tool;
         - Non duplicare le informazioni che trovi eseguendo la query;
         - Non devi modificare alcuna informazione che trovi eseguendo la query.
    """
    return db_query_func(query)



@tool
def query_preventivo_casa(state: Annotated[AppState, InjectedState]) -> Command:
    """
    Utilizza questo tool per poter scrivere una query sintatticamente corretta su un database SQL per raccogliere le informazioni da chiedere per compilare un preventivo per una casa in fasi distinte.
    La query deve essere limitata alla tabella 'preventivo_casa' e deve selezionare solo i campi 'nome_campo', 'opzioni' e 'obbligatorio' a seconda del valore di 'fase'.
    La query deve riferirsi ad un solo valore di 'fase' per volta. Il valore d'input 'fase' corrisponde al valore di 'fase' nello state AppState. Non devi inventare il valore d'input 'fase' o reimpostarla ad 1, devi usare quello che ti arriverà in 1.
    """

    fase= state.get("fase",0)
    query_template = "SELECT nome_campo, opzioni, obbligatorio FROM preventivo_casa WHERE fase = {fase}"
    return query_template.format(fase=fase)

@tool
def ending_greetings(riepilogo: str, ringraziamento:str)->str:
    """
    Utilizza questo tool quando devi RINGRAZIARE per aver fornito le informazioni e annunciare il termine delle operazioni.
    L'output deve contenere questi due elementi:
     - un messaggio di ringraziamento, ad esempio 'Grazie per aver fornito i dati richiesti.';
     - un riepilogo dei dati inseriti, ad esempio "Nome: Mario; Cognome: Rossi".
    """
    global conv_end, is_end
    is_end = True
    conv_end = True
    return riepilogo + ringraziamento

def agentCasa_node(state: AppState) -> Command[Literal["agentUI"]]:
    
    """
        Sei un assistente che, in diverse fasi, chiede le informazioni necessarie per poter scrivere un preventivo per una casa.
    """

    agentCasa_agent = create_react_agent(
        llm,
        tools=[ query_preventivo_casa, run_query_tool, ending_greetings],
        prompt=("""
            Sei un agente specializzato nei preventivi per case, il cui compito consiste nel raccogliere e chiedere le informazioni necessarie all'utente.
            Tramite i tool che ti sono stati assegnati, raccogli le informazioni necessarie dal database SQL assegnato.
            
            Quando vieni chiamato devi SEMPRE utilizzare i seguenti due tool:
                1. il tool 'query_preventivo_casa' per interagire con il database e generare la query per raccogliere le informazioni da chiedere. Devi eseguire questo tool solo per una fase alla volta. Preleva la fase dall'input dell'invocazione;
                2. eseguire la query tramite il tool 'run_query_tool', fornendo come risposta le informazioni da chiedere all'utente.
                
            Il tool 'ending_greetings' viene utilizzato SOLO SE 'run_query_tool' ha fornito come risposta '', non può essere utilizzato se 'run_query_tool' non è stato chiamato. Il tool è utilizzato per ringraziare l'utente per aver fornito le informazioni.
            
            Ogni tool può essere utilizzato una volta sola durante il processo.
                
            La risposta che fornirai potrà essere:
                - il risultato della query, fornito dal tool 'run_query_tool', senza alcuna introduzione;
                - un ringraziamento con il riepilogo, fornito da 'ending_greetings', dovuto alla conclusione del processo.
            Fornisci le risposte dirette, evita le introduzioni.
          """),
          state_schema= AppState
    )
    global is_end

    fase_attuale = state.get("fase",1)
    message_attuale = state["messages"]

    result = agentCasa_agent.invoke({
        "messages": message_attuale,
        "fase": fase_attuale
    })

    #Per gestire la fase
    if is_end:
        fase_attuale = 1
    else:
        fase_attuale += 1

    return Command(
        update = {
            "fase": fase_attuale,
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="agentCasa")
            ]
        },
        goto = "agentUI"
    )

# ------------------------------------------------------ AgentAuto  ------------------------------------------------------



@tool
def query_preventivo_auto(state: Annotated[AppState, InjectedState]) -> Command:
    """
    Utilizza questo tool per poter scrivere una query sintatticamente corretta su un database SQL per raccogliere le informazioni da chiedere per compilare un preventivo per un auto in fasi distinte.
    La query deve essere limitata alla tabella 'preventivo_auto' e deve selezionare solo i campi 'nome_campo', 'opzioni' e 'obbligatorio' a seconda del valore di 'fase'.
    La query deve riferirsi ad un solo valore di 'fase' per volta. Il valore d'input 'fase' corrisponde al valore di 'fase' nello state AppState. Non devi inventare il valore d'input 'fase' o reimpostarla ad 1, devi usare quello che ti arriverà in 1.
    """
    fase= state.get("fase",0)
    query_template = "SELECT nome_campo, opzioni, obbligatorio FROM preventivo_auto WHERE fase = {fase}"
    return query_template.format(fase=fase)


def agentAuto_node(state: AppState) -> Command[Literal["agentUI"]]:

    """
        Sei un assistente che, in diverse fasi, chiede le informazioni necessarie per poter scrivere un preventivo per un auto.
    """

    agentAuto_agent = create_react_agent(
        llm,
        tools=[ query_preventivo_auto, run_query_tool, ending_greetings],
        prompt = ("""
            Sei un agente specializzato nei preventivi per auto, il cui compito consiste nel raccogliere e chiedere le informazioni necessarie all'utente.
            Tramite i tool che ti sono stati assegnati, raccogli le informazioni necessarie dal database SQL assegnato.
            
            Quando vieni chiamato devi SEMPRE utilizzare i sguenti due tool:
                1. il tool 'query_preventivo_auto' per interagire con il database e generare la query per raccogliere le informazioni da chiedere. Devi eseguire questo tool solo per una fase alla volta. Preleva la fase dall'input dell'invocazione;
                2. eseguire la query tramite il tool 'run_query_tool', fornendo come risposta le informazioni da chiedere all'utente.
                
            Il tool 'ending_greetings' viene utilizzato SOLO SE 'run_query_tool' ha fornito come risposta '', non può essere utilizzato se 'run_query_tool' non è stato chiamato. Il tool è utilizzato per ringraziare l'utente per aver fornito le informazioni.

            Ogni tool può essere utilizzato una volta sola durante il processo.
            
                
            La risposta che fornirai potrà essere:
                - il risultato della query, senza alcuna introduzione,  fornito dal tool 'run_query_tool', senza alcuna introduzione;
                - un ringraziamento con il riepilogo, fornito da 'ending_greetings', dovuto alla conclusione del processo.
            Fornisci le risposte dirette, evita le introduzioni.
            """),
            state_schema=AppState
    )
    
    global is_end

    fase_attuale = state.get("fase",1)
    message_attuale = state["messages"]

    result = agentAuto_agent.invoke({
        "messages": message_attuale,
        "fase": fase_attuale
    })

    if is_end:
        fase_attuale = 1
    else:
        fase_attuale += 1

    return Command(
        update = {
            "fase": fase_attuale,
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="agentAuto")
            ]
        },
        goto = "agentUI"
    )

#  ------------------------------------------------------ AgentUI  ------------------------------------------------------


def agentUI_node(state: AppState) -> Command[Literal["supervisor"]]:
    """
        Risponde con la descrizione dell'interfaccia UI Angular basandosi sulle informazioni che l'agente precedente sta richiedento. 
        Il risultato viene scritto in un array JSON su una riga sola senza alcuna introduzione.
        Esempio: [{\"element\":\"form\",\"name\":\"Dati Personali\",\"id\":\"datiPersonaliForm\",\"components\":[{\"element\":\"input\",\"type\":\"text\",\"name\":\"Targa\",\"id\":\"targaAuto\",\"components\":[]},{\"element\":\"button\",\"id\":\"bottoneInvia\",\"name\":\"Invia\",\"components\":[]}]}]
    """

    agentUI_agent = create_react_agent(
        llm,
        tools = all_tools,
        prompt = "Il tuo compito è generare interfacce UI in Angular sulla base della risposta ricevuta dall'agente precedente. \n"
            "La risposta che fornirai sarà data dai diversi tool che utilizzerai.\n"
            "Devi rispettare le seguenti regole:\n"
            "1.Il risultato non devono essere i parametri dei tool utilizzati;\n"
            "2.La risposta deve essere un array JSON scritto su una sola riga.\n"
            "3.Quando devi mostrare un messaggio e non chiedere informazioni, utilizza 'DivDefinerTool' ;\n"
            "4.Quando devi mostrare un riepilogo, utilizza 'TableDefinerTool' per mostrare i dati;"
            "5.Quando devi creare più di un input, racchiudilo all'interno di un form utilizzando il tool 'ParentDefiner' e inserisci anche un bottone utilizzando 'ButtonDefiner';"
            "Esempio di risposta: [{\"element\":\"form\",\"name\":\"Dati Personali\",\"id\":\"datiPersonaliForm\",\"components\":[{\"element\":\"input\",\"type\":\"text\",\"name\":\"Targa\",\"id\":\"targaAuto\",\"components\":[]},{\"element\":\"button\",\"id\":\"bottoneInvia\",\"name\":\"Invia\",\"components\":[]}]}]"
            "6.Quando c'è una spiegazione oltre agli input, devi mostrarla tramite 'DivDefinerTool' all'interno del form. Il div non deve contenere i dati inseriti nell'input.\n"
            "Esempio: [{\"element\":\"form\",\"name\":\"Dati Personali\",\"id\":\"datiPersonaliForm\",\"components\":[{\"element\":\"div\",\"id\":\"spiegazioneInfo\",\"name\":\"E' importante fornire info.\",\"components\":[]}{\"element\":\"input\",\"type\":\"text\",\"name\":\"Targa\",\"id\":\"targaAuto\",\"components\":[]},{\"element\":\"button\",\"id\":\"bottoneInvia\",\"name\":\"Invia\",\"components\":[]}]}]"
            "7. Quando c'è un messaggio di ringraziamento con un riepilogo, mostrare con 'DivDefinerTool' il messaggio e con 'TableDefinerTool' il riepilogo."
            "8. Quando devi utilizzare il tool 'InputFormDefiner' deduci il tipo dell'informazione. Se il valore di 'obbligatorio' è 1 allora required sarà True, altrimenti False. "
            "9. Quando devi utilizzare il tool 'ListDefinerTool' e hai più di 3 opzioni, applicare la tipologia tendina. Se il valore di 'obbligatorio' è 1 allora required sarà True, altrimenti False."          
        )
    
    result = agentUI_agent.invoke(state)

    return Command(
        update={
            "fase": state.get("fase",1),
            "messages": [ 
                HumanMessage(
                    content=result["messages"][-1].content,  
                    name="agentUI"  
                )
            ]
        },
        goto="supervisor", 
    )

#  ------------------------------------------------------ Grafo   ------------------------------------------------------

graph = StateGraph(AppState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("agentCasa", agentCasa_node)
graph.add_node("agentAuto", agentAuto_node)
graph.add_node("agentUI", agentUI_node)

graph.add_edge(START, "supervisor")
graph.add_edge("agentUI", "supervisor")

#Variabile d'ambiente per scegliere se usare o meno il checkpoint (quindi se farlo partire da FE o da Langgraph Studio)
use_custom_checkpoint = os.getenv("USE_CUSTOM_CHECKPOINT", "true").lower() == "true"

if use_custom_checkpoint:
    checkpointer = InMemorySaver()
    workflow = graph.compile(checkpointer=checkpointer)
else:
    workflow = graph.compile()

#  ------------------------------------------------------ Mettiamo in moto  ------------------------------------------------------
import pprint

@app.post("/")
async def genera_preventivo(request: Request):
    global THREAD_ID, conv_end, config

    dati = await request.json()
    messaggio_utente = dati.get("content")
    nuovi_dati = dati.get("dati_form")

    if isinstance(nuovi_dati, dict) and nuovi_dati:
        input_messaggio = json.dumps(nuovi_dati, ensure_ascii=False)
    else:
        input_messaggio = messaggio_utente

    print("Input per la comunicazione", input_messaggio)

    inputs = {
        "messages": [ ("user", input_messaggio)]
    }

    if conv_end:
        THREAD_ID = f"thread-{uuid.uuid4().hex}"
        conv_end = False

    config["configurable"]["thread_id"] = THREAD_ID

    result = None
    for event in workflow.stream(inputs, config):
        for key, value in event.items():
            if value is None:
                continue
            last_message = value.get("messages", [])[-1] if "messages" in value else None
            if last_message:
                pprint.pprint(f"Output from node '{key}':")
                pprint.pprint(last_message, indent=2, width=80, depth=None)
                print()
                result = last_message

    return {"result": result.content}
    

if __name__ == "__main__":
     import uvicorn
     uvicorn.run("backend:app", host="0.0.0.0", port=2024, reload=True)

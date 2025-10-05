from agentevals.graph_trajectory.llm import create_graph_trajectory_llm_as_judge
from agentevals.graph_trajectory.strict import graph_trajectory_strict_match
from langsmith import Client
from dotenv import load_dotenv
import json
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate 


load_dotenv()
client = Client()

#Run di un'esecuzione corretta
run_id = ['1c17b625-c354-455c-8b50-583180de8f75']


run_evaluated = client.list_runs(id = run_id)
run = next(run_evaluated)


# ---------------------- REFERENCE_TRAJECTORY -------------------
reference_trajectory_casa = {
    "inputs": run.inputs,
    "results" : [],
    "steps" : [['__start__', 'supervisor', 'agentCasa', 'agentUI', 'supervisor']]
}

reference_trajectory_auto = {
    "inputs": run.inputs,
    "results" : [],
    "steps" : [['__start__', 'supervisor','agentAuto', 'agentUI', 'supervisor']]
}

reference_trajectory_errata = {
    "inputs": [],
    "results" : [{'messages': [{'role': 'user', 'name': 'supervisor', 'content': 'Non è disponibile'}]}],
    "steps" : [['__start__','agentProva', 'agentRisposta', '__end__']]
}

# ---------------------- GRAPH TRAJECTORY LLM-AS-JUDGE (dovrebbe dare RISULTATO ERRATO) -------------------

evaluator_llm = create_graph_trajectory_llm_as_judge(
    model = "gpt-4o")

res_llm_errato = evaluator_llm(
    inputs = run.inputs,
    outputs = run.outputs,
    reference_outputs = reference_trajectory_errata
)

print("Test traiettoria llm-as-judge (il risultato dovrebbe essere errato, ma risulta corretto)", res_llm_errato)

# ---------------------- GRAPH TRAJECTORY LLM-AS-JUDGE (RISULTATO CORRETTO) -------------------
res_llm = evaluator_llm(
    inputs = run.inputs,
    outputs = run.outputs,
    reference_outputs = reference_trajectory_casa
)

print("Test traiettoria llm-as-judge (Risultato CORRETTO)", res_llm)

# ------------------------- GRAPH TRAJECTORY STRICT MATCH --------------------


#Se volessimo testare una run con input 'preventivi per auto' si dovrebbe cambiare la reference trajectory, altrimenti il risultato sarebbe errato
res_strict = graph_trajectory_strict_match(
    outputs = run.outputs,
    reference_outputs= reference_trajectory_casa
)

print("Test traiettoria strict match (Corretto)", res_strict)

# ------------------------- GRAPH TRAJECTORY STRICT MATCH (Risultato: False) --------------------


res_strict_false = graph_trajectory_strict_match(
    outputs = run.outputs,
    reference_outputs= reference_trajectory_errata
)

print("Test traiettoria strict match (Errato)", res_strict_false)

# ---------------------- LLM-AS-JUDGE con Prompt ------------------------------------------------


prompt_template = ChatPromptTemplate([
    ("system", """
        Sei un esperto valutatore di agenti AI, il cui compito è valutare la correttezza della traiettoria fatta nella run fornita in risposta ad una query utente.
    In base alla tua valutazione dovrai fornire uno score, che potrà essere True o False.
    Non devi inventare la run o gli output, devi utilizzare quelli che ti verrà indicata dall'user prompt.

    <Instructions>
        Dovrai valutare:
        1. se gli step eseguiti sono UGUALI, in NUMERO e in NOME, a quelli della traiettoria di riferimento;
        2. se la traiettoria ha un senso logico tra i passaggi;
        3. se la traiettoria è efficiente.

        Lo score sarà 'True' quando tutti i criteri sono soddisfatti, altrimenti sarà 'False'.
        La tua risposta non deve contenere introduzioni, ma solamente lo score e la motivazione per quel punteggio.
    </Instructions>
        """),
    ("user", """
        La run da valutare è : {{run}}.
        L'output da valutare è: {{outputs}}.
        La traiettoria di riferimento è: {{reference_trajectory}}.
    """)
])

examples_prova = [
    {"inputs": [],
     "outputs": {"results" : [],
    "steps" : [['__start__', 'supervisor','agentAuto', 'agentUI', 'supervisor']]},
    "score": "True"
    },
    {"inputs": [],
     "outputs": {"results" : [],
    "steps" : [['__start__','agentProva', 'agentRisposta', '__end__']]},
    "score": "False"
    },
    {"inputs": [],
     "outputs": {"results" : [],
    "steps" : [['__start__', 'supervisor','agentCasa', 'agentUI', 'supervisor']]},
    "score": "True"
    },
    {"inputs": [],
     "outputs": {"results" : [],
    "steps" : [['__start__', 'supervisor','agentUI', 'agentCasa', 'supervisor']]},
    "score": "False"
    },
]


prompt_filled = prompt_template.format(
    run=run.id,
    outputs=json.dumps(run.outputs, indent=2),
    reference_trajectory=json.dumps(reference_trajectory_auto['steps'], indent=2)
)

evaluator_llm = create_graph_trajectory_llm_as_judge(
    model = "gpt-4o",
    prompt = prompt_filled,
    few_shot_examples= examples_prova,
)

res_llm = evaluator_llm(
    inputs = run.inputs,
    outputs = run.outputs,
    run=run.id,
    reference_trajectory=reference_trajectory_auto
)

print("Test LLM-AS-JUDGE con prompt", res_llm)




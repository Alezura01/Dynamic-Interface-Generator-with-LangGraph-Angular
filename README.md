# Thesis-project: Dynamic Interface Generator with LangGraph + Angular

## About the project
### Description
This project consists of a multi-agent system that, through the work of its agents, generates insurance quotes based on user input. <br>
The architecture is represented in the following picture.

![Architecture of the system](https://github.com/Alezura01/Dynamic-Interface-Generator-with-LangGraph-Angular/blob/main/Architettura.png?raw=true)

At the moment, the project supports two types of quotes: **car** and **home**.

## Trajectory
According to the type of quote, the *supervisor*, the orchestrator of the communication between the user and the agents, will delegate the conversation to the specialized agent.<br>
The *specialized agent* queries the back-end database and, using its associated tools, extracts the information to ask to the user.<br>
The *agentUI*, through its own tools, generates the ‘skeleton’ of the form to be displayed to the user.<br>
The supervisor, then, forwards it to the front-end as a JSON array. The front-end parses the array and builds the interface using Angular Material components.<br>

## Structure of the project
The application consists of:
- a back-end built with **LangGraph** and connected to the front-end with **FastAPI**;
- a front-end built with **Angular**.

### Structure of the back-end
The structure of the *back-end* consists of:
- **toolsFolder** → contains all the tools used by AgentUI, collected then in a list inside tools.py
- **dataset.py** → creates the dataset with the examples used for the evaluations;
- **preventivi.sql** → defines the database tables containing the information to request to the user, specifying the type and the order of the questions;
- **test.py** → contains the evaluators to judge the trajectory of the system.

### Structure of the front-end
The structure of the *front-end* consists of:
- **components** → a folder that includes Angular Material components (button, input field, list and table);
    - **fieldset** → groups multiple input fields, in case a form contains a nested form;
    - **form** → builds the final form to display to the user;
- **dynamic-response** → displays the form generated from the components;
- **home** → contains the initial landing page.

## Built with
- Python (version 3.11.0)
- LangChain (version 0.3.25)
- LangGraph (version 0.4.2)
- Angular (version 19.2.10)

## Environment configuration
1. Clone the repository
``` 
git clone https://github.com/Alezura01/Dynamic-Interface-Generator-with-LangGraph-Angular.git
cd chatbot-ui 
```
2. Create a virtual environment
```
python -m venv venv
venv\Scripts\activate
```

3. Install the requirements
``` pip install -r requirements.txt ```

## Run the project
### Run the project on browser

To run the application on **browser**:
1. Start the back-end by running `` python back-end.py `` ;
2. Start the front-end by running  `` ng serve `` ;
3. Open in the browser (http://localhost:4200) to interact with the application.

### Run the project on LangGraph Studio
To run the application on **LangGraph Studio**:
1. Start the back-end and change the value of the environment variable *'USE_CUSTOM_CHECKPOINT'* by running: 
```
export USE_CUSTOM_CHECKPOINT = false
langgraph dev
``` 
2. LangGraph Studio will automatically open on browser;
3. Set the value of *'fase'* as 1 and write your request on *'messages'*.

If you want to continue the communication, increase the value of *'fase'* by 1 and write the requested information in a dictionary, specifying the keys and the values.
The keys correspond to the field name of the tables that you can find inside 'preventivi.sql'. <br>
An example of message to write is:
``` 
{'Tipologia Macchina':'Suv', 'Targa':'as234ds', 'Cilindrata':'1000'}
 ```


### Run the evaluators

To run **the evaluators**, execute in the back-end  `` python test.py `` 

## Other features
It’s possible to change the style of the entire front-end without modifying the CSS-file of each component.

1. Upload the css file inside the folder **‘assets/styles’**. Each selector of the file must specify the selector name and the element of the component that is being modified;
2. Change the value of the variable *‘href’* inside the file **‘theme.service.ts’**

## Future works
Some future works proposed for the project could be:

- adding the possibility to handle the status of the button (disabled or not) through the AI system, in such a way the button will be activated only when all the fields have been filled.;
- trying to make the system faster by using other LLM models;
- to use other evaluators, pre-built or customized, to evaluate other parts of the graph, or by using LLM-as-judge evaluators with prompts.
- trying to have more accurated results by improving the agents' prompt dividing it in system and human part.

import logging

import sys
from langchain import hub
from langchain.memory import ConversationBufferWindowMemory

from tools import listen_tool, generatemixtape_tool, followup_tool
from langchain.agents import initialize_agent, AgentExecutor, load_tools
import yaml
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, create_structured_chat_agent, create_react_agent, \
    create_json_chat_agent

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

n = len(sys.argv)
userInput = ""
if n > 1:
    for i in range(1, n):
        userInput += sys.argv[i] + " "
else:
    userInput = "Make a mixtape " + input('''Make a mixtape ''')

# Construct the agent. We will use the default agent type here.
tools = [listen_tool, generatemixtape_tool, followup_tool]

# , model=config["model"]
llm = ChatOpenAI(temperature=0)  # , model="gpt-4")

impersonification = '''
Your task is to chat with the Human in order to get mixtape details, create a mixtape and write it to spotify. 
Create a refined version of the mixtape after every user input and show the user the result. 
Add some followup questions in order to get a more detailed description of the mixtape you have to create. Do it even if you already generated a mixtape.
Write the mixtape to spotify only if the user confirms it. 
'''
# Explain the user why
# Remember the Human that can ask for modification of the playlist and ask followup questions.
# tools_prompt = """ You have access to the following tools:"""
system_1 = """
You have access to the following tools:
{tools}
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:
```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```
Follow this format:
Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. 
Format is Action:```$JSON_BLOB```then Observation
"""

human_template = """
 {input}
{agent_scratchpad} 
(reminder to respond in a JSON blob no matter what)
 """

system_2 = """"
TOOLS
------
You have access to the following tools:
{tools}

RESPONSE FORMAT INSTRUCTIONS
----------------------------
When responding to me, please output a response in one of two formats:
**Option 1:**
Use this if you want the human to use a tool.
Markdown code snippet formatted in the following schema:
```json
{{
    "action": string, \ The action to take. Must be one of {tool_names}
    "action_input": string \ The input to the action
}}
```

**Option #2:**
Use this if you want to respond directly to the human. Markdown code snippet formatted in the following schema:
```json
{{
    "action": "Final Answer",
    "action_input": string \ You should put what you want to return to use here
}}
```
"""

human_template_2 = """
USER'S INPUT
--------------------
Here is the user's input (remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else):
{input}
"""

# prompt = hub.pull("hwchase17/structured-chat-agent")
# print(prompt)
# print(type(prompt))
# agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)


from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

myTmplate = ChatPromptTemplate.from_messages([
    #
    ("system", impersonification + system_2),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", human_template_2),
    MessagesPlaceholder("agent_scratchpad")
])
print(myTmplate)
print(type(myTmplate))
agent = create_json_chat_agent(llm=llm, tools=tools, prompt=myTmplate)

# Create the memory object
memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=3,
    return_messages=True,
    input_key="input",
    output_key="output"
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory,
                               return_intermediate_steps=True)

while True:
    if userInput == "exit":
        exit()
    else:
        logger.info("invoke the agent")
        response = agent_executor.invoke({"input": userInput})
        userInput = input(response["output"])

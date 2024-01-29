import logging

import sys
from langchain import hub
from tools import listen_tool, generatemixtape_tool, followup_tool
from langchain.agents import initialize_agent, AgentExecutor, load_tools
import yaml
from langchain_openai import OpenAI
from langchain.agents import create_openai_functions_agent, create_structured_chat_agent

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
llm = OpenAI(temperature=0)

impersonification = '''
Your task is to work with the Human to create a mixtape and write it to spotify. 
Ask followup questions to the Human in response, in order to get a more detailed description of the mixtape you have to create. 
Create a refined version of the mixtape after every user input and show the user the result. 
Use the tool to write the mixtape to spotify only when the user asks for it. 
'''
# Explain the user why
# Remember the Human that can ask for modification of the playlist and ask followup questions.
# tools_prompt = """ You have access to the following tools:"""
agent_init = """
Respond to the human as helpfully and accurately as possible. You have access to the following tools:
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
human_template="""
 {input}
{agent_scratchpad} 
(reminder to respond in a JSON blob no matter what)
 """

prompt = hub.pull("hwchase17/structured-chat-agent")
print(prompt)
print(type(prompt))
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)


from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

myTmplate = ChatPromptTemplate.from_messages([
    #impersonification
    ("system", agent_init),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", human_template)
])
print(myTmplate)
print(type(myTmplate))
agent_2 = create_structured_chat_agent(llm=llm, tools=tools, prompt=myTmplate)

agent_executor = AgentExecutor(agent=agent_2, tools=tools, verbose=True, handle_parsing_errors=True)

while True:
    if userInput == "exit":
        exit()
    else:
        logger.info("invoke the agent")
        response = agent_executor.invoke({"input": userInput})
        print(response)
        userInput = input("")

import logging

import sys
from langchain.memory import ConversationBufferWindowMemory

from tools import listen_tool, generatemixtape_tool, followup_tool
from langchain.agents import AgentExecutor
import yaml
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

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

logger.info(userInput)

tools = [listen_tool, generatemixtape_tool, followup_tool]

if config["model"]:
    model = config["model"]
else:
    model = "gpt-3.5-turbo"
logger.info("Model used: " + model)
llm = ChatOpenAI(temperature=0, model=model)

impersonification = '''
You are MusicMille, an expert music lover and with excellent emphatic skills.
Your task is to chat with the User in order to get mixtape details, create a mixtape and write it to spotify. 
Always ask some at least one creative followup question in order to get a more detailed description of the mixtape you have to create. Do it even if you already generated a mixtape.
Create a refined version of the mixtape after every user input and show the user the result. 
Write the mixtape to spotify only if the user confirms it. 
'''

human_template = """
{input}
{agent_scratchpad} 
"""

prompt = ChatPromptTemplate.from_messages([
    #
    ("system", impersonification),  # +system
    MessagesPlaceholder("chat_history", optional=True),
    ("human", human_template),
    MessagesPlaceholder("agent_scratchpad")
])

chat_history = MessagesPlaceholder(variable_name="chat_history")

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=3,
    return_messages=True,
    input_key="input",
    output_key="output"
)

agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory,
                               return_intermediate_steps=True)

while True:
    if userInput == "exit":
        exit()
    else:
        logger.info("invoke the agent")
        response = agent_executor.invoke({"input": userInput})
        # response= agent_chain.invoke({"input": userInput})
        userInput = input(response["output"])

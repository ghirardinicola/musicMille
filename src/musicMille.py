import logging

import sys
import os
from tools import listen_tool, generatemixtape_tool, followup_tool
from langchain.agents import ConversationalAgent, initialize_agent, AgentExecutor, load_tools
import yaml
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import create_openai_functions_agent, create_react_agent

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
tools_names = [listen_tool, generatemixtape_tool, followup_tool]

memory = ConversationBufferMemory(memory_key="chat_history")
# , model=config["model"]
llm = OpenAI(temperature=0)

impersonification = '''
Your task is to work with the Human to create a mixtape and write it to spotify. 
Ask followup questions to the Human in response, in order to get a more detailed description of the mixtape you have to create. 
Create a refined version of the mixtape after every user input and show the user the result. 
Use the tool to write the mixtape to spotify only when the user asks for it. 
'''
#Explain the user why
#Remember the Human that can ask for modification of the playlist and ask followup questions.
#tools_prompt = """ You have access to the following tools:"""
suffix = """

{chat_history}
 {input}
{agent_scratchpad}"""

#create_react_agent()

prompt = ConversationalAgent.create_prompt(
    tools_names,
    prefix=impersonification,# + tools_prompt,
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"]
)

llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
agent = ConversationalAgent(llm_chain=llm_chain, verbose=True, return_intermediate_steps=True)
agent_executor = AgentExecutor(agent=agent, tools=tools_names, verbose=True, memory=memory)

while True:
    if userInput == "exit":
        exit()
    else:
        logger.info("invoke the agent")
        response = agent_executor.invoke({"input": userInput})
        userInput = input(response["output"])

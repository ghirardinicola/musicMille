import logging

import sys
import openai
import os
from tools import listen_tool, generatemixtape_tool, followup_tool
import openai
from langchain.agents import ConversationalAgent, Tool, AgentExecutor
from tools import llm
import yaml
from langchain import OpenAI, LLMChain
from langchain.chains.conversation.memory import ConversationBufferMemory


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

openai.api_key = config["open_api_api_key"]
os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]


n = len(sys.argv)
userInput=""
if n>1:
    for i in range(1, n):
        userInput+=sys.argv[i] + " "
else:
    userInput = "Make a mixtape " + input('''Make a mixtape ''')


# Construct the agent. We will use the default agent type here.
tools=[listen_tool, generatemixtape_tool, followup_tool]

memory = ConversationBufferMemory(memory_key="chat_history")
llm=OpenAI(temperature=0.7)

impersonification='''
Your task is to work with the Human to create a mixtape and write it to spotify. 
Then always ask followup questions to the Human in order to get a more detailed description of the mixtape you have to create. 
Create a new version of the mixtape after the Human response and write to spotify.
Always use the tool to write the mixtape to spotify.
Remember the Human that can ask for modification of the playlist and ask followup questions.
'''

tools_prompt=""" You have access to the following tools:"""
suffix = """Make a mixtape... "

{chat_history}
Question: {input}
{agent_scratchpad}"""

prompt = ConversationalAgent.create_prompt(
    tools, 
    prefix=impersonification+tools_prompt, 
    suffix=suffix, 
    input_variables=["input", "chat_history", "agent_scratchpad"]
)

llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt,verbose=True)
agent = ConversationalAgent(llm_chain=llm_chain, tools=tools, verbose=True, return_intermediate_steps=True)
agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)

while True:
    if userInput=="exit":
        exit()
    else:   
        response=agent_chain.run(input=userInput)
        userInput=input("")

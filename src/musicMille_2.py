import logging

import sys
import os
from tools import listen_tool, generatemixtape_tool, followup_tool
from langchain.agents import ConversationalAgent, initialize_agent, load_tools
from langchain.agents import AgentExecutor, create_structured_chat_agent

import yaml
from langchain.chains import LLMChain
from langchain_openai import OpenAI
# from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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

tools = [listen_tool, generatemixtape_tool, followup_tool]

# memory = ConversationBufferMemory(memory_key="chat_history")
# , model=config["model"]
llm = OpenAI(temperature=0)

impersonification = '''
Your are MusicMille. Your task is to chat with the User to create a mixtape and then write it to spotify. 
Ask some followup questions to the User in order to get a more detailed description of the mixtape you have to create. 
Create a new version of the mixtape after the Human responses.
Use the tool to write the mixtape to spotify, after the user confirm it.
Remember the Human that can ask for modification of the playlist and ask followup questions.
'''

# tools_prompt = """ You have access to the following tools:"""
# {chat_history}
request = """Make a mixtape  {input} """

# final_input = impersonification + " This is user input " + request

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            impersonification,
        ),
        ("user", request),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# prompt = ConversationalAgent.create_prompt(
#     tools_names,
#     prefix=impersonification + tools_prompt,
#     suffix=suffix,
#     input_variables=["input", "chat_history", "agent_scratchpad"]
# )

# llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

from langchain import hub
obj = hub.pull("hwchase17/structured-chat-agent")

# Construct the JSON agent
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)
# agent = ConversationalAgent(llm_chain=llm_chain, verbose=True, return_intermediate_steps=True)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)  # memory=memory

# while True:
#     if userInput == "exit":
#         exit()
#     else:
#         logger.info("invoke the agent")
#         response = agent_executor.invoke({"input": userInput} , "chat_history": [
#             HumanMessage(content="hi! my name is bob"),
#             AIMessage(content="Hello Bob! How can I assist you today?"),
#         ],)
#         userInput = input("")

import logging
from spotify import renew_mixtape

import sys
import openai
import os
from tools import listen_tool, generatemixtape_tool, followup_tool
import openai
from langchain.agents import initialize_agent
from tools import llm
import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

openai.api_key = config["open_api_api_key"]
os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]


n = len(sys.argv)
mixtape_desc=""
if n>1:
    for i in range(1, n):
        mixtape_desc+=sys.argv[i] + " "
else:
    mixtape_desc = input('''I am here to help you to create a mixtape.
    Ask me!
    ''')


# Construct the agent. We will use the default agent type here.
tools=[listen_tool, generatemixtape_tool, followup_tool]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
#ßagent = initialize_agent(tools, llm, agent="conversational-react-description", verbose=True)


impersonification='''You are a personal coach AI, expert in music and compilations.
Your task is to work with the user to create a mixtape and write it to spotify.
You think the best way to create a mixtape together is to create it having as input the original request and ask followup questions in order to stimulate the user to tweak the intermediate reasoning giving additional and more detailed inputs.
It'a also very important to make the user listen what you produced together in order to tweak it iteratively (more of this, less of that, don't use that).
Your final task is always to create the mixtape produced on spotify.'''

agent.run(impersonification + mixtape_desc)
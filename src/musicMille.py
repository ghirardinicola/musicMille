import logging
from spotify import renew_playlist

import sys
import openai
import os
from tools import convert2json_tool, generatePlaylist_tool, followup_tool
import openai
from langchain.llms import OpenAI
from langchain.agents import ConversationalAgent, ZeroShotAgent, AgentExecutor, initialize_agent
from langchain.chains import LLMChain
from tools import llm
import json
import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

openai.api_key = config["open_api_api_key"]
os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]


n = len(sys.argv)
playlist_desc=""
if n>1:
    for i in range(1, n):
        playlist_desc+=sys.argv[i] + " "
else:
    playlist_desc = input('Create a mixtape ')


# Construct the agent. We will use the default agent type here.
tools=[convert2json_tool, generatePlaylist_tool, followup_tool]


#
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
playlist_json_string=agent.run('Create a mixtape ' +  playlist_desc + '''.
Ask the user followup question in order to get additional details about the mixtape parameters. 
Then convert to a valid json array representing the songs. 
Use MUST use ONLY the valid json as final response''')

logger.debug(playlist_json_string)
playlist_obj= json.loads(playlist_json_string)


for song in playlist_obj:
    print(song) 

renew_playlist(playlist_obj)

logger.info("The music_mille0 playlist is on your spotify account!")
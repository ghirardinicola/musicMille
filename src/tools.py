import os
import yaml
from gpt import build_templates
from langchain.agents import Tool
from spotify import renew_mixtape
from langchain_openai import OpenAI
from langchain.chains import LLMChain
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

os.environ["OPENAI_API_KEY"] = config["open_api_api_key"]

llm = OpenAI(temperature=0, max_tokens=512)


def string2List(string):
    songs = []
    lines = string.split(";")
    logger.debug(len(lines))
    for line in lines:
        if line != "":
            values = line.split(",")
            songs.append({
                "song": values[0].replace('"', ""),
                "artist": values[1]
            })
    return songs


def writemixtapeInSpotify(mixtapeListStr):
    logger.debug("input:" + mixtapeListStr)
    mixtapeList = string2List(mixtapeListStr)
    renew_mixtape(mixtapeList)
    return "The music_mille0 mixtape is on your spotify account!"


listen_tool = Tool(
    name="writemixtapeInSpotify",
    func=writemixtapeInSpotify,
    description='''useful to write a mixtape on Spotify in order to make the user listen to it.
    The input to this tool should be something like:
    "The Scientist", "Coldplay"; "Don't Stop Me Now", "Queen"
    '''
)

main_prompt_template, follow_up_template = build_templates()

main_request_template = LLMChain(llm=llm, prompt=main_prompt_template)
questions_template = LLMChain(llm=llm, prompt=follow_up_template)

generatemixtape_tool = Tool(
    name="generateMixtape",
    func=main_request_template.run,
    description='''
    useful for when you have to create a mixtape. 
    The output is the mixtape
    The input should be all the user request and the previous generated mixtape, if there is one.
    ''',
)

followup_tool = Tool(
    name="generateFollowup",
    func=questions_template.run,
    description='''useful for when you have to generate followup questions in order to better understand the user input, asking details.
    If the prompt is "Make a mixtape for me for my working afternoon bla bla. ble blu."
    the input should be a string like "Make a mixtape for me for my working afternoon bla bla. ble blu."
    The output are the followup questions
    ''',
)

if __name__ == "__main__":
    # with open('config.yaml', 'r') as file:
    #     config = yaml.safe_load(file)

    # openai.api_key = config["open_api_api_key"]
    # os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]

    # llm = OpenAI(temperature=0)
    # prompt="Ok, let's listen it!"
    # mixtape="Mixtape: 1: a, 2: b."
    # # Construct the agent. We will use the default agent type here.
    # agent = initialize_agent([convert2json_tool], llm, agent="zero-shot-react-description", verbose=True)

    # agent.run(mixtape + prompt)
    sl = string2List('''"Code Monkey", "Jonathan Coulton"
    "The Scientist", "Coldplay"
    "I'm Shipping Up To Boston", "Dropkick Murphys"
    "Eye of the Tiger", "Survivor"
    "Immigrant Song", "Led Zeppelin"''')
    print("mixtapeList: {}".format(' '.join(map(str, sl))))
    renew_mixtape(sl)

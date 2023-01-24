import openai
import os
import yaml
from gpt import build_templates, json_convert_template
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from spotify import renew_playlist
from langchain.chains import LLMChain


with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

openai.api_key = config["open_api_api_key"]
os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]

llm = OpenAI(temperature=0.7,max_tokens=512)

#json_converter= LLMChain(llm=llm, prompt=json_convert_template())

def json_converter(string):
    songs=[]
    lines = string.split("\n")
    for line in lines:
        values = line.split(",")
        songs+={"song": values[0], "artist":values[1]}
    return songs


convert2json_tool =  Tool(
    name = "convert2json",
    func=json_converter,
    description='''useful for when you have to listen a playlist / mixtape or convert it to json
    If the playlist is 
    1 - song,artist 
    2- song2,artist2 
    the input should be 
    song,artist 
    song2,artist2 
    ''',
    return_direct=True
)

main_prompt_template,follow_up_template=build_templates()

main_request_template = LLMChain(llm=llm, prompt=main_prompt_template)
questions_template = LLMChain(llm=llm, prompt=follow_up_template)

generatePlaylist_tool = Tool (
    name = "generateMixtape",
    func=main_request_template.run,
    description='''
    useful for when you have to make, generate a playlist or mixtape. 
    The output is the mixtape
    If the prompt is "a mixtape for me"
    the input should be "for me"
    ''',
)

followup_tool = Tool (
    name = "generateFollowup",
    func=questions_template.run,
    description="useful for when you have to generate followup questions in order to better understand the user input, asking details",
)




if __name__ == "__main__":
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    openai.api_key = config["open_api_api_key"]
    os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]

    llm = OpenAI(temperature=0)
    prompt="Ok, let's listen it!"
    mixtape="Mixtape: 1: a, 2: b."
    # Construct the agent. We will use the default agent type here.
    agent = initialize_agent([convert2json_tool], llm, agent="zero-shot-react-description", verbose=True)

    agent.run(mixtape + prompt)


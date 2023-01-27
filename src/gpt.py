
import openai
import os
import yaml
import logging
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

logger= logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def build_templates():
        instruction_main='''mixtape_request:  Make a mixtape of 10 songs 
        '''
                
        instruction_2=        '''Do not used the same artist more then once.
                '''

        instruction_5=''' Add an explanation on why did you choose these songs and how this is a good mixtape 
        '''

        example_mixtape_request= ''' Make a mixtape of 4 songs to listen in a train travel while snowing. It's for Nicola. He's italian and he's 40. Start with Time after time, sang by Eva Cassidy '''
 
        example_mixtape_ouput='''
        1 - "Time after time", "Eva cassidy". 
        Reason: "A strong entrance, setting the nostalgic mood. It's a famous song but a different singer"
        2 - "Love in vain", "The rolling stones".
        Reason: "It's one of your favourite song, it fit perfectly during a train trip for lyrics and mood"
        3 - "Sky full Of Song","Florence + the machine".
        Reason: "It's powerful and truble, more modern, interesting to discover"
        4 - "Ho imparato a sognare", "Negrita".
        Reason: "This is childhoold time in Italy in a song"

        Description: This is a nice mixtape because the mood it create fit with the nostalgic mood usually linked with a train travel and a snowy day. It also got some input from the childood time in Italy"     
        '''

 

        # First, create the list of few shot examples.
        examples = [
        {"mixtape_request": example_mixtape_request, "mixtape":  example_mixtape_ouput}
        ]

        # Next, we specify the template to format the examples we have provided.
        # We use the `PromptTemplate` class for this.
        example_formatter_template = """
                mixtape_request: {mixtape_request}
                mixtape: {mixtape}\n
        """
        example_prompt = PromptTemplate(
                input_variables=["mixtape_request", "mixtape"],
                template=example_formatter_template,
        )

        main_prompt = FewShotPromptTemplate(
                input_variables=["user_input"],
                prefix= instruction_2 + instruction_5,
                suffix= instruction_main + " {user_input} ",
                example_prompt=example_prompt,
                examples=examples
        )

        follow_up = PromptTemplate(
                input_variables=["user_input"],
                template='''Important input to consider when doing a mixtape are whom the mixtape is for, the ralation with him/her, the message to carry,
                a reference artist, the occasion the mixtape is for, etc. 
                Write 3 creative questions in order to get other inputs to make a personalized mixtape.
                Request: ''' + instruction_main + " {user_input} " + '''
                Questions:
                '''
        )

   

        return main_prompt,follow_up

if __name__ == "__main__":

        with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)

        openai.api_key = config["open_api_api_key"]
        os.environ["OPENAI_API_KEY"]=config["open_api_api_key"]

        llm = OpenAI(temperature=0.7,max_tokens=512)
        
        user_prompt='rock adatta al sabato mattina come la farebbe scaruffi'
        main_prompt,follow_up=build_templates()

        main_request = LLMChain(llm=llm, prompt=main_prompt)
        questions = LLMChain(llm=llm, prompt=follow_up)

        # Run the chain only specifying the input variable.
        mixtape=main_request.run(user_prompt)
        follow_ups=questions.run(user_prompt)

        print(mixtape)
        print(follow_ups)
     

        json_template=json_convert_template()
        json_converter = LLMChain(llm=llm, prompt=json_template)
        print(json_converter.run(input=mixtape))
        

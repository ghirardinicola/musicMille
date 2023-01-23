
import openai
import yaml
import logging
import json

logger= logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

openai.api_key = config["open_api_api_key"]

def build_playlist(prompt):
        
        # Generate text
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
        )


        # Print the generated text
        #logger.debug(response["choices"][0]["text"])

        playlist_str_real=response["choices"][0]["text"]

        # playlist_str='''
        # [
        #         {
        #                 "song": "Roundabout",
        #                 "artist": "Yes"
        #         }
        # ]
        # '''
        # playlist_obj= json.loads(playlist_str)
        # logging.debug(playlist_obj)
        playlist_obj= json.loads(playlist_str_real)
        logger.debug(playlist_obj)

        return playlist_obj


def build_gpt_prompt(user_input):

        impersonification=''' You are a music expert AI that can produce valid json describing mixtape.
        '''

        instruction_main='''  Make a mixtape of 10 songs 
        '''
                
        instruction_2=        '''Do not used the same artist more then once.
                '''
#         Important input to consider are whom the mixtape is for, the ralation with him/her, the message to carry,
#        a reference artist, the occasion the mixtape is for, etc. 
        instruction_3=           ''' Add 2 creative questions in order to get other inputs to make a personalized mixtape.
               '''

        instruction_5=''' Add an explanation on why did you choose these songs and how this is a good mixtape 
        '''

        example='''
                Be sure to return only a valid json. An example:
                { "mixtape":
                                [
                                        {
                                                "song": "Song title",
                                                "artist": "Song artist"
                                        }
                                ],
                "questions": [ "text": "Question to get param1", text:"text to get param2"]
                "mixtape_title": "title",
                "explanation":"this is a nice mixtape because ... "
                } 
        '''
        
        prompt=impersonification + instruction_main + user_input + instruction_2 + instruction_3  + instruction_5 + example
        logger.debug("prompt: "+ prompt)
        return prompt

if __name__ == "__main__":
        
        user_prompt=' rock adatta al sabato mattina come la farebbe scaruffi'
        prompt=build_gpt_prompt(user_prompt)
        logger.info(prompt)
        playlist=build_playlist(prompt)
        logger.info(playlist)
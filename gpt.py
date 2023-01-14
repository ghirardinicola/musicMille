
import openai
import yaml
import logging
import json




with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

openai.api_key = config["open_api_api_key"]

def build_playlist(prompt):

        logging.debug(prompt)
        
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
        logging.debug(response["choices"][0]["text"])

        playlist_str_real=response["choices"][0]["text"]

        playlist_str='''
        [
                {
                        "song": "Roundabout",
                        "artist": "Yes"
                }
        ]
        '''
        playlist_obj= json.loads(playlist_str)
        logging.debug(playlist_obj)
        playlist_obj= json.loads(playlist_str_real)
        logging.debug(playlist_obj)

        return playlist_obj


def build_gpt_prompt(user_input):
        
        prompt='''Give me a json file containing an array of 10 objects having song and artist keys describing "playlist ''' +  user_input + ''' "
                Be sure to give a valid json. Something like:
                [
                        {
                                "song": "Roundabout",
                                "artist": "Yes"
                        }
                ]
                '''
        return prompt

if __name__ == "__main__":
        logging.basicConfig(level=logging.DEBUG)
        user_prompt=' rock adatta al sabato mattina come la farebbe scaruffi'
        prompt=build_gpt_prompt(user_prompt)
        logging.info(prompt)
        playlist=build_playlist(prompt)
        logging.info(playlist)
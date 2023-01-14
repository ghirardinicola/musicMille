import logging
from spotify import renew_playlist
from gpt import build_playlist,build_gpt_prompt

logging.basicConfig(level=logging.INFO)

playlist_desc = input('Voglio una playlist ')

prompt=build_gpt_prompt(playlist_desc)

playlist_obj= build_playlist(prompt)
logging.info(prompt)

renew_playlist(playlist_obj)
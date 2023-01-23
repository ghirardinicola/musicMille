import logging
from spotify import renew_playlist
from gpt import build_playlist,build_gpt_prompt
import sys

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

n = len(sys.argv)
playlist_desc=""
if n>1:
    for i in range(1, n):
        playlist_desc+=sys.argv[i] + " "
else:
    playlist_desc = input('Create a mixtape ')

prompt=build_gpt_prompt(playlist_desc)

playlist_obj= build_playlist(prompt)

for song in playlist_obj["mixtape"]:
    print(song) 

renew_playlist(playlist_obj["mixtape"])

logger.info("The music_mille0 playlist is on your spotify account!")

print("Want to have a more personalized playlist?")
for question in playlist_obj["questions"]:
    print(question["text"])
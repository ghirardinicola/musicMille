import yaml
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['client_id'],
                                               client_secret=config['client_secret'],
                                               redirect_uri='http://localhost:8000/callback',
                                               scope=["playlist-modify-public"]))

def renew_mixtape(mixtape_obj):

    logger.debug(mixtape_obj)
   
    username = config['username']
    mixtape_name = 'musicMille_0'

    mixtape_results = sp.search(q=mixtape_name, type='playlist')

    mixtape=None

    if mixtape_results['playlists']['total'] > 0:
        for mixtape_res in mixtape_results['playlists']['items']:
            if mixtape_res['name'] == mixtape_name:
                mixtape = mixtape_res
                logger.debug("playlist found, removing tracks")

                tracks = sp.playlist_tracks(mixtape_res['id'])
                track_uris = [track["track"]["uri"] for track in tracks["items"]]
                sp.user_playlist_remove_all_occurrences_of_tracks(username, mixtape_res['id'], track_uris)
                logger.debug(f'All {len(track_uris)} tracks removed from the mixtape')
                

    if mixtape==None:
        logger.debug("mixtape not found, creating")
        mixtape = sp.user_playlist_create(username, mixtape_name)

    mixtape_id = mixtape['id']
    logger.debug(f"mixtape_id: {mixtape_id}")



    for item in mixtape_obj:
        title = item['song']
        artist = item['artist']
        results = sp.search(q='track:' + title + ' artist:' + artist, type='track')

        if results['tracks']['total'] > 0:
            track_uri = results['tracks']['items'][0]['uri']
            sp.user_playlist_add_tracks(username, mixtape_id, [track_uri])
            logger.debug(f"Track {title} by {artist} added to the mixtape")
        else:
            logger.warn(f"Track {title} by {artist} not found")



if __name__ == "__main__":
    
    prompt='Give me a list of python dict having song and artist keys describing "mixtape rock adatta al sabato mattina come la farebbe scaruffi"'

    mixtape_obj = [
        {'song': 'Good Morning Little School Girl', 'artist': 'The Yardbirds'},
        {'song': 'Saturday Morning', 'artist': 'The Kinks'},
        {'song': 'Breakfast in Bed', 'artist': 'Dusty Springfield'},
        {'song': 'Saturday Night', 'artist': 'The Rubinoos'},
        {'song': 'Morning Dew', 'artist': 'The Grateful Dead'},
        {'song': 'Saturday Sun', 'artist': 'Nick Drake'},
        {'song': 'Morning Glory', 'artist': 'Oasis'},
        {'song': 'Saturday Night\'s Alright for Fighting', 'artist': 'Elton John'},
        {'song': 'Good Morning Blues', 'artist': 'Lead Belly'},
        {'song': 'Saturday Night', 'artist': 'The Bay City Rollers'},
    ]

    renew_mixtape(mixtape_obj)

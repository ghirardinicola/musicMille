import yaml
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)



with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['client_id'],
                                               client_secret=config['client_secret'],
                                               redirect_uri='http://localhost:8000/callback',
                                               scope=["playlist-modify-public"]))

def renew_playlist(playlist_obj):
   
    username = config['username']
    playlist_name = 'musicMille_0'

    playlist_results = sp.search(q=playlist_name, type='playlist')

    playlist=None

    if playlist_results['playlists']['total'] > 0:
        for playlist_res in playlist_results['playlists']['items']:
            if playlist_res['name'] == playlist_name:
                playlist = playlist_res
                logger.debug("Playlist found, removing tracks")

                tracks = sp.playlist_tracks(playlist_res['id'])
                track_uris = [track["track"]["uri"] for track in tracks["items"]]
                sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_res['id'], track_uris)
                logger.debug(f'All {len(track_uris)} tracks removed from the playlist')
                

    if playlist==None:
        logger.debug("Playlist not found, creating")
        playlist = sp.user_playlist_create(username, playlist_name)

    playlist_id = playlist['id']
    logger.debug(f"playlist_id: {playlist_id}")


    for item in playlist_obj:
        title = item['song']
        artist = item['artist']
        results = sp.search(q='track:' + title + ' artist:' + artist, type='track')

        if results['tracks']['total'] > 0:
            track_uri = results['tracks']['items'][0]['uri']
            sp.user_playlist_add_tracks(username, playlist_id, [track_uri])
            logger.debug(f"Track {title} by {artist} added to the playlist")
        else:
            logger.warn(f"Track {title} by {artist} not found")



if __name__ == "__main__":
    
    prompt='Give me a list of python dict having song and artist keys describing "playlist rock adatta al sabato mattina come la farebbe scaruffi"'

    playlist_obj = [
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

    renew_playlist(playlist_obj)

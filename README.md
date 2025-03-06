# musicMille

Linux terminal command to create a musicMille spotify mixtape, just as talking with (chat)GPT

## Usage
Create a config.yaml file such as (first entries of spotify):   

    client_id: 
    client_secret: 
    username: 
    open_api_api_key: 

- Create python env using requirement.txt
- python musicMille.py
- Listen musicMille_0 mixtape
- Contribuite ;)

## Next
Make it step-by-step:
- Collaborate on a mixtape. Modify "by hand"
- Get a spotify mixtape and start from there (NICE! Start from there, more this, less that)

# TEST
python src/app.py    

## Docker
docker build -t chat-api .  
docker run -p 8080:8080 chat-api
curl http://localhost:8080/health


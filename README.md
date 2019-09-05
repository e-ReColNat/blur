Supported format:
.png, .jpg, jpeg

## Install
```
source install.sh
```
Installation is made in a VirtualEnv so use "activate" command to manually activate the Env (mandatory to DEBUG/TEST)

## Run API:
```
#DEBUG DETECTOR (DEBUG flag activated by default)
source ./env/bin/activate
python3 reco_michel.py http://mediaphoto.mnhn.fr/media/1441381633726ttCwJlmrl5PE83H3 0.3

#DEBUG FLASK
source ./env/bin/activate
gunicorn api:app

#PRODUCTION (auto start at boot)
sudo service supervisor start
sudo service supervisor restart
sudo service supervisor stop
sudo service supervisor status
```

## Authorize ip
```
echo "API_KEY:IP" >> auths.txt
```

## Call api (IP must have been authorized)
```
curl -H "Content-type: application/json" -H "Key: API_KEY" -X POST http://detectlabel.agoralogie.fr/api/ -d '{"data": "IMG_URL", "threshold": 0.65, "debug": "True"}'
```

## Run UnitTests:
```
python -m pytest --disable-warnings
```

## Remove
```
rm -rf env
```
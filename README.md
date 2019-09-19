## Requirements : 
Python(>=3.5) 
pip(>=9.0.1)

## Install
(tested on Ubuntu 18.04.3, Ubuntu_server 18.04.3, Debian 10.1.0)
```
sudo apt-get update
source install.sh [SERVERNAME]
```
You can safely ignore the red lines...

SERVERNAME can be provided as an argument or it will be asked durring installation.
(examples : "localhost" or "http://my_url.com http://www.my_url.com" or "143.21.178.46")
Keep in mind that the address/name should be accessible from outside, otherwise you will experiment some 404 errors...

Installation is made in a Python VirtualEnv so you must use the "activate" command to manually activate the Env 
(mandatory to DEBUG/TEST but automaticaly done by supervisor while in production)

## Run API:
```
#DEBUG DETECTOR (DEBUG flag activated by default)
source ./env/bin/activate
python3 reco_michel.py IMG_URL [CONFIDENCE]

#DEBUG FLASK
source ./env/bin/activate
gunicorn api:app

#PRODUCTION (auto start at boot)
sudo service supervisor start
sudo service supervisor restart
sudo service supervisor stop
sudo service supervisor status
```
with 	IMG_URL		: an accessible image url
	CONFIDENCE 	: the confidence threshold (def to 65, mean that detection are drawn over 65% confidence only)


## Authorize ip
(https://codepen.io/corenominal/pen/rxOmMJ)
```
echo "API_KEY:IP" >> auths.txt
```
with 	API_KEY 	: your private API_KEY
	IP		: your public IP
Several IPs can be user wuth the same API_KEY, just add one line per IP
You can use wildcards "*" at the end of the IP to allow a whole network/subnet


## Call api (IP must have been authorized)
```
curl http://[SERVERNAME]/api/?key=API_KEY&source=IMG_URL&confidence=CONFIDENCE&debug=DEBUG

or from localhost:
curl http://localhost:8000/api/?key=API_KEY&source=IMG_URL&confidence=CONFIDENCE&debug=DEBUG
```
with 	API_KEY 	: your private API_KEY (note that it is tied to your IP by host)
	IMG_URL		: an accessible image url
	CONFIDENCE 	: the confidence threshold (def to 65, mean that detection are drawn over 65% confidence only)
	FILEOUT		: flag (0 or 1) to get the censored image url in return (default to 1)
	DEBUG		: debug flag (0 or 1) save and return original image, masked image, boxes data and detected image (default to 0)

returns : {	"message":"OK",
		"result_data": {Boxes data dict},
		["result_image":"your_image_name_censored.jpg"] }


## Run UnitTests:
```
python -m pytest --disable-warnings
```

## Remove
```
source uninstall.sh
```

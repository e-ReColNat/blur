Supported format:
.png, .jpg, jpeg

## Install
```
source install.sh
```
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


## Call api (IP must have been authorized)
```
curl http://detectlabel.agoralogie.fr/api/?key=API_KEY&source=IMG_URL&confidence=CONFIDENCE&debug=DEBUG
```
with 	API_KEY 	: your private API_KEY (note that it is tied to your IP by host)
	IMG_URL		: an accessible image url
	CONFIDENCE 	: the confidence threshold (def to 65, mean that detection are drawn over 65% confidence only)
	DEBUG		: debug flag (to be defined)

returns : {	"message":"OK",
		"result_data":"your_image_name_listbox.txt",
		"result_image":"your_image_name_censored.jpg" }


## Run UnitTests:
```
python -m pytest --disable-warnings
```

## Remove
```
source uninstall.sh
```
"deactivate" command is to turn off the Python virtual env (if you see "(env)" at start of your shell's lines, you are in...)

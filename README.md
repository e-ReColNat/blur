Supported format:
.png, .jpg, jpeg

## install
```
pip install -r requirements.txt
```

## run API:
```
#DEBUG
python api.py

#PROD
gunicorn -b 0.0.0.0:8000 api:app
```

## call api
```
curl -H "Content-type: application/json" -H "Key: TEST_KEY" -X POST http://127.0.0.1:8000/api/ -d '{"data": "http://mediaphoto.mnhn.fr/media/1441305440248Dg5YP6C3kALFvbh5", "threshold": 0.65}'
```

## run UnitTests:
```
python -m pytest --disable-warnings
```
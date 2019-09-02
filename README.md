
## install
```
pip install -r requirements.txt
```

## run API:
```
#DEBUG
python api.py

#PROD
gunicorn -b 0.0.0.0:5000 api:app
```

## call api
```
curl -H "Content-type: application/json" -H "Key: TEST_KEY" -X POST http://192.168.0.10:5000/api/ -d '{"Data": "test"}'
```

## run UnitTests:
```
python -m pytest --disable-warnings
```
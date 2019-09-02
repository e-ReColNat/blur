
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
curl -H "Content-type: application/json" -H "Key: TEST_KEY" -X POST http://127.0.0.1:8000/api/ -d '{"Data": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Illustration_Lupinus_luteus1.jpg", "Save_flag": "False"}'
```

## run UnitTests:
```
python -m pytest --disable-warnings
```
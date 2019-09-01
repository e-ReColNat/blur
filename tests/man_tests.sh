# run unit tests with : 
# python -m pytest --disable-warnings
curl -H "Content-type: application/json" -H "Key: TEST_KEY" -X POST http://127.0.0.1:5000/api/ -d '{"Data": "test"}'
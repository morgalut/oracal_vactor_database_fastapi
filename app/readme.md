## how run
```sh 
pip install -r requirements.txt
```




# run fastapi
```sh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

# test 
```sh
curl -X POST http://localhost:8000/vector/documents \
  -H "Content-Type: application/json" \
  -d '{
    "id": "doc_002",
    "text": "FastAPI and Oracle vector store integration test."
  }'
```
import imp
from typing import Optional, List
from fastapi import FastAPI, Header, Request
#from jose import JWTError, jwt
import jwt

CLIENT_ID='23cd2d50b8d338ef9bd0d8a542218c7436755e47'

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test")
def test(request: Request):
    
    try:
        print(request.headers.get('Authorization'))
        payload = request.headers.get('Authorization').replace('Bearer ', '')
        print(payload)
    except:
        return {"error": "no token"}
        
    # authd = jwt.decode(access_token, '23cd2d50b8d338ef9bd0d8a542218c7436755e47', algorithms=['HS256'], options={"verify_signature": False})
    authd = jwt.decode(payload, algorithms=['HS256'], options={"verify_signature": False, "verify_aud": False})
    print(authd)
    for key, value in authd.items():
        print(key, value)
    
    if authd['cid'] != CLIENT_ID:
        return {'error': 'invalid client id'}

    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
from typing import Optional, List
from fastapi import FastAPI, Header, Request
import uvicorn
#from jose import JWTError, jwt
import jwt
import k11

CLIENT_ID = '23cd2d50b8d338ef9bd0d8a542218c7436755e47'

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

    authd = jwt.decode(payload,
                       algorithms=['HS256'],
                       options={
                           "verify_signature": False,
                           "verify_aud": False
                       })
    print(authd)
    for key, value in authd.items():
        print(key, value)

    if authd['cid'] != CLIENT_ID:
        return {'error': 'invalid client id'}

    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/test1")
def test1(request: Request):
    return k11.read_root()


@app.get("/test2")
def test2(request: Request):
    return k11.read_racks()


@app.get("/read_racks_as_csv")
def test3(request: Request):
    return k11.read_racks_as_csv()


@app.get("/test4")
def test4(request: Request):
    return k11.read_racks_as_df()


@app.get("/test5")
def test4(request: Request):
    return k11.read_racks_mean_as_csv()


@app.get("/read_as_table")
def read_as_table(request: Request):
    return k11.read_root_as_table()


@app.get("/read_cell_as_table")
def read_cell_as_table(request: Request):
    return k11.read_cell_as_table()


@app.get("/read_cell")
def read_cell(request: Request):
    return k11.read_cell()


@app.get("/read_bank_summary")
def read_bank_summary(request: Request):
    return k11.read_bank_summary()


@app.get("/read_bank_summary_cur")
def read_bank_summary_cur(request: Request):
    return k11.read_bank_summary_cur()


@app.get("/read_bank_summary_soc")
def read_bank_summary_soc(request: Request):
    return k11.read_bank_summary_soc()


@app.get("/read_cells_for_histogram/{bank_idx}")
def read_cells_for_histogram(request: Request, bank_idx: int = 0):
    return k11.read_cells_for_histogram(bank_idx)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
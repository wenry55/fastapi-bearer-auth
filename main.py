from datetime import datetime
import string
from typing import Optional, List
from fastapi import FastAPI, Header, Request
import uvicorn
#from jose import JWTError, jwt
import jwt
import k11
import os
import json
from typing import List
from fastapi.responses import FileResponse
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from sqlalchemy.orm import Session

from dashboard import crud, models, schemas
from dashboard.database import SessionLocal, engine

CLIENT_ID = '23cd2d50b8d338ef9bd0d8a542218c7436755e47'
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}



@app.get("/get_image/{img_id}")
async def get_image(img_id: str):
    return FileResponse("/image/camera00"+ img_id +".jpg")

@app.get("/get_result_json/{json_id}")
async def get_result_json(json_id: str):
    return FileResponse("/image/detect_result"+ json_id +".json")

@app.post("/save_switch_json/{cam_id}/{carriage_state}/{rack_state}")
async def save_switch_json(cam_id: int, carriage_state: str, rack_state: str):
    UPLOAD_DIR = "/image"  # 이미지를 저장할 서버 경로
    
    # data = {"hi":"world"}
    json_string = '{"Camera":1,"detect_carriage":"ON","detect_rack":""}'
    json_data = json.loads(json_string)
    json_data["Camera"] = cam_id
    json_data["detect_carriage"] = carriage_state
    json_data["detect_rack"] = rack_state
    
    
    filename = "detect_switch1.json"  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "w") as fp:
        fp.write(json.dumps(json_data))  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"filename": filename}

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

@app.get("/read_module_temp_for_histogram/{bank_idx}")
def read_module_temp_for_histogram(request: Request, bank_idx: int = 0):
    return k11.read_module_temp_for_histogram(bank_idx)

@app.get("/read_rack_status/{bank_idx}/{rack_idx}")
def read_rack_status(request: Request, bank_idx: int, rack_idx: int):
    return k11.read_rack_status(bank_idx, rack_idx)

@app.get("/read_module_status/{bank_idx}/{rack_idx}")
def read_module_status(request: Request, bank_idx: int, rack_idx: int):
    return k11.read_module_status(bank_idx, rack_idx)

@app.get("/read_cell_status/{bank_idx}/{rack_idx}/{val_type}")
def read_cell_status(request: Request, bank_idx: int, rack_idx: int, val_type: str):
    return k11.read_cell_status(bank_idx, rack_idx, val_type)

@app.get("/read_rack_trend/{bank_idx}/{rack_idx}/{unit}/{val_type}/{from_date}/{to_date}/{time_stamp}")
def read_rack_trend(request: Request, bank_idx: int, rack_idx: int, val_type: str, unit: str, from_date: datetime, to_date: datetime, time_stamp: str):
    return k11.read_rack_trend(bank_idx, rack_idx, unit, val_type, from_date, to_date, time_stamp)

@app.get("/dashboards/", response_model=List[schemas.Dashboard])
def read_dashboards(skip: int = 0,
                    limit: int = 100,
                    db: Session = Depends(get_db)):
    dashboards = crud.get_dashboards(db, skip=skip, limit=limit)
    return dashboards


@app.get("/dashboards/{dashboard_id}", response_model=schemas.Dashboard)
def read_dashboard(dashboard_id: str, db: Session = Depends(get_db)):
    db_dashboard = crud.get_dashboard(db, dashboard_id=dashboard_id)
    if db_dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return db_dashboard


@app.post("/dashboards/", response_model=schemas.Dashboard)
def create_dashboard(dashboard: schemas.DashboardCreate,
                     db: Session = Depends(get_db)):
    return crud.create_dashboard(db=db, dashboard=dashboard)


@app.put("/dashboards/{dashboard_id}", response_model=schemas.Dashboard)
def update_dashboard(dashboard_id: str,
                     dashboard: schemas.DashboardUpdate,
                     db: Session = Depends(get_db)):
    return crud.update_dashboard(db=db,
                                 dashboard_id=dashboard_id,
                                 dashboard=dashboard)


@app.delete("/dashboards/{dashboard_id}", response_model=schemas.Dashboard)
def delete_dashboard(dashboard_id: str, db: Session = Depends(get_db)):
    return crud.delete_dashboard(db=db, dashboard_id=dashboard_id)



@app.get("/components/{component_id}", response_model=schemas.Component)
def read_component(component_id: str, db: Session = Depends(get_db)):
    db_component = crud.get_component(db, component_id=component_id)
    if db_component is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return db_component

@app.post("/components/", response_model=schemas.Component)
def create_component(component: schemas.ComponentCreate,
                     db: Session = Depends(get_db)):
    return crud.create_component(db=db, component=component)

@app.put("/components/{component_id}", response_model=schemas.Component)
def update_component(component_id: str,
                     component: schemas.ComponentUpdate,
                     db: Session = Depends(get_db)):
    return crud.update_component(db=db,
                                 component_id=component_id,
                                 component=component)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
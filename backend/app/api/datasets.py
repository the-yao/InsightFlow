import io
import os
from datetime import datetime

import pandas as pd
from fastapi import APIRouter,Depends,File,HTTPException,UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models import Dataset

router = APIRouter(prefix="/datasets",tags=["datasets"])

STORAGE_DIR = "storage" #上传文件落盘目录

#--Pydantic响应模型：定义“返回给前端的数据长什么样”--
class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True) #允许从OSR对象直接读字段

    id: int
    name: str
    file_path: str
    schema_json: dict
    created_at: datetime

def infer_schema(df:pd.DataFrame)->dict:
    """推断每列类型 + 样例值 + 缺失值数量，供后续 Agent 理解数据结构"""
    schema = {}
    for col in df.columns:
        non_null = df[col].dropna()
        schema[col] ={
            "dtype": str(df[col].dtype),
            "sample": str(non_null.iloc[0]) if not non_null.empty else "None",
            "null_count": int(df[col].isna().sum()) #缺失值数量
        }
    return schema

@router.post("/",response_model=DatasetOut,status_code=201)
async def upload_dataset(file: UploadFile = File(...),db: Session = Depends(get_db)):
    #1.校验：只允许上传CSV文件
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400,detail="只支持CSV文件")

    #2.pandas 解析并推断 schema
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400,detail="CSV文件解析失败")
    schema = infer_schema(df)

    #3.文件落盘
    os.makedirs(STORAGE_DIR,exist_ok=True)
    file_path = os.path.join(STORAGE_DIR,file.filename)
    with open(file_path,"wb") as f:
        f.write(content)

    #4.写数据库（user_id 暂时留空，等阶段4加认证时再补）
    dataset = Dataset(name=file.filename,file_path=file_path,schema_json=schema)
    db.add(dataset)
    db.commit()
    db.refresh(dataset) #拿回数据库生成的 id 和 created_at 

    return dataset

@router.get("/",response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.execute(select(Dataset)).scalars().all()

@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.get(Dataset,dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404,detail="数据集不存在")
    return dataset


from fastapi import status
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud.crud_item import get_all_az_keys, get_normal_az_keys, add_az_key, update_az_key_crud, delete_az_key, get_az_key_by_id

from typing import Optional
from asyncio import Lock

# 全局变量和锁初始化
global_counter = 0
counter_lock = Lock()

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_all_az_keys(request: Request, db: Session = Depends(get_db)):
    az_keys = await get_all_az_keys(db)  # 假设这会返回所有AZKeys的列表
    return templates.TemplateResponse("index.html", {"request": request, "az_keys": az_keys})

# 让我们更改 "/az-keys/normal/{in_use_count}" 路由处理函数以返回HTML页面
@router.get("/az-keys/normal/{in_use_count}", response_class=HTMLResponse)
async def read_normal_az_keys_html(request: Request, in_use_count: int = 6, db: Session = Depends(get_db)):
    try:
        # 根据入参调整调用方式
        normal_az_keys = await get_normal_az_keys(db, in_use_count if in_use_count > 0 else None)
        # 返回HTML模板响应
        return templates.TemplateResponse("normal_az_keys.html", {"request": request, "az_keys": normal_az_keys})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to read normal AZKeys: {str(e)}")
    


# 加上这行代码注册前端表单
@router.get("/az-keys/add-form", response_class=HTMLResponse)
async def add_az_key_form(request: Request):
    return templates.TemplateResponse("add_az_key.html", {"request": request})

# 确保所有其他路由和函数保持不变
# 这里插入之前的路由和函数

# 注意更改重名的POST路由处理函数
@router.post("/az-keys/")
async def create_az_key(
    db: Session = Depends(get_db), 
    resourcename: str = Form(...), 
    key: str = Form(...), 
    status: Optional[str] = Form(None), 
    is_in_use: Optional[bool] = Form(None)
):
    az_key_data = {
        "resourcename": resourcename,
        "key": key,
        "status": status,
        "is_in_use": is_in_use,
    }
    try:
        new_az_key = await add_az_key(db, az_key_data)
        return RedirectResponse(url='/', status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to create AZKey: {str(e)}")
    

@router.get("/az-keys/")
async def read_all_az_keys(db: Session = Depends(get_db)):
    try:
        az_keys = await get_all_az_keys(db)
        return {"data": az_keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to read AZKeys: {str(e)}")

@router.post("/az-keys/")
async def create_az_key(az_key_data: dict, db: Session = Depends(get_db)):
    try:
        new_az_key = await add_az_key(db, az_key_data)
        return {"message": "AZKey created successfully", "data": new_az_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to create AZKey: {str(e)}")

# 假设您有这样一个路由来显示编辑表单
@router.get("/az-keys/edit/{az_key_id}", response_class=HTMLResponse)
async def edit_az_key_form(request: Request, az_key_id: int, db: Session = Depends(get_db)):
    az_key = await get_az_key_by_id(db, az_key_id)  # 假设这是获取AZKey详情的异步函数
    if not az_key:
        raise HTTPException(status_code=404, detail="AZKey not found")
    return templates.TemplateResponse("edit_az_key.html", {"request": request, "az_key": az_key})

# 更新AZKey的后端处理
@router.post("/az-keys/update/{az_key_id}")
async def update_az_key_handler(request: Request, az_key_id: int, db: Session = Depends(get_db)):
    form_data = await request.form()
    update_data = {
        "resourcename": form_data.get("resourcename"),
        "key": form_data.get("key"),
        "status": form_data.get("status"),
        # add other fields as needed
    }
    # Ensure that this call is made to the correctly named CRUD operation function
    updated_az_key = await update_az_key_crud(db, az_key_id, update_data)
    if not updated_az_key:
        raise HTTPException(status_code=404, detail="AZKey not found")
    return RedirectResponse(url='/', status_code=303)

@router.get("/az-keys/delete/{az_key_id}")
async def delete_az_key_api(az_key_id: int, db: Session = Depends(get_db)):
    delete_result = await delete_az_key(db, az_key_id)
    if "error" in delete_result:
        raise HTTPException(status_code=404, detail=delete_result["message"])
    return RedirectResponse(url='/', status_code=303)


@router.get("/get-keys/")
async def get_keys(db: Session = Depends(get_db)):
    global global_counter
    async with counter_lock:
        # 累加并获取全局计数
        global_counter += 1

    # 获取常规的AZKeys数组
    normal_az_keys = await get_normal_az_keys(db=db, in_use_count=0)

    if not normal_az_keys:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No AZKeys found."}
        )

    # 根据全局计数器对数组长度取余，以实现循环访问
    key_index = global_counter % len(normal_az_keys)
    selected_key = normal_az_keys[key_index]

    # 返回被选择的key和一些其他可能有用的信息
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Successfully retrieved AZKey.",
            "data": selected_key,
            "key_index": key_index
        },
    )
    
from openai import AsyncAzureOpenAI
    
async def request_azure(resourcename, key):
    try:
        async with AsyncAzureOpenAI(
            api_version="2023-07-01-preview",
            azure_endpoint=f"https://{resourcename}.openai.azure.com",
            api_key=key
        ) as client:
            completion = await client.models.list()
            return False
    except Exception as e:
        if 'Unauthorized' in str(e):
            print('Unauthorized')
            return True
        else:
            return False

import asyncio
@router.get("/update_keys/")
async def get_keys(db: Session = Depends(get_db)):
    normal_keys = await get_normal_az_keys(db, in_use_count=-1)
    for normal_key in normal_keys:
        print('验证', normal_key)
        is_401 = await request_azure(normal_key['resourcename'], normal_key['key'])
        if is_401:
            print("这个账号已经被禁用了")
            normal_key['status'] = 'suspend'
            await update_az_key_crud(db, normal_key['id'], normal_key)
            await asyncio.sleep(1)
    
    
    


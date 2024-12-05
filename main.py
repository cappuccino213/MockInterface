"""
@File : main.py
@Date : 2023/7/12 16:25
@Author: 九层风（YePing Zhang）
@Contact : yeahcheung213@163.com
"""
import uvicorn
from fastapi import FastAPI

from routers.dep_router import dep_route
from routers.token_router import token_route, product_route
from routers.archive_router import archive_route
from routers.follow_up_router import follow_up_route
from routers.imcis_router import imcis_route
from routers.exam_recognition_router import recognition_route

from multiprocessing import freeze_support

from config import CONFIG

app = FastAPI()

# 注册路由
app.include_router(archive_route)
app.include_router(follow_up_route)
app.include_router(imcis_route)
app.include_router(token_route)
app.include_router(product_route)
app.include_router(dep_route)

app.include_router(recognition_route)

if __name__ == "__main__":
    # uvicorn.run(app='main:app', host='0.0.0.0', port=8888, reload=True)
    freeze_support()  # 解决pyinstaller打包后无限重启的问题
    uvicorn.run(app='main:app', host='0.0.0.0', port=CONFIG['uvicorn']['port'], reload=CONFIG['uvicorn']['reload'],
                workers=CONFIG['uvicorn']['process_num'])

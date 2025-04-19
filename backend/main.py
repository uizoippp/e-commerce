from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.signup import signup
from routes.signin import signin
from routes.curd import *
from routes.crawl import *
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from websocket_llm.chat import chat as websocket_chat
from websocket_detectface.videoprocessing import videoprocess as websocket_video_process

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Có thể thay "*" bằng danh sách các domain mà bạn muốn cho phép
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức HTTP
    allow_headers=["*"],  # Cho phép tất cả các header
)

app.mount('/media', StaticFiles(directory='media'), name='media')

app.include_router(signin, prefix='/user') #127.0.0.1:8000/user/login
app.include_router(signup, prefix='/user')
app.include_router(user_route, prefix='/user')
app.include_router(product_route, prefix='/product')
app.include_router(cart_route, prefix='/cart')
app.include_router(order_route, prefix='/order')
app.include_router(crawl, prefix='/crawl')
app.include_router(websocket_chat) # websocket
app.include_router(websocket_video_process)

app.include_router(test_routes, prefix='') # websocket
if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
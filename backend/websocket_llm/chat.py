import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from concurrent.futures import ThreadPoolExecutor
from websocket_llm.model import *
from websocket_llm.functions import *
import asyncio
from functools import partial
from database.database import get_db

chat = APIRouter(
    tags=['websocket-chat']
)

role_system = """Bạn là một trợ lý AI hữu ích. Chỉ sử dụng thông tin trong tài liệu để trả lời câu hỏi. Nếu không tìm thấy thông tin cần thiết, hãy trả lời: "Tôi không biết!". Không được tự suy đoán hoặc sử dụng kiến thức bên ngoài.\n"""

# Tạo một ThreadPoolExecutor để thực hiện các tác vụ tính toán song song
executor = ThreadPoolExecutor(max_workers=4)

@chat.websocket("/ws/chatroom")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global role_system

    try: 
        while True:
            text = await websocket.receive_text()
        
            db_session = next(get_db())

            # Chạy tính toán song song sử dụng ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            relevant_documents_fn = partial(relevant_documents, text=text, db=db_session, top_k=3, threshold=0.8)
            documents_search_fn = partial(documents_search, text=text, top_internet=4, top_local=3, threshold=0.5)
            
            docs_database = loop.run_in_executor(executor, relevant_documents_fn)
            docs_internet = loop.run_in_executor(executor, documents_search_fn)

            docs_db, docs_inter = await asyncio.gather(docs_database, docs_internet)
            
            prompt = build_prompt(documents=docs_db, documents_internet=docs_inter, question=text, system_msg=role_system)
            response = generate_answer(prompt=prompt)

            print(response)
            response = response.strip().split('### Assistant:')[-1]
            await websocket.send_text(f"{response}")

    except WebSocketDisconnect:
        print('Ngat ket noi')
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

role_system = """Bạn là một trợ lý AI hữu ích, chỉ sử dụng thông tin được cung cấp để trả lời câu hỏi. Nếu không tìm thấy thông tin cần thiết, hãy trả lời: "Tôi không biết và giải thích do thiếu thông tin!". Không được suy đoán hoặc dùng kiến thức bên ngoài.\n"""

@chat.websocket("/ws/chatroom")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global role_system

    try: 
        while True:
            text = await websocket.receive_text()
            db_session = next(get_db())

            list_query = decompose_prompt(query=text)
            loop = asyncio.get_event_loop()

            task = []
            with ThreadPoolExecutor() as executor:
                for q in list_query:
                    relevant_documents_fn = partial(relevant_documents, text=q, db=db_session, top_k=2, threshold=0.8)
                    documents_search_fn = partial(documents_search, text=q, top_internet=3, top_local=2, threshold=0.7)
                
                    docs_database = loop.run_in_executor(executor, relevant_documents_fn)
                    docs_internet = loop.run_in_executor(executor, documents_search_fn)
                    
                    task.append(asyncio.gather(docs_database, docs_internet))
            
            results = await asyncio.gather(*task)
            
            doc_db, doc_inter = zip(*results)
            # print(doc_inter)
            prompt = build_prompt(documents=doc_db, documents_internet=doc_inter, question=text, system_msg=role_system)
            response = generate_answer(prompt=prompt)

            print(response)
            response = response.strip().split('### Assistant:')[-1]
            await websocket.send_text(f"{response}")

    except WebSocketDisconnect:
        
        print('Ngat ket noi')
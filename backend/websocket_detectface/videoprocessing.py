from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from database import get_db, user
from sqlalchemy.orm import Session
import numpy as np
import cv2
from .videoProcessManager import VideoProcessing
import re
import json
from database.database import vectorUser
import time


videoprocess = APIRouter(
    tags=['websocket-videoprocess']
)

def add_vector_to_db(user_id, embedding, db):
    vector_json = json.dumps(embedding.tolist())

    vector_data = vectorUser(vector=vector_json, id_user=user_id)
    db.add(vector_data)
    db.commit()

def is_image_data(data: str) -> bool:
    image_regex = r'^data:image\/[a-zA-Z]*;base64,'
    return bool(re.match(image_regex, data))
         
        
@videoprocess.websocket('/ws/stream/{id_user}')
async def video_process(websocket: WebSocket, id_user: int, db: Session = Depends(get_db)):
    videoProcess = VideoProcessing()
    await videoProcess.connect(websocket)
    try:
        bbox = []
        alignFace = None
        embedding = None
        while True:
            data = await websocket.receive_text()
            if data:
                # Kiểm tra dữ liệu là hình ảnh hay là yêu cầu của người dùng
                if is_image_data(data):
                    # Tách chuỗi base64 thành dữ liệu ảnh
                    videoProcess.decodeImage(data)

                    bbox = videoProcess.faceDetecting()
                    if len(bbox) != 0:
                        # Mặt người dùng có quá xa camera hay không
                        if not videoProcess.estimateDistance(bbox): 
                            await websocket.send_json({
                                'type': 'text', 
                                'message': f'Khuôn mặt quá xa camera!'})
                        else:
                            # Chỉ cắt mặt của người dùng để xử lý tiếp
                            croppedFace = videoProcess.croppedFace(bbox)
                            # Chỉnh lại góc độ khuôn mặt và giảm ảnh hưởng độ rung, lắc, xoay camera
                            alignFace = videoProcess.alignFace(croppedFace)
                            await websocket.send_json({
                                'type': 'text',
                                'message': 'Bạn có thể gửi ảnh!'
                            })
                    else: 
                        await websocket.send_json({
                            'type': 'text',
                            'message': 'Không nhận dạng bất kỳ khuôn mặt nào!'
                        })
                    # Mã hóa chuỗi trước khi đưa vào wesocket
                    encodeImage = videoProcess.encodeImage() 
                    # Đưa dữ liệu vào websocket 
                    await websocket.send_text(f'data:image/jpeg;base64,{encodeImage}')
                
                # Kiểm tra dữ liệu có phải là yêu cầu người dùng chụp ảnh khôngkhông
                elif data:
                    # Kiểm tra măt thật hay giả, độ xa của khuôn mặt có đạt yêu cầu, đã crop khuôn mặt và xử lý rung lắc chưachưa
                    if len(alignFace) != 0 and videoProcess.estimateDistance(bbox):
                    # and videoProcess.is_alive_face(alignFace):
                        embedding = videoProcess.get_embedding(alignFace)
                        # lưu vector vào csdl
                        add_vector_to_db(id_user, embedding, db)

                        # videoProcess.faiss.add(np.array([embedding]))
                        # faiss.write_index(videoProcess.faiss, 'websocket/face_embedding/face_index.bin')
                        
                        await websocket.send_json({'type': 'text',
                                                   'message': 'Embedding sumitted!!!!!!!!!!!!!!'})
                    
                    await websocket.send_json({'type': 'text',
                                               'message': 'Có lỗi xảy ra!'})


    except WebSocketDisconnect:
        cv2.destroyAllWindows()

class checkEmbedding(VideoProcessing):
    def __init__(self):
        VideoProcessing.__init__(self)
        self.id_user_list = []

    def get_all_vector(self, db: Session):
        vector_datas = db.query(vectorUser).all()
        # vector_data = id, vector, id_user
        vector_list = []

        for vector_data in vector_datas:
            vector = json.loads(vector_data.vector)
            vector_array = np.array(vector, dtype=np.float64)
            self.id_user_list.append(vector_data.id_user)
            vector_list.append(vector_array)

        vectors_np = np.array(vector_list, dtype=np.float64)
        self.faiss.add(vectors_np)

    def calculateSimilarity(self, currEmbedding):
        '''
        Trả về id_user và khoảng cách cosin có độ tương đồng cao nhất.
        '''
        distances, indices = self.faiss.search(currEmbedding.reshape(1, -1), 1)
        closest_id_user = self.id_user_list[indices[0][0]]
        return closest_id_user, distances[0][0]
    
    def check_condition_in_1_second(self, id_user: int, distances: float):
        start_time = time.time()
        pre_id = None
        cur_id = None
        while time.time() - start_time < 1:
            cur_id = id_user
            if not (cur_id == pre_id) and distances < self.similarity_threshold:
                return False
            pre_id = cur_id
            time.sleep(0.01)  # Thử lại mỗi 10ms
        return True

@videoprocess.websocket('/ws/check')
async def check_face(websocket: WebSocket, db: Session = Depends(get_db)):
    checkFace = checkEmbedding()
    await checkFace.connect(websocket)
    checkFace.get_all_vector(db)
    try:
        bbox = []
        alignFace = None
        embedding = None
        id_user = None
        distances = None
        while True: 
            data = await websocket.receive_text()
            
            if data:
                # Kiểm tra dữ liệu là hình ảnh hay là yêu cầu của người dùng
                if is_image_data(data):
                    # Tách chuỗi base64 thành dữ liệu ảnh
                    checkFace.decodeImage(data)
                    bbox = checkFace.faceDetecting()
                    if len(bbox) != 0:
                        # Chỉ cắt mặt của người dùng để xử lý tiếp
                        croppedFace = checkFace.croppedFace(bbox)
                        # Chỉnh lại góc độ khuôn mặt và giảm ảnh hưởng độ rung, lắc, xoay camera
                        alignFace = checkFace.alignFace(croppedFace)

                        if len(alignFace) != 0 and checkFace.estimateDistance(bbox):
                            # and videoProcess.is_alive_face(alignFace):
                            embedding = checkFace.get_embedding(alignFace)
                            id_user, distances = checkFace.calculateSimilarity(embedding)
                            if checkFace.check_condition_in_1_second(id_user, distances):
                                await websocket.send_json({'type': 'submit',
                                                    'message': f'User {id_user}, độ tương đồng {distances}'})
                                users = db.query(user).filter(user.id == id_user).first()
                                await websocket.send_json({'type': 'user',
                                                           'id': users.id, 'token': users.password, 'username': users.username})
                            # else:
                            #     await websocket.send_json({'type': 'submit',
                            #                                 'message': 'Không tìm thấy khuôn mặt tương đồng!'})
                            await websocket.send_json({'type': 'text',
                                                       'message': 'Đang quét!'})
                        else: 
                            await websocket.send_json({'type': 'text',
                                                   'message': 'Khuôn mặt quá xa camera hoặc không nhận diện được'})
                    
                    # Mã hóa chuỗi trước khi đưa vào wesocket
                    encodeImage = checkFace.encodeImage() 
                    # Đưa dữ liệu vào websocket 
                    await websocket.send_text(f'data:image/jpeg;base64,{encodeImage}')
            # await asyncio.sleep(0.25) # đợi 0.25 giây mới thực hiện tiếp vòng lặp tiếp theo


    except WebSocketDisconnect:
        cv2.destroyAllWindows()
        print('Disconnect!!!')

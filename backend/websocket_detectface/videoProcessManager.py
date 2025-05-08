import base64
import os
import warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Fix lỗi OpenMP
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
from keras_facenet import FaceNet
from ultralytics import YOLO
import mediapipe as mp
import faiss
from fastapi import WebSocket
import cv2
import numpy as np

class VideoProcessing(object):
    """
    Do websocket được xây dựng để truy xuất dữ liệu nhị phân nên các hình ảnh,
    ký tử, số,... đều phải được mã hóa trước khi được truyền vào websocket. 
    Chính vì thế trước khi xử lý ảnh cần phải qua bước mã hóa hình ảnh.
    """
    def __init__(self):
        self.websocket: WebSocket 
        self.frame = None
        self.max_num_faces = 1 # Số lượng khuôn mặt được nhận dạng tối đa

        # Đọc model yolo trong thư mục
        self.model = YOLO('websocket_detectface/model/yolov11n-face.pt')
        
        # Khởi tạo MediaPipe để tìm các đặc trưng         
        mp_face_mesh =mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=self.max_num_faces, refine_landmarks=True)
        del mp_face_mesh
        
        # Khởi tạo model facenet để trích xuất vector đặc trưng
        self.embedder = FaceNet()

        # Số chiều quy định
        self.embdding_dim = 512

        # Khởi tạo FAISS sử dụng độ đo cosin (IndexFlatIP)
        self.faiss = faiss.IndexFlatIP(self.embdding_dim)

        # Ngưỡng tương đồng
        self.similarity_threshold = 0.8
        # Ngưỡng xác định khuôn mặt
        self.faceDetecting_threshold = 0.3
        
    async def connect(self, websocket: WebSocket):
        self.websocket = websocket
        await self.websocket.accept()
        
    # giải mã chuỗi ký tự từ websocket thành hình ảnh
    def decodeImage(self, data: str):
        # Tách chuỗi base64 thành dữ liệu ảnh
        image_data = data.split(",")[1]  # Loại bỏ phần data:image/jpeg;base64,
        image_data = base64.b64decode(image_data)
        nparr = np.frombuffer(image_data, np.uint8)
        self.frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # mã hóa hình ảnh thành chuỗi ký tự để truyền vào websocket
    def encodeImage(self):
        _, encodeImage = cv2.imencode('.jpg', self.frame)
        encodeImage = encodeImage.tobytes()
        encodeImage = base64.b64encode(encodeImage).decode('utf-8')
        return encodeImage
    
    # Xác định khuôn mặt bằng YOLO -> list[x1, y1, x2, y2] tọa độ của bbox
    def faceDetecting(self) -> list:
        results = self.model(self.frame, conf=self.faceDetecting_threshold, verbose=False)
        self.frame = results[0].plot()
        bbox = []
        for result in results[0].boxes.data.tolist():
            x1, y1, x2, y2, _, _ = result
            bbox = [int(x1), int(y1), int(x2), int(y2)]
        return bbox

    # Kiểm tra người dùng có khoảng cách với camera đủ gần không
    def estimateDistance(self, bbox: list, sizeFace: float = 0.1) -> bool:
        """
        sizeFace: độ lớn diện tích của khuôn mặt so với toàn bộ camera, default = 0.05 là 5% diện tích của camera
        nếu diện tích khuôn mặt nhỏ hơn 5% diện tích camera thì yêu cầu người dùng tiến gần hơn
        """
        x1, y1, x2, y2 = bbox
        # Kiểm tra khoảng cách: Nếu bounding box quá nhỏ, cần phải đưa khuôn mặt gần hơn
        face_area = (x2 - x1) * (y2 - y1)
        frame_area = self.frame.shape[0] * self.frame.shape[1]
        if face_area < frame_area * sizeFace and face_area: # Ví dụ: dưới 5% diện tích frame
            return False
        return True
    
    # Cân bằng lại khuôn mặt khi di chuyển, rung lắc hoặc xoay camera
    def alignFace(self, croppedFace):
            
        face_rgb = cv2.cvtColor(croppedFace, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(face_rgb)
        
        # Tăng độ tương phản
        croppedFace = cv2.equalizeHist(cv2.cvtColor(croppedFace, cv2.COLOR_BGR2GRAY))
        croppedFace = cv2.cvtColor(croppedFace, cv2.COLOR_GRAY2BGR)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_eye = (int(landmarks[3].x * croppedFace.shape[1]), int(landmarks[33].y * croppedFace.shape[0]))
            right_eye = (int(landmarks[263].x * croppedFace.shape[1]), int(landmarks[263].y) * croppedFace.shape[0])

            # Xoay theo góc mắt
            dy = right_eye[1] - left_eye[1]
            dx = right_eye[0] - left_eye[0]
            angle = np.degrees(np.arctan2(dy, dx))
            eyes_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
            M = cv2.getRotationMatrix2D(eyes_center, angle, scale=1)
            align_face = cv2.warpAffine(croppedFace, M, (croppedFace.shape[1], croppedFace.shape[0]))

            return align_face
        
        return croppedFace
    
    # Kiểm tra khuôn mặt thật hay ảnh giả
    def is_alive_face(self, cropped_face, confidence_threshold: int = 90) -> bool:
        """
        Hàm kiểm tra tính 'live' của khuôn mặt.
        Ở đây sử dụng biến thiên của Laplacian làm thủ thuật kiểm tra (giá trị thấp có thể chỉ ra ảnh in hoặc mask).
        Trong thực tế, bạn có thể thay bằng mô hình anti-spoofing chuyên dụng.
        """
        gray = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Ngưỡng xác định có phải người thật hay ảnh giả.
        if laplacian_var < confidence_threshold: 
            return False

        return True

    # Khoanh vùng khuôn mặt cần tính bằng bbox 
    def croppedFace(self, bbox: list):
        x1, y1, x2, y2 = bbox
        cropped_face = self.frame[y1:y2, x1:x2]

        return cropped_face

    # Chuẩn hóa, reshape lại phân vùng khuôn mặt,...
    def get_embedding(self, align_face, rows_dims: int = 160, cols_dims: int = 160):
        face_rgb = cv2.cvtColor(align_face, cv2.COLOR_BGR2RGB)
        face_rgb = cv2.resize(face_rgb, (rows_dims, cols_dims))
        embedding = self.embedder.embeddings([face_rgb])[0]

        return embedding


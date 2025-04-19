from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db, user

# Cấu hình mã hóa token
SECRET_KEY = "matkhau"  # 🔒 đổi thành key bảo mật
ALGORITHM = "HS256"

# FastAPI sẽ tự kiểm tra header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/signin")

def create_access_token(data: dict):
    """
    Tạo JWT không có thời gian hết hạn.
    """
    to_encode = data.copy()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Xác thực token từ người dùng
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực token",
        headers={"Authorization": "Bearer "},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_data = db.query(user).filter(user.id == user_id).first()
    if user_data is None:
        raise credentials_exception
    return user_data

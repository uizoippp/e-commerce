from fastapi import APIRouter, HTTPException, status, Depends
from models.models import User
from database import user, get_db
from sqlalchemy.orm import Session
from auth.auth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt

# định nghĩa url của user, tag dùng để chú thích đường dẫn urlurl
signin = APIRouter(
    tags=['signin']
)

@signin.post('/signin')
async def sign_new_user(form_data: User, db: Session = Depends(get_db)) -> dict:
    
    # user.name đã tồn tại từ database
    user_data = db.query(user).filter(user.username == form_data.username).first()
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    # kiểm tra xem user đã tồn tại chưa nếu không thì trả về lỗi
    if user_data.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Sai tài khoản'
            )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    access_token = create_access_token(data={'sub': str(user_data.id)})
    # nếu user và password đúng thì trả về id và mật khẩu đã mã hóa của user
    return {
        "token": access_token,
        "token_type": "bearer",
        "id": user_data.id,
        "username": user_data.username
    }
    
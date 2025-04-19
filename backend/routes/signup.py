from fastapi import APIRouter, HTTPException, status, Depends
from models.models import User
from database import user, get_db
from sqlalchemy.orm import Session
from auth.auth import create_access_token

# định nghĩa url của user, tag dùng để chú thích đường dẫn urlurl
signup = APIRouter(
    tags=['signup']
)


@signup.post('/signup/')
async def sign_new_user(request: User, db: Session = Depends(get_db)) -> dict:
    # user.name đã tồn tại từ database
    if not request.username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No user name'
        )
    users = db.query(user).filter(user.username == request.username).first()
    # kiểm tra xem user đã tồn tại chưa nếu có thì trả về lỗi
    if users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied username existed"
        )
    new_user = user(username=request.username, password=request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={'sub': str(new_user.id)})
    return {
        "token": access_token,
        "token_type": "bearer",
        "id": new_user.id,
        "username": new_user.username
    }



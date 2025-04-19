from pydantic import BaseModel, Field
from datetime import datetime
from datetime import datetime
from typing import Union, Optional

'''
Định nghĩa lớp User (lớp phụ) sử dụng Pydantic
đây là lớp User để nhận dữ liệu từ frontend 
và kiểm tra các ràng buộc, chứng thực dữ liệu trước khi
truyền vào lớp user (lớp chính) được lưu trong csdl
'''
class User(BaseModel):
    id: Union[int, None] = Field(None) # nếu không có giá trị trường này sẽ none
    username: Union[str, None] = Field(None, max_length=50) # có giá trị sẽ chuyển sang trường Field. Xét điều kiện Field, nếu vượt quá 50 ký tự thì none hoặc giữ nguyên giá trị
    password: Union[str, None] = Field(None, max_length=64)
    phone: Union[str, None] = Field(None, max_length=10) # có giá trị sẽ chuyển sang trường Field. Xét điều kiện Field, nếu vượt quá 10 ký tự thì none hoặc giữ nguyên giá trị
    create_date: datetime = datetime.utcnow()

    class Config:
        from_attributes  = True  # Để Pydantic tương thích với SQLAlchemy (ORM)

class Product(BaseModel):
    id: Union[int, None] = Field(None) # nếu không có giá trị trường này sẽ none
    name: str
    description: Optional[str]
    price: float
    create_date: datetime = Field(default_factory=datetime.utcnow)
    image_url: str

    class Config:
        from_attributes = True


class Cart(BaseModel):
    id: Union[int, None] = Field(None) # nếu không có giá trị trường này sẽ none
    id_product: int
    quantity: int
    id_user: int
    create_date: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class Order(BaseModel):
    id: Union[int, None] = Field(None)
    id_user: int
    id_product: int
    total_price: float
    name_product: str
    quantity_product: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class CartIn(BaseModel):
    id_product: int
    quantity: int
    id_user: int

    class Config:
        from_attributes = True

class ListCart(BaseModel):
    id_product: int
    image_url: str
    name: str
    price_one_product: float
    quantity: int

    class Config:
        from_attributes = True

class UpdateCartIn(BaseModel):
    id_product: int
    quantity: float

    class Config:
        from_attributes = True

class IdProduct(BaseModel):
    id_product: int

    class Config:
        from_attributes = True

class Webs(BaseModel):
    id: Optional[int]
    source_url: Optional[str]
    title: Optional[str]
    vector: Optional[list[float]]

    class Config:
        from_attributes = True

class Chunks(BaseModel):
    id: Optional[int]
    parent_id: Optional[int]
    chunk_index: Optional[int]
    text: Optional[str]
    vector: Optional[list[float]]

    class Config:
        from_attributes = True
'''
khi muốn cập nhật csdl, cần phải đi qua 1 lớp chứng thực, kiểm tra các ràng buộc
thông qua lớp User (lớp phụ) trước khi tương tác với csdl tại lớp user chính
'''
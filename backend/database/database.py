from sqlalchemy import Column, Integer, JSON, String, DateTime, ForeignKey, Text, Double
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship, backref
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Tạo base class cho SQLAlchemy
Base = declarative_base() 
# Lớp Base sẽ lưu lại toàn bộ các bảng đã định nghĩa từ trước để khởi tạo cơ sở dữ liệu thông qua các bảng đã lưu sẵn trong Base

'''
Định nghĩa lớp User trong database.db
Đây là lớp chính dùng để lưu trữ trong csdl 
và dùng để quy định ràng buộc 
'''
class user(Base):
    __tablename__ = 'users'

    # ràng buộc index là chỉ mục. Dùng để tăng hiệu suất truy xuất cho thuộc tính
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False) 
    password = Column(String(64), nullable=False) # nullable không cho phép để trống
    phone = Column(String(10), nullable=True) # nullable cho phép để trống
    create_date = Column(DateTime, default=datetime.utcnow())

    carts = relationship('cart', back_populates='user')
    orders = relationship("order", back_populates="user")
    vectors = relationship('vectorUser', back_populates='user')

    def __repr__(self):
        return f'User {self.id}, name {self.username}, create_date {self.create_date}'
    
class product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    price = Column(Double, nullable=False)
    description = Column(Text, nullable=True)
    create_date = Column(DateTime, default=datetime.utcnow())
    image_url = Column(String(250), nullable=False)

    carts = relationship('cart', back_populates='product')
    orders = relationship('order', back_populates='product')

    def __repr__(self):
        return f'Product {self.id}, name {self.name}, price {self.price}, create_date {self.create_date}'

class cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    id_product = Column(Integer, ForeignKey('products.id'))
    create_date = Column(DateTime, default=datetime.utcnow())
    quantity = Column(Integer, default=1)

    user = relationship('user', back_populates='carts')
    product = relationship('product', back_populates='carts')

class order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    id_product = Column(Integer, ForeignKey('products.id'))
    name_product = Column(String(50), nullable=False)
    quantity_product = Column(Integer, default=1)
    create_date = Column(DateTime, default=datetime.utcnow())
    total_price = Column(Double, nullable=False)

    product = relationship('product', back_populates='orders')
    user = relationship('user', back_populates='orders')

class vectorUser(Base):
    __tablename__ = 'vectorsEmbedding'

    id = Column(Integer, primary_key=True, index=True)
    vector = Column(Text, nullable=True)
    id_user = Column(Integer, ForeignKey('users.id'))

    user = relationship('user', back_populates='vectors')

class webs(Base):
    __tablename__ = 'webs'
    """
    Mỗi một đối tượng tri thức nền là 1 trang web
    Một trang web có một khối thông tin
    Một khối thông tin được chia thành nhiều đoạn (chunks)
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    vector = Column(JSON, nullable=True)

    chunks = relationship('chunks', back_populates='web')

class chunks(Base):
    __tablename__ = 'chunks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('webs.id'), nullable=False)
    chunk_index = Column(Integer, nullable=False) # số thứ tự của đoạn này trong một trang web
    text = Column(Text, nullable=False)
    vector = Column(JSON, nullable=False)

    web = relationship('webs', back_populates='chunks')

# Cấu hình kết nối cơ sở dữ liệu SQLite
engine = create_engine('sqlite:///database.db')

# Khởi tạo engine và session
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()




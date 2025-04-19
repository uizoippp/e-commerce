from database import Base, engine

if __name__ == '__main__':
    # Khởi tạo csdl
    Base.metadata.create_all(bind=engine)
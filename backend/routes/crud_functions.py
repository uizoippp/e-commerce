from database import user, product, order, cart
from models.models import *
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status
import os

# USER CRUD
def create_user(user: User, db: Session) -> User:
    db_user = db.User(username=user.username, password=user.password, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session) -> List[User]:
    return db.query(db.User).all()

def get_user(user_id: int, db: Session) -> User:
    return db.query(user).filter(user.id == user_id).first()

def delete_user(user_id: int, db: Session) -> User:
    user = get_user(user_id=user_id, db=db)
    if user:
        db.delete(user)
        db.commit()
    return user

# PRODUCT CRUD
def create_product(product_data: Product, db: Session) -> Product:
    db_product = product(name=product_data.name, price=product_data.price, description=product_data.description, image_url=product_data.image_url)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session) -> List[Product]:
    return db.query(product).all()

def update_product(product_data: Product, db: Session) -> Product:
    data = db.query(product).filter(product.id == product_data.id).first()
    if data:
        for key, value in product_data.dict().items():
            if value is not None:
                setattr(data, key, value)

        db.commit()
        db.refresh(data)
    return data

def delete_product(product_id: int, db: Session) -> Product | dict:
    try:
        data = db.query(product).filter(product.id == product_id).first()
        db.delete(data)
        db.commit()
        if data.image_url and os.path.exists(data.image_url):
            os.remove(data.image_url)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm"
        )

# CART CRUD
def add_to_cart(user_id: int, cartIn: CartIn, db: Session) -> Cart:
    check_cart = db.query(cart).filter(cart.id_user == user_id, cart.id_product == cartIn.id_product).first()
    if check_cart:
        check_cart.quantity += cartIn.quantity
        db.commit()
        db.refresh(check_cart)
        return check_cart
    db_cart = cart(id_user=user_id, id_product=cartIn.id_product, quantity=cartIn.quantity) 
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def get_cart(user_id: int, db: Session) -> List[Cart]:
    return db.query(cart).filter(cart.id_user == user_id).all()

def get_cart_by_userid(product_id: int, user_id: int, db: Session) -> Cart:
    try:
        cart_item = db.query(cart).filter(cart.id_product == product_id, cart.id_user == user_id).first()
        db.commit()
        db.refresh(cart_item)
        return cart_item
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy giỏ hàng"
        )

# ORDER CRUD
def create_order(user_id: int, db: Session) -> list[order]:
    # 1. Lấy sản phẩm trong giỏ hàng của user
    cart_items = db.query(cart).filter(cart.id_user == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Giỏ hàng đang trống")

    orders_created = []

    for item in cart_items:
        product_name = db.query(product).filter(product.id == item.id_product).first()
        data = db.query(product).filter(product.id == item.id_product).first()
        if not data:
            continue  # Bỏ qua nếu sản phẩm không tồn tại

        # 2. Tính tổng giá tiền
        price = data.price * item.quantity

        # 3. Tạo đơn hàng
        new_order = order(
            id_user=user_id,
            id_product=data.id,
            quantity_product=item.quantity,
            total_price=price,
            name_product=product_name.name,
        )
        db.add(new_order)
        orders_created.append(new_order)

    # 4. Xoá giỏ hàng sau khi tạo đơn
    db.query(cart).filter(cart.id_user == user_id).delete()

    db.commit()
    return orders_created

def get_orders(user_id: int, db: Session) -> List[Order] | dict:
    try: 
        return db.query(order).filter(order.id_user == user_id).all()
    except Exception as e:
        raise status(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Có order nào trong cơ sở dữ liệu"
        )
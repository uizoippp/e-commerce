from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from .crud_functions import *
from models.models import Product, Cart, Order
from database import get_db
from auth.auth import get_current_user

user_route = APIRouter(
    tags=['user']
)

@user_route.delete('/delete/{id}')
async def delete_user_by_id(user_id: int, db: Session = Depends(get_db)) -> dict:
    user = delete_user(user_id=user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

product_route = APIRouter(
    tags=['product']
)

@product_route.post('/create', response_model=Product)
async def create_new_product(name: str = Form(...), description: str = Form(...), price: float = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    file_location = f'media/images/{image.filename}'
    with open(file_location, 'wb') as f:
        f.write(image.file.read())
    product_data = Product(id=None, name=name, description=description, price=price, image_url=file_location)
    try:
        data = create_product(product_data, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return data

@product_route.get('/get/{id}', response_model=Product)
async def get_product_by_id(id: int, db: Session = Depends(get_db)) -> dict:
    data = db.query(product).filter(product.id == id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return data

@product_route.get('/get')
async def get_all_products(db: Session = Depends(get_db)) -> List[Product]:
    return get_products(db=db)

@product_route.put('/update/{id}')
async def update_product_by_id(product: Product, db: Session = Depends(get_db)) -> dict:
    data = update_product(product, db)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    # Update product details
    return {"message": f"Product {data.id} updated successfully"}

@product_route.delete('/delete/{id}')
async def delete_product_by_id(product_id: int, db: Session = Depends(get_db)) -> dict:
    product = delete_product(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return {'message': f'Delete product {product.id} successfully!'}

cart_route = APIRouter(
    tags=['cart']
)

@cart_route.post('/add/user', response_model=Cart)
async def add_cart(cartIn: CartIn, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> dict | Cart:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Không có quyền thao tác'
        )
    cart = add_to_cart(current_user.id, cartIn, db)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Có lỗi khi thêm giỏ hàng"
        )
    return cart

@cart_route.get('/get/user', response_model=List[ListCart])
async def get_cart_by_user_id(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> List[ListCart]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Không có quyền thao thác'
        )

    carts = get_cart(current_user.id, db)
    if not carts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy giỏ hàng"
        )
    result_data = []
    for cart in carts:
        data = db.query(product).filter(product.id == cart.id_product).first()
        if data:
            result_data.append(ListCart(id_product=data.id, 
                                        image_url=data.image_url, 
                                        name=data.name, 
                                        price_one_product=data.price, 
                                        quantity=cart.quantity
                                        ))
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

    return result_data

@cart_route.post('/update/user', response_model=List[ListCart])
async def update_cart_by_user_id(data: UpdateCartIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> List[ListCart]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Không có quyền thao thác'
        )

    cart_item = get_cart_by_userid(data.id_product, current_user.id, db)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    cart_item.quantity += data.quantity
    if cart_item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )
    db.commit()
    db.refresh(cart_item)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    result_data = []
    carts = db.query(cart).filter(cart.id_user == current_user.id).all()
    for cart_1 in carts:
        data = db.query(product).filter(product.id == cart_1.id_product).first()
        if data:
            result_data.append(ListCart(id_product=data.id, 
                                        image_url=data.image_url, 
                                        name=data.name, 
                                        price_one_product=data.price, 
                                        quantity=cart_1.quantity
                                        ))
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

    return result_data

@cart_route.delete('/delete/user', response_model=List[ListCart])
async def delete_cart_by_user_id(data: IdProduct, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> List[ListCart]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Không có quyền thao thác'
        )
    cart_item = db.query(cart).filter(cart.id_product == data.id_product, cart.id_user == current_user.id).all()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    for item in cart_item:
        db.delete(item)

    db.commit()
    result_data = []
    carts = db.query(cart).filter(cart.id_user == current_user.id).all()
    for cart_1 in carts:
        data = db.query(product).filter(product.id == cart_1.id_product).first()
        if data:
            result_data.append(ListCart(id_product=data.id, 
                                        image_url=data.image_url, 
                                        name=data.name, 
                                        price_one_product=data.price, 
                                        quantity=cart_1.quantity
                                        ))
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

    return result_data

order_route = APIRouter(
    tags=['order']
)

@order_route.post('/create/user', response_model=list[Order])
async def create_order_by_user_id(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> list[Order]:
    order = create_order(current_user.id, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@order_route.get('/get/user', response_model=List[Order])
async def get_all_order_by_user_id(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> List[Order]:
    orders = get_orders(current_user.id, db)
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orders not found"
        )
    return orders

test_routes = APIRouter(
    tags=['test']
)

@test_routes.get('/test')
async def test_route(current_user = Depends(get_current_user)) -> dict:
    return {"message": "Test route is working!"}
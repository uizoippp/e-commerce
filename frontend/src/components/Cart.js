import Header from "../layout/Header";
import Footer from "../layout/Footer";
import React, { useState, useEffect } from 'react';
import axios from "axios";
import { useNavigate } from 'react-router-dom';

export default function Cart() {
    const [cartItems, setCartItems] = useState([]);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        axios.get(`http://127.0.0.1:8000/cart/get/user`,
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
            }
        )
            .then((response) => setCartItems(response.data))
            .catch((error) => console.error("Lỗi khi gọi API:", error));
    }, []);

    const checkOut = async (e) => {
        e.preventDefault();
        await axios.post(`http://127.0.0.1:8000/order/create/user`, {},
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
            }
        )
            .then((response) => {
                alert("Đặt hàng thành công!");
                navigate('/payment-history');
            })
            .catch((error) => setError(error.response.data.detail));
    }

    const handleQuantityChange = async (index, amount) => {
        setError(null); // Reset error message
        setCartItems((prevItems) =>
            prevItems.map((item, index_1) =>
                index_1 === index
                    ? { ...item, quantity: Math.max(1, item.quantity + amount) }
                    : item
            )
        );
        const cartItem = cartItems.find((_, i) => i === index);
        if (cartItem) {
            const quantity_data = amount;
            const id_product = cartItem.id_product;
            // dùng quantity_data & id_product ở đây
            await axios.post(`http://127.0.0.1:8000/cart/update/user`,
                {
                    quantity: quantity_data,
                    id_product: id_product
                },
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`
                    },
                }
            )
                .then((response) => setCartItems(response.data))
                .catch((error) => setError(error.response.data.detail));

        }


    };

    const handleRemove = async (id_product) => {
        await axios.delete(`http://127.0.0.1:8000/cart/delete/user`, {
            data: {
                id_product: id_product
            },
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`
            },
        }
        )
            .then((response) => setCartItems(response.data))
            .catch((error) => setError(error.response.data.detail));


    };

    const total = cartItems.reduce((sum, item) => sum + item.price_one_product * item.quantity, 0);

    return (
        <>
            <Header />
            <div className="cart-container">
                <h2>🛒 Giỏ hàng</h2>
                {cartItems.length === 0 ? (
                    <p>Không có sản phẩm nào trong giỏ.</p>
                ) : (
                    <div>
                        {cartItems.map((item, index) => (
                            <div className="cart-item" key={index}>
                                <img src={`http://127.0.0.1:8000/${item.image_url}`} alt={item.name} />
                                <div className="cart-info">
                                    <h4>{item.name}</h4>
                                    <p>Giá: {item.price_one_product.toLocaleString()}₫</p>
                                    <div className="quantity-controls">
                                        <button onClick={() => handleQuantityChange(index, -1)}>-</button>
                                        <span>{item.quantity}</span>
                                        <button onClick={() => handleQuantityChange(index, 1)}>+</button>
                                    </div>
                                    {error === null ? (null) : (
                                        <p style={{ color: "red" }}>{error}</p>
                                    )}
                                    <p>Tổng: {(item.price_one_product * item.quantity).toLocaleString()}₫</p>
                                    <button className="remove-btn" onClick={() => handleRemove(item.id_product)}>🗑 Xóa</button>
                                </div>
                            </div>
                        ))}
                        <hr />
                        <h3>Tổng cộng: {total.toLocaleString()}₫</h3>
                        <button type="submit" onClick={(e) => checkOut(e)} className="checkout-btn">Thanh toán</button>
                    </div>
                )}
            </div>
            <Footer />
        </>
    );
}


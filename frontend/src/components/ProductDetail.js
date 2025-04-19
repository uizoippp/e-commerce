import React, { useState } from "react";
import Header from "../layout/Header";
import Footer from "../layout/Footer";
import { useEffect } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";


export default function ProductDetailPage() {
    const { id } = useParams(); // 👈 lấy tham số "id" từ URL
    const [product, setProducts] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        axios.get(`http://127.0.0.1:8000/product/get/${id}`)
            .then((response) => setProducts(response.data))
            .catch((error) => console.error("Lỗi khi gọi API:", error));
    }, []);

    const handleBuy = async (idProduct) => {
        if (!localStorage.getItem("token")) {
            alert('Hãy đăng nhập trước khi mua hàng!');
            navigate('/login');
            return;
        }

        try {
            const data = {
                id_product: product.id,
                id_user: localStorage.getItem('userid'),
                quantity: 1,
            };
            const res = await axios.post(
                `http://127.0.0.1:8000/cart/add/user`, data,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`
                    }
                }
            );
            alert("Đặt hàng thành công!");
            navigate('/');
        } catch (error) {
            alert("Đặt hàng thất bại: " + error.response.data.detail || "Lỗi không xác định");
        }
    };

    if (!product) return (<p>Đang tải sản phẩm...</p>)
    if (product) return (
        <>
            <Header />
            <div className="product-container">
                <div className="product-image">
                    <img src={`http://127.0.0.1:8000/${product.image_url}`} alt={product.name} />
                </div>
                <div className="product-info">
                    <h1>{product.name}</h1>
                    <p className="description">{product.description}</p>
                    <p className="price">{product.price} ₫</p>
                    <button onClick={(e) => handleBuy(id, e)} className="add-to-cart-btn">Thêm vào giỏ hàng</button>
                    <p className="details">{product.details}</p>
                </div>
            </div>
            <Footer />
        </>
    );
}

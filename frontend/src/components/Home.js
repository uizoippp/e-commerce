import Header from "../layout/Header";
import Footer from "../layout/Footer";
import { useEffect, useState } from 'react';
import axios from "axios";
import { useNavigate } from "react-router-dom";

const ProductList = () => {
    const [products, setProducts] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        axios.get("http://127.0.0.1:8000/product/get")
            .then((response) => setProducts(response.data))
            .catch((error) => console.error("Lỗi khi gọi API:", error));
    }, []);

    const handleCheckDetail = async (idProduct) => {
        navigate(`/productdetail/${idProduct}`);
    };

    const handleBuyProduct = async (product) => {
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
        } catch (error) {
            alert("Đặt hàng thất bại: " + error.response.data.detail || "Lỗi không xác định");
        }
    };

    return (
        <div className="row">
            {products.map((product) => (
                <div key={product.id} className="col-sm-6 col-md-4 col-lg-3">
                    <div className="box">
                        <div className="img-box">
                            <img style={{cursor: 'pointer'}} onClick={() => handleCheckDetail(product.id)} src={`http://127.0.0.1:8000/${product.image_url}`} alt={product.name} />
                        </div>
                        <div className="detail-box">
                            <h6 style={{cursor: 'pointer'}} onClick={() => handleCheckDetail(product.id)}>{product.name}</h6>
                            <h6>
                                Price<br />
                                <span>{product.price} VND</span>
                            </h6>
                        </div>
                        <button onClick={() => handleBuyProduct(product)}>Mua</button>
                        <div className="new">
                            <span>New</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default function Home() {

    return (
        <>
            <Header />
            <div className="hero_area">
                <section className="slider_section">
                    <div className="slider_container">
                        <div id="carouselExampleIndicators" className="carousel slide" data-ride="carousel">
                            <div className="carousel-inner">
                                <div className="carousel-item active">
                                    <div className="container-fluid">
                                        <div className="row">
                                            <div className="col-md-7">
                                                <div className="detail-box">
                                                    <h1>
                                                        Welcome To Our <br />
                                                        Gift Shop
                                                    </h1>
                                                    <p>
                                                        Sequi perspiciatis nulla reiciendis, rem, tenetur impedit, eveniet non necessitatibus error distinctio mollitia suscipit. Nostrum fugit doloribus consequatur distinctio esse, possimus maiores aliquid repellat beatae cum, perspiciatis enim, accusantium perferendis.
                                                    </p>
                                                    <a href="">
                                                        Contact Us
                                                    </a>
                                                </div>
                                            </div>
                                            <div className="col-md-5 ">
                                                <div className="img-box">
                                                    <img src="images/slider-img.png" alt="" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="carousel-item ">
                                    <div className="container-fluid">
                                        <div className="row">
                                            <div className="col-md-7">
                                                <div className="detail-box">
                                                    <h1>
                                                        Welcome To Our <br />
                                                        Gift Shop
                                                    </h1>
                                                    <p>
                                                        Sequi perspiciatis nulla reiciendis, rem, tenetur impedit, eveniet non necessitatibus error distinctio mollitia suscipit. Nostrum fugit doloribus consequatur distinctio esse, possimus maiores aliquid repellat beatae cum, perspiciatis enim, accusantium perferendis.
                                                    </p>
                                                    <a href="">
                                                        Contact Us
                                                    </a>
                                                </div>
                                            </div>
                                            <div className="col-md-5 ">
                                                <div className="img-box">
                                                    <img src="images/slider-img.png" alt="" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="carousel-item ">
                                    <div className="container-fluid">
                                        <div className="row">
                                            <div className="col-md-7">
                                                <div className="detail-box">
                                                    <h1>
                                                        Welcome To Our <br />
                                                        Gift Shop
                                                    </h1>
                                                    <p>
                                                        Sequi perspiciatis nulla reiciendis, rem, tenetur impedit, eveniet non necessitatibus error distinctio mollitia suscipit. Nostrum fugit doloribus consequatur distinctio esse, possimus maiores aliquid repellat beatae cum, perspiciatis enim, accusantium perferendis.
                                                    </p>
                                                    <a href="">
                                                        Contact Us
                                                    </a>
                                                </div>
                                            </div>
                                            <div className="col-md-5 ">
                                                <div className="img-box">
                                                    <img src="images/slider-img.png" alt="" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>

            <section className="shop_section layout_padding">
                <div className="container">
                    <div className="heading_container heading_center">
                        <h2>
                            Latest Products
                        </h2>
                    </div>
                    <ProductList />
                    {/* <div className="btn-box">
                        <a href="">
                            View All Products
                        </a>
                    </div> */}
                </div>
            </section>

            <Footer />
        </>
    )
}
import React from "react";
import { Link, useNavigate  } from "react-router-dom";



export default function Navbar() {
    const navigate = useNavigate(); // ✅ OK vì nằm trong component

    const clearUser = () => {
        window.localStorage.removeItem('userid');
        window.localStorage.removeItem('username');
        window.localStorage.removeItem('token');
        navigate('/');
    }

    return (
        <nav className="navbar navbar-expand-lg custom_nav-container ">
            <a className="navbar-brand" href="/">
                <span>
                    Giftos
                </span>
            </a>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span className=""></span>
            </button>

            <div className="collapse navbar-collapse" id="navbarSupportedContent">
                <ul className="navbar-nav  ">
                    <li className={window.location.pathname === '/' ? 'nav-item active' : 'nav-item'} >
                        <Link className="nav-link" to="/">
                            Home
                        </Link>
                    </li>
                    <li className={window.location.pathname === '/shop' ? 'nav-item active' : 'nav-item'} >
                        <Link className="nav-link" to="/shop">
                            Shop
                        </Link>
                    </li>
                    <li className={window.location.pathname === '/why' ? 'nav-item active' : 'nav-item'} >

                        <Link className="nav-link" to="/payment-history">
                            LỊch sử đơn hàng
                        </Link>
                    </li>
                    <li className={window.location.pathname === '/chat' ? 'nav-item active' : 'nav-item'} >

                        <Link className="nav-link" to="/chat">
                            Chat
                        </Link>
                    </li>
                    <li className={window.location.pathname === '/contact' ? 'nav-item active' : 'nav-item'} >

                        <Link className="nav-link" to="/contact">Contact Us</Link>
                    </li>
                </ul>
                <div className="user_option">

                    {window.localStorage.getItem('userid') === null ? (
                        <>
                            <Link to="/login">
                                <i className="fa fa-user" aria-hidden="true"></i>
                                <span>Đăng nhập</span>
                            </Link>
                            <Link to="/register">
                                <i className="fa fa-user" aria-hidden="true"></i>
                                <span>
                                    Đăng ký
                                </span>
                            </Link>
                            <Link to="/cart">
                                <i className="fa fa-shopping-bag" aria-hidden="true"></i>
                            </Link>
                        </>
                    ) : (
                        <>
                            <Link >
                                <i className="fa fa-user" aria-hidden="true"></i>
                                <span>{window.localStorage.getItem('username')}</span>
                            </Link>
                            <Link>
                                <i className="fa fa-user" aria-hidden="true"></i>
                                <span onClick={clearUser}>
                                    Đăng xuất
                                </span>
                            </Link>
                            <Link to="/cart">
                                <i className="fa fa-shopping-bag" aria-hidden="true"></i>
                                <span>Giỏ hàng</span>
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    )
}

import Header from "../layout/Header";
import Footer from "../layout/Footer";
import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link, data } from "react-router-dom";
import SHA256 from 'crypto-js/sha256';

export default function Login() {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    const navigate = useNavigate();

    const [error, setError] = useState('');

    async function handleSubmit(event) {
        event.preventDefault();
        // Handle form submission logic here
        if (!formData.userName || !formData.password) {
            setError('Please fill in all fields');
            return;
        };
        // Example API call using axios
        // Hash SHA-256 the password before sending it to the server 
        const hashedPassword = SHA256(formData.password);

        const data = {
            'username': formData.userName,
            'password': hashedPassword.toString(),
        };

        await axios.post('http://127.0.0.1:8000/user/signin', data)
            .then(response => {
                // store the token in local storage or context
                localStorage.setItem('token', response.data.token);
                localStorage.setItem('userid', response.data.id);
                localStorage.setItem('username', response.data.username);
                // Redirect to home page
                navigate('/');

            })
            .catch(error => {
                // Handle error response
                if (error.response && error.response.status === 401) {
                    setError(error.response.data.detail);
                };
                if (error.response && error.response.status === 404) {
                    setError(error.response.data.detail);
                };
            });
    }

    function handleChange(event) {
        // Handle input change logic here
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    };


    return (
        <>
            <Header />
            <section className="contact_section layout_padding login_section">
                <div className="container px-0">
                    <div className="heading_container " style={{ alignItems: 'center' }}>
                        <h2 className="">
                            Đăng nhập tài khoản
                        </h2>
                        {error && <p style={{ color: 'red' }}>{error}</p>}
                    </div>
                </div>
                <div className="container container-bg ">
                    <div className="px-0" style={{ width: '100%' }}>
                        <form action="#">
                            <div>
                                <input
                                    type="text"
                                    placeholder="Tên đăng nhập"
                                    name="userName"
                                    value={formData.userName}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <input type="password"
                                    placeholder="Mật khẩu"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="d-flex">
                                <button onClick={handleSubmit} type="submit">
                                    Đăng nhập
                                </button>
                            </div>
                                <Link to='/register' style={{float: 'rigth', paddingRigth: '1.5rem'}}>Đăng ký</Link>
                        </form>
                    </div>
                </div>
            </section>
            <Footer />
        </>
    )
}

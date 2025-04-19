import React, { useEffect, useState } from "react";
import axios from "axios";
import Header from "../layout/Header";
import Footer from "../layout/Footer";


const PaymentHistory = () => {
    const [payments, setPayments] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchPayments = async () => {
            try {
                const res = await axios.get("http://127.0.0.1:8000/order/get/user", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`
                    }
                });
                setPayments(res.data);
            } catch (error) {
                setError(error.response?.data?.detail || "Lỗi khi tải lịch sử thanh toán");
            }
        };

        fetchPayments();
    }, []);

    return (
        <>
            <Header />
            <div className="payment-history">
                <h2>Lịch sử thanh toán</h2>
                {error && <p style={{ color: "red" }}>{error}</p>}
                {payments.length === 0 ? (
                    <p>Không có giao dịch nào.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Sản phẩm</th>
                                <th>Giá</th>
                                <th>Số lượng</th>
                                <th>Tổng</th>
                                <th>Ngày thanh toán</th>
                            </tr>
                        </thead>
                        <tbody>
                            {payments.map((payment, index) => (
                                <tr key={index}>
                                    <td>{index + 1}</td>
                                    <td>{payment.name_product}</td>
                                    <td>{(payment.total_price / payment.quantity_product).toLocaleString()}₫</td>
                                    <td>{payment.quantity_product}</td>
                                    <td>{payment.total_price.toLocaleString()}₫</td>
                                    <td>{new Date(payment.created_at.replace(" ", "T")).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
            <Footer />
        </>
    );
};

export default PaymentHistory;

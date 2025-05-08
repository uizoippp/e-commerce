import React from "react";
import Header from "../layout/Header";
import Footer from "../layout/Footer";
import { useEffect, useState, useRef } from "react";

function sendImageToWebSocket(img) {
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        // Chuyển canvas thành base64
        const dataUrl = canvas.toDataURL("image/jpeg");
        return dataUrl;
    }
    catch (e) {
        console.log(e);
        return null;
    }
}

export default function FaceID() {
    const [title, setTitle] = useState('Login via Face ID');
    const [ipcamera, setIpcamera] = useState('http://192.168.100.2:8080/video');
    const [previousImage, setPreviousImage] = useState('');
    const [message, setMessage] = useState('');
    const [sendImage] = useState(500);
    const [isSending, setIsSending] = useState(true);
    const wsRef = useRef(null);

    const submitImage = () => {
        wsRef.current.send('submit');
        setIsSending(false);
    }

    useEffect(() => {
        const socket = new WebSocket(`ws://127.0.0.1:8000/ws/stream/${window.localStorage.getItem('userid')}`);
        wsRef.current = socket;

        socket.onopen = () => {
            console.log("Kết nối WebSocket thành công");

            const imageElement = document.getElementById('camera');
            const interval = setInterval(() => {
                if (imageElement && isSending) {
                    const dataUrl = sendImageToWebSocket(imageElement);
                    if (previousImage !== dataUrl && wsRef.current.readyState === WebSocket.OPEN) {
                        wsRef.current.send(dataUrl);
                        setPreviousImage(dataUrl);
                    }
                }
            }, sendImage);

            // Clear interval when unmount
            return () => clearInterval(interval);
        };

        socket.onmessage = (event) => {
            const data = event.data;
            setMessage(data.message);
        };

        socket.onclose = () => {
            console.log("WebSocket bị đóng");
        };

        socket.onerror = (error) => {
            console.error("WebSocket lỗi:", error);
        };

        return () => {
            socket.close();
        };
    }, []);

    return (
        <>
            <Header />
            {isSending ? (<section className="contact_section layout_padding login_section">
                <div className="container px-0">
                    <div className="heading_container " style={{ alignItems: 'center' }}>
                        <h2 className="">
                            Đăng nhập khuôn mặt {message}
                        </h2>
                        {message && <p style={{ color: 'red' }}>{message}</p>}
                    </div>
                </div>
                <div className="container container-bg ">
                    <div className="px-0" style={{ width: '100%' }}>
                        <img id="camera" className="card-img-top" crossOrigin="anonymous" src={ipcamera} alt="" style={{ width: 'auto', height: '480px' }} />
                        {message == 'Bạn có thể gửi ảnh!' && <button onClick={submitImage}>Xác nhận khuôn mặt</button>}
                    </div>
                </div>
            </section>) : <h1>Tạo face ID thành công</h1>}
            <Footer />
        </>
    )
}

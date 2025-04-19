import React, { useState } from "react";
import Header from "../layout/Header";
import Footer from "../layout/Footer";
import { useEffect, useRef } from "react";

const Message = ({ sender, text }) => {
    const isUser = sender === "user";
    return (
        <div className={`message-row ${isUser ? "user" : "bot"}`}>
            <div className="message-bubble">
                {text}
            </div>
        </div>
    );
};


const ChatPage = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const chatEndRef = useRef(null);
    const [ws, setWs] = useState(null);
    const [isTyping, setIsTyping] = useState(false);

    useEffect(() => {
        const socket = new WebSocket('ws://127.0.0.1:8000/ws/chatroom');

        socket.onopen = () => {
            console.log("Kết nối WebSocket thành công");
        };

        socket.onmessage = (event) => {
            console.log("Tin nhắn từ server:", event.data);
            setMessages((prev) => [
                ...prev,
                { sender: "bot", text: event.data },
            ]);
            setIsTyping(false); // Bot đã phản hồi xong
        };

        socket.onclose = () => {
            console.log("WebSocket bị đóng");
        };

        socket.onerror = (error) => {
            console.error("WebSocket lỗi:", error);
        };
        setWs(socket);

    }, [messages]);

    const sendMessage = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const newMessage = { sender: "user", text: input };
        if (ws) {
            ws.send(input);
            setIsTyping(true); // Bắt đầu đợi phản hồi
        }
        setMessages((prev) => [...prev, newMessage]);
        setInput("");
    };

    return (
        <>
            <Header />
            <div className="chat-wrapper">
                <h2 className="chat-title">💬 Trò chuyện trực tuyến</h2>
                <div className="chat-box">
                    {messages.map((msg, idx) => (
                        <Message key={idx} sender={msg.sender} text={msg.text} />
                    ))}
                    {/* 👇 Hiệu ứng "Bot đang trả lời..." */}
                    {isTyping && (
                        <div className="message-row bot typing-indicator">
                            <div className="message-bubble">...</div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>
                <form className="chat-input-area" onSubmit={sendMessage}>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Nhập tin nhắn..."
                        disabled={isTyping}
                    />
                    <button type="submit" disabled={isTyping}>
                        {isTyping ? "Đang trả lời..." : "Gửi"}
                    </button>
                </form>
            </div>
            <Footer />
        </>
    );
};

export default ChatPage;

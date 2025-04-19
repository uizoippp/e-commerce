import React, { useState } from 'react';
import axios from 'axios';

const StoreCrawl = () => {
    const [url, setUrl] = useState('');
    const [title, setTitle] = useState('');
    const [text, setText] = useState('');
    const [titleSent, setTitleSent] = useState(false);
    const [index, setIndex] = useState('');

    const [idweb, setIdweb] = useState('');
    const [responseUrlTitle, setResponseUrlTitle] = useState('');
    const [responseText, setResponseText] = useState('');

    const handleSendTitle = async () => {
        if (!url.trim() || !title.trim()) return;

        try {
            const response = await axios.post('http://127.0.0.1:8000/crawl/add/web', {
                'title': title,
                'source_url': url,
            });

            setResponseUrlTitle('✅ Đã gửi tiêu đề + URL');
            setTitleSent(true);
            setIdweb(response.data);
        } catch (err) {
            setResponseUrlTitle('❌ Lỗi gửi tiêu đề');
        }
    };

    const refreshPage = () => {
        setUrl('');
        setTitle('');
        setText('');
        setTitleSent(false);
        setIndex('');
        setIdweb('');
        setResponseText('');
        setResponseUrlTitle('');
    };

    const handleSendText = async () => {
        if (!text.trim()) return;

        try {
            const response = await axios.post('http://127.0.0.1:8000/crawl/add/chunk', {
                'id': idweb.id,
                'text': text,
                'index': index
            });
            setText('');
            setIndex('');
            setResponseText('✅ Đã gửi nội dung');
        } catch (err) {
            setResponseText('❌ Lỗi gửi nội dung');
        }
    };

    return (
        <div style={{ maxWidth: 700, margin: '40px auto', padding: 20, fontFamily: 'sans-serif' }}>
            
            <h2>🕸️ Nhập URL, Tiêu đề và Nội dung</h2>
            <button type='submit' onClick={() => refreshPage()}>Cào trang web mới</button>
                {/* URL input */}
                <div style={{ marginBottom: 20 }}>
                    <label><strong>🔗 URL:</strong></label>
                    <input
                        disabled={titleSent}
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="Nhập URL..."
                        style={{ width: '100%', padding: 10 }}
                    />
                </div>

                {/* Title input */}
                <div style={{ marginBottom: 20 }}>
                    <label><strong>📝 Tiêu đề:</strong></label>
                    <textarea
                        disabled={titleSent}
                        rows={2}
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Nhập tiêu đề..."
                        style={{ width: '100%', padding: 10 }}
                    />
                    <button
                        onClick={handleSendTitle}
                        disabled={!url.trim() || !title.trim() || titleSent}
                        style={{
                            marginTop: 10,
                            backgroundColor: (!url.trim() || !title.trim()) ? '#ccc' : '#007bff',
                            color: 'white',
                            border: 'none',
                            padding: '10px 20px',
                            cursor: (!url.trim() || !title.trim()) ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                        }}
                    >
                        🚀 Gửi Tiêu đề
                    </button>
                    {responseUrlTitle && <p style={{ color: 'green', marginTop: 10 }}>{responseUrlTitle}</p>}
                </div>

                {/* Text input - chỉ bật khi đã gửi title */}
                <div style={{ opacity: titleSent ? 1 : 0.5 }}>
                    <label><strong>📄 Nội dung:</strong></label>
                    <input
                        type='tel'
                        value={index}
                        onChange={(e) => setIndex(e.target.value)}
                        placeholder='Nhập index text'
                        disabled={!titleSent}
                    >

                    </input>
                    <textarea
                        rows={5}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Nhập nội dung..."
                        style={{ width: '100%', padding: 10 }}
                        disabled={!titleSent}
                    />
                    <button
                        onClick={handleSendText}
                        disabled={!titleSent}
                        style={{
                            marginTop: 10,
                            backgroundColor: titleSent ? '#28a745' : '#ccc',
                            color: 'white',
                            border: 'none',
                            padding: '10px 20px',
                            cursor: titleSent ? 'pointer' : 'not-allowed',
                            fontWeight: 'bold',
                        }}
                    >
                        📤 Gửi Nội dung
                    </button>
                    {responseText && <p style={{ color: 'green', marginTop: 10 }}>{responseText}</p>}
                </div>
        </div>
    );
};

export default StoreCrawl;

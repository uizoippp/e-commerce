import React, { useState } from 'react';
import axios from 'axios';

const CrawlTool = () => {
    const [url, setUrl] = useState('');
    const [chunks, setChunks] = useState([]);
    const [titles, setTitles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [wordPerChunk, setWordPerChunk] = useState('100');
    const handleCrawl = async () => {
        if (!url) {
            setError('⚠️ Vui lòng nhập URL hoặc từ khoá để cào!');
            return;
        }

        setLoading(true);
        setError('');
        setChunks([]);
        setTitles([]);

        try {
            const response = await axios.post('http://127.0.0.1:8000/crawl/getdata', {
                url: url,
                word_per_chunk: wordPerChunk,
            });

            setChunks(response.data.chunks || []);
            setTitles(response.data.title || []);
        } catch (err) {
            setError('❌ Lỗi khi cào dữ liệu. Kiểm tra backend hoặc URL.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: 800, margin: '40px auto', padding: '20px', fontFamily: 'sans-serif' }}>
            <h2>🕷️ Công cụ cào dữ liệu</h2>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Nhập từ khoá hoặc URL..."
                    style={{ flex: 1, padding: '10px', fontSize: '16px' }}
                />
                <button
                    onClick={handleCrawl}
                    disabled={loading}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: loading ? '#ccc' : '#007BFF',
                        color: '#fff',
                        border: 'none',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold',
                    }}
                >
                    {loading ? '🔄 Đang cào...' : '🚀 Bắt đầu cào'}
                </button>
            </div>

            {error && (
                <div style={{ color: 'red', marginBottom: '20px' }}>
                    {error}
                </div>
            )}

            {titles.length > 0 && (
                <div style={{ marginTop: '30px' }}>
                    <h3>🔖 Tiêu đề trang:</h3>
                    <ul>
                        {titles.map((title, index) => (
                            <li key={index}><strong>{title}</strong></li>
                        ))}
                    </ul>
                </div>
            )}

            {chunks.length > 0 && (
                <div style={{ marginTop: '30px' }}>
                    <h3>📄 Nội dung (chia theo đoạn {wordPerChunk} từ):</h3>
                    {chunks.map((chunk, index) => (
                        <>
                        <h3>{index}</h3>
                        <div
                            key={index}
                            style={{
                                background: '#f9f9f9',
                                padding: '15px',
                                borderRadius: '8px',
                                marginBottom: '15px',
                                border: '1px solid #ddd',
                                whiteSpace: 'pre-wrap',
                            }}
                        >
                            {chunk}
                        </div>
                        </>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CrawlTool;

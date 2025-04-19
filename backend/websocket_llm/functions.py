import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np
import faiss
from typing import Optional, List, Literal, Dict
from .model import convert_text_to_tokenizer
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from collections import defaultdict
from sqlalchemy.orm import Session
from database.database import chunks, webs

# Hàm tính độ tương đồng với FAISS
def find_similar_vectors(list_vectors: list, vector: list, top_k: int = 3) -> Optional[tuple[list[float], list[int]]]:
    # Chuẩn hóa vector đầu vào
    vector = np.array([vector], dtype='float32')  # shape (1, dim)
    faiss.normalize_L2(vector)

    # Chuẩn bị danh sách embedding và chuẩn hóa
    query_embedding = []
    for entry in list_vectors:
        vector_np = np.array(entry.vector, dtype='float32').reshape(1, -1)
        faiss.normalize_L2(vector_np)
        query_embedding.append(vector_np[0])

    query_embedding = np.array(query_embedding).astype('float32')

    # FAISS index
    index = faiss.IndexFlatIP(vector.shape[1])
    index.add(query_embedding)

    # Tìm vector tương tự
    similarities, indices = index.search(vector, top_k)

    # Chuẩn hóa về [0, 1]
    normalized_similarities = (similarities + 1) / 2

    return normalized_similarities.tolist(), indices.tolist()

def relevant_documents(text: str, db: Session, top_k: int = 3, threshold: float = 0.6) -> Optional[List[Dict[Literal['title', 'text'], str]]] | None:
    data = db.query(chunks).all()

    tokenized_text = convert_text_to_tokenizer(text=text)
    distances, indices = find_similar_vectors(data, tokenized_text, top_k)

    # Lọc kết quả
    filtered = [
        (idx, score)
        for idx, score in zip(indices[0], distances[0])
        if score >= threshold
    ]

    top_matches = [data[idx] for idx, score in filtered]  # entrys[i] là object của bảng web

    # Sắp xếp theo id tăng dần, nếu id giống nhau thì theo chunk_index tăng dần
    sorted_matches = sorted(top_matches, key=lambda x: (x.parent_id, x.chunk_index))

    if len(sorted_matches) > 0:    
        documents = []
        temp_parent_id = sorted_matches[0].parent_id
        i = 1
        text_data = ""
        for entry in sorted_matches:    
            if temp_parent_id == entry.parent_id:
                text_data += f"đoạn {i}: {entry.text}."
                i += 1
            else:
                web = db.query(webs).filter(webs.id == temp_parent_id).first()
                documents.append({'title': web.title, 'text': text_data})
                text_data = f"đoạn {1}: {entry.text}."
                i = 2
                temp_parent_id = entry.parent_id
        web_temp = db.query(webs).filter(webs.id == temp_parent_id).first()
        documents.append({'title': web_temp.title, 'text': text_data})
    
        return documents
    return None 

def split_into_word_chunks(text: str, words_per_chunk: int = 50) -> List[str]:
    """
    Chia văn bản thành các chunk có khoảng words_per_chunk từ trong mỗi chunk.
    """
    # Tách văn bản thành các từ
    words = text.split()
    
    # Chia thành các chunk mỗi chunk có tối đa words_per_chunk từ
    chunks = [' '.join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
    
    return chunks

def crawl_and_extract(url: str, word_per_chunk: int) -> dict:
    """
    Cào dữ liệu từ URL và chỉ lấy các thẻ <h1> và <p>.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Gửi yêu cầu và lấy HTML
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Lấy tất cả thẻ <h1> và <p>
    h1_tags = soup.find_all('h1')
    p_tags = soup.find_all('p')

    # Trích xuất nội dung từ thẻ <h1> và <p>
    h1_text = [tag.get_text(strip=True) for tag in h1_tags]
    p_text = [tag.get_text(strip=True) for tag in p_tags]

    # Kết hợp tất cả văn bản thành một chuỗi
    full_text = ' '.join(h1_text + p_text)

    # Chia văn bản thành các chunk mỗi chunk có 200 từ
    text_chunks = split_into_word_chunks(full_text, words_per_chunk=word_per_chunk)
    
    return {'url': url, 'h1': h1_text, 'p': p_text, 'chunks': text_chunks}

def list_chunks(url, word_per_chunk) -> tuple[list, list] :
    """
    chunks, titles
    Trả về kết quả là danh sách chunk với mỗi chunk có số lượng word_per_chunk và title.
    """
    # results = search_duckduckgo(query)
    chunks = list()
    # titles = list()
    # urls = list()
    # for result in results:
        # url = result['href']
    page_data = crawl_and_extract(url, word_per_chunk)
    titles = page_data['h1']
    title_list = list()
    for t in titles:
        title_list.append(t)
    # In các chunks văn bản
    for i, chunk in enumerate(page_data['chunks'], start=1):
        chunks.append(chunk)
    
    return chunks, title_list, url

def search_urls(query: str, max_results: int = 5):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(r['href'])
    return results

def extract_text_from_url(url: str) -> tuple[str, str]:
    try:
        resp = requests.get(url, timeout=5)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')

        h1_tags = soup.find_all('h1')
        title = h1_tags[0].get_text().strip() if h1_tags else "Không có tiêu đề"

        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        return text, title
    
    except Exception as e:
        print(f"⚠️ Lỗi khi đọc {url}: {e}")
        return "", "" 
       
def documents_search(text: str, top_internet: int = 4, top_local: int = 3, threshold: float = 0.70) -> Dict[str, str]:
    search_results = search_urls(text, max_results=top_internet)
    chunks = []
    for url in search_results:
        extracted_text, title = extract_text_from_url(url)
        if extracted_text:

            texts = split_into_word_chunks(text=extracted_text, words_per_chunk=100)
            for text in texts:
                data = {'title': title, 'text': text, 'vector': convert_text_to_tokenizer(text=text)}
                chunks.append(data)
            
    tokenized_text = convert_text_to_tokenizer(text=text)

    # Chuyển các vectors trong CSDL thành numpy array
    vector = np.array([tokenized_text]).astype('float32')

    query_embedding = []
    # Chuyển query embedding thành numpy array
    for entry in chunks:
        vector_np = np.array(entry['vector'], dtype='float32')
        query_embedding.append(vector_np)
    query_embedding = np.array(query_embedding)
    
    faiss.normalize_L2(vector)
    faiss.normalize_L2(query_embedding)

    # FAISS index
    index = faiss.IndexFlatL2(vector.shape[1])
    index.add(query_embedding)

    # Tìm các vector tương tự
    distances, indices = index.search(vector, top_local)  # Tìm top_k vectors tương tự

    # Lọc kết quả
    filtered = [
        (idx, score)
        for idx, score in zip(indices[0], distances[0])
        if score >= threshold
    ]

    top_matches = [chunks[idx] for idx, score in filtered]  # entrys[i] là object của bảng web

    merged = defaultdict(list)
    for item in top_matches:
        merged[item['title']].append(item['text'])
   
    documents = []
    for title, texts in merged.items():
        # Gộp text với số thứ tự
        numbered_text = "\n".join([f"Đoạn {i+1}: {t}" for i, t in enumerate(texts)])
        t = 'Không có tiêu đề.'
        if title: 
            t = title
        documents.append({'title': t, 'text': numbered_text})
    return documents

def build_prompt(documents: list[str] | None, documents_internet: list[str] | None, question: str, system_msg: str = None) -> str:
    doc_text = ""
    doc_internet = ""
    if documents:
        doc_text = "\n".join([f"{i+1}. Tiêu đề: {doc['title']}. Nội dung: {doc['text']}" for i, doc in enumerate(documents)])
    if documents_internet:
        doc_internet = "\n".join([f"{i+1}. Tiêu đề: {doc['title']}. Nội dung: {doc['text']}" for i, doc in enumerate(documents_internet)])

    prompt = ""
    if system_msg:
        prompt += f"### System:\n{system_msg.strip()}\n\n"
    
    prompt += f"""### User:
CHỈ DẪN:
Chỉ sử dụng thông tin từ hai nguồn bên dưới. Nếu có mâu thuẫn, ưu tiên nguồn **TÀI LIỆU TỪ CƠ SỞ DỮ LIỆU**. Không suy đoán. Nếu không đủ thông tin, trả lời: "Tôi không biết!".
---
TÀI LIỆU THỜI GIAN THỰC (Internet):
{doc_internet}
---
TÀI LIỆU TỪ CƠ SỞ DỮ LIỆU:
{doc_text}
---
CÂU HỎI:
Hãy trả lời ngắn gọn, súc tích, không vượt quá 3-4 câu. {question.strip()}

### Assistant:
"""
    return prompt
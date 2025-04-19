from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from pydantic import BaseModel
from websocket_llm.functions import *
from websocket_llm.model import *
from database.database import get_db, webs, chunks
from models.models import *
from sqlalchemy.orm import Session

crawl = APIRouter(
    tags=['crawl']
)

class CrawlRequest(BaseModel):
    url: str
    word_per_chunk: int


@crawl.post('/getdata')
async def crawl_data(request: CrawlRequest, db: Session = Depends(get_db)) -> dict:
    chunks, title, _ = list_chunks(request.url, request.word_per_chunk)
    return {
        "chunks": chunks,
        "title": title,
    }

class webRequest(BaseModel):
    title: str
    source_url: str


@crawl.post('/add/web', response_model=Webs)
async def add_web(request: webRequest, db: Session = Depends(get_db)) -> Webs:
    if request.title != None:
        vector_data = embedder.encode([request.title])
        new_web = webs(source_url=request.source_url, 
                       title=request.title,
                       vector=vector_data.flatten().tolist()
                       )
        db.add(new_web)
        db.commit()
        db.refresh(new_web)
        return new_web
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Nhận được title'
    )

class chunkRequest(BaseModel):
    id: int
    text: str
    index: int

@crawl.post('/add/chunk', response_model=Chunks)
async def add_chunk(request: chunkRequest, db: Session = Depends(get_db)) -> Chunks:
    vector_data = embedder.encode([request.text])
    new_chunk = chunks(parent_id=request.id, chunk_index=request.index, text=request.text, vector=vector_data.flatten().tolist())
    db.add(new_chunk)
    db.commit()
    db.refresh(new_chunk)
    return new_chunk


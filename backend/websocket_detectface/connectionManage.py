from typing import List
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json({'type': 'text',
                                   'message': message})

    async def broadcast(self, message: str):
        data = json.loads(message)
        for connection in self.active_connections:
            await connection.send_json({'type': 'text',
                                    'message': data.get('message'),
                                    'username': data.get('username')})

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import json
import uuid
import os
import logging
import asyncio

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# メッセージタイプ
class MessageType(str, Enum):
    TEXT = "text"
    BINARY = "binary"
    POSITION_REPORT = "position_report"
    SAFETY = "safety"
    DISTRESS = "distress"

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Pydanticスキーマ
class MMTPMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_mrn: str = Field(..., regex=r"^urn:mrn:mcp:")
    recipient_mrn: str = Field(..., regex=r"^urn:mrn:mcp:")
    message_type: MessageType = MessageType.TEXT
    priority: MessagePriority = MessagePriority.NORMAL
    subject: Optional[str] = None
    body: str = Field(..., description="メッセージ本文")
    metadata: Optional[Dict] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    expiry: Optional[datetime] = None

class MessageStatus(BaseModel):
    message_id: str
    status: str  # queued, routing, delivered, failed
    timestamp: datetime
    details: Optional[str] = None

class ConnectionManager:
    """WebSocket接続を管理するクラス"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_mrn: str):
        await websocket.accept()
        self.active_connections[client_mrn] = websocket
        logger.info(f"Client connected: {client_mrn}")
        
    def disconnect(self, client_mrn: str):
        if client_mrn in self.active_connections:
            del self.active_connections[client_mrn]
            logger.info(f"Client disconnected: {client_mrn}")
    
    async def send_message(self, message: dict, client_mrn: str):
        if client_mrn in self.active_connections:
            websocket = self.active_connections[client_mrn]
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Error sending message to {client_mrn}: {e}")
                self.disconnect(client_mrn)
                return False
        return False

# FastAPIアプリケーション
app = FastAPI(
    title="MCP Maritime Messaging Service (Demo)",
    description="Demo version of MCP Messaging Service",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接続マネージャーとメッセージストレージ
manager = ConnectionManager()
message_store: Dict[str, MMTPMessage] = {}
message_status_store: Dict[str, MessageStatus] = {}

@app.on_event("startup")
async def startup_event():
    logger.info("MMS Demo service started")

# API エンドポイント
@app.get("/health")
async def health_check():
    return {"status": "UP", "service": "MMS", "timestamp": datetime.utcnow()}

@app.post("/api/v1/messages", response_model=MessageStatus, status_code=201)
async def send_message(message: MMTPMessage):
    """メッセージを送信"""
    
    # メッセージを保存
    message_store[message.message_id] = message
    
    # 初期ステータス
    status = MessageStatus(
        message_id=message.message_id,
        status="queued",
        timestamp=datetime.utcnow()
    )
    message_status_store[message.message_id] = status
    
    # 配信試行
    try:
        # WebSocket接続があるかチェック
        if await manager.send_message(message.dict(), message.recipient_mrn):
            status.status = "delivered"
            status.details = "Delivered via WebSocket"
        else:
            # シミュレーション: 他の配信チャネル
            status.status = "routing"
            status.details = "Routing via alternative channels"
            
            # 非同期で配信処理をシミュレート
            asyncio.create_task(simulate_delivery(message))
    
    except Exception as e:
        status.status = "failed"
        status.details = str(e)
    
    message_status_store[message.message_id] = status
    logger.info(f"Message queued: {message.message_id} from {message.sender_mrn} to {message.recipient_mrn}")
    
    return status

async def simulate_delivery(message: MMTPMessage):
    """配信シミュレーション"""
    await asyncio.sleep(2)  # 配信遅延をシミュレート
    
    status = message_status_store.get(message.message_id)
    if status and status.status == "routing":
        # 90%の確率で配信成功
        import random
        if random.random() < 0.9:
            status.status = "delivered"
            status.details = "Delivered via VDES channel (simulated)"
        else:
            status.status = "failed"
            status.details = "Delivery failed - recipient unreachable"
        
        status.timestamp = datetime.utcnow()
        logger.info(f"Message delivery simulated: {message.message_id} - {status.status}")

@app.get("/api/v1/messages/{message_id}/status", response_model=MessageStatus)
async def get_message_status(message_id: str):
    """メッセージステータスを取得"""
    if message_id not in message_status_store:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message_status_store[message_id]

@app.get("/api/v1/messages")
async def get_messages(
    sender_mrn: Optional[str] = None,
    recipient_mrn: Optional[str] = None,
    limit: int = 100
):
    """メッセージ一覧を取得"""
    messages = list(message_store.values())
    
    if sender_mrn:
        messages = [m for m in messages if m.sender_mrn == sender_mrn]
    
    if recipient_mrn:
        messages = [m for m in messages if m.recipient_mrn == recipient_mrn]
    
    # 最新順でソート
    messages.sort(key=lambda x: x.timestamp, reverse=True)
    
    return {
        "count": len(messages[:limit]),
        "messages": messages[:limit]
    }

@app.get("/api/v1/connections")
async def get_active_connections():
    """アクティブな接続一覧を取得"""
    return {
        "count": len(manager.active_connections),
        "connections": list(manager.active_connections.keys())
    }

# WebSocketエンドポイント
@app.websocket("/ws/{client_mrn}")
async def websocket_endpoint(websocket: WebSocket, client_mrn: str):
    await manager.connect(websocket, client_mrn)
    
    try:
        while True:
            # クライアントからのメッセージを受信
            data = await websocket.receive_json()
            
            # 受信したデータをメッセージとして処理
            if "message_type" in data:
                try:
                    message = MMTPMessage(**data)
                    message.sender_mrn = client_mrn  # 送信者を接続クライアントに設定
                    
                    # メッセージを他のクライアントに転送
                    await send_message(message)
                    
                    # 送信者に確認応答
                    await websocket.send_json({
                        "type": "ack",
                        "message_id": message.message_id,
                        "status": "received"
                    })
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            else:
                # その他のコマンド処理
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
    except WebSocketDisconnect:
        manager.disconnect(client_mrn)

# ルーティング情報API（デモ用）
@app.get("/api/v1/routing/{mrn}")
async def get_routing_info(mrn: str):
    """ルーティング情報を取得（デモ用）"""
    
    # MRNからエンティティタイプを判定
    parts = mrn.split(":")
    entity_type = parts[3] if len(parts) >= 4 else "unknown"
    
    # シミュレートされたルーティング情報
    routing_info = {
        "recipient_mrn": mrn,
        "entity_type": entity_type,
        "available_channels": [],
        "preferred_channel": "internet",
        "fallback_channels": [],
        "last_seen": None
    }
    
    if entity_type == "vessel":
        routing_info["available_channels"] = ["vdes", "inmarsat", "internet"]
        routing_info["preferred_channel"] = "vdes"
        routing_info["fallback_channels"] = ["inmarsat", "internet"]
    elif entity_type == "shore":
        routing_info["available_channels"] = ["internet", "vdes"]
        routing_info["preferred_channel"] = "internet"
        routing_info["fallback_channels"] = ["vdes"]
    else:
        routing_info["available_channels"] = ["internet"]
        routing_info["preferred_channel"] = "internet"
        routing_info["fallback_channels"] = []
    
    # WebSocket接続がある場合は追加
    if mrn in manager.active_connections:
        routing_info["available_channels"].append("websocket")
        routing_info["preferred_channel"] = "websocket"
        routing_info["last_seen"] = datetime.utcnow().isoformat()
    
    return routing_info

# 通信チャネル統計API（デモ用）
@app.get("/api/v1/channels/stats")
async def get_channel_stats():
    """通信チャネル統計を取得（デモ用）"""
    return {
        "channels": [
            {
                "name": "websocket",
                "type": "IP",
                "active_connections": len(manager.active_connections),
                "messages_sent": len(message_store),
                "availability": "online"
            },
            {
                "name": "vdes",
                "type": "RF",
                "active_connections": 0,
                "messages_sent": 0,
                "availability": "simulated"
            },
            {
                "name": "inmarsat",
                "type": "Satellite",
                "active_connections": 0,
                "messages_sent": 0,
                "availability": "simulated"
            },
            {
                "name": "internet",
                "type": "IP",
                "active_connections": 0,
                "messages_sent": 0,
                "availability": "simulated"
            }
        ],
        "total_messages": len(message_store),
        "delivered_messages": len([s for s in message_status_store.values() if s.status == "delivered"]),
        "failed_messages": len([s for s in message_status_store.values() if s.status == "failed"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
#!/usr/bin/env python3
"""
MCP船舶メッセージング デモスクリプト

このスクリプトは、船舶と拠点間のメッセージ送受信をシミュレートします。
WebSocketとREST APIの両方の使用例を示します。
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any

class MCPMessagingDemo:
    def __init__(self):
        self.mms_base_url = "http://localhost:8083"
        self.mms_ws_url = "ws://localhost:8083/ws"
        
        # MRN（Maritime Resource Name）の定義
        self.vessel_mrn = "urn:mrn:mcp:vessel:imo:1234567"
        self.vts_mrn = "urn:mrn:mcp:shore:authority:vts:tokyo-bay"
        self.port_mrn = "urn:mrn:mcp:shore:port:yokohama"
        
        self.vessel_ws = None
        self.vts_ws = None
        
    async def connect_vessel(self):
        """船舶のWebSocket接続を確立"""
        try:
            self.vessel_ws = await websockets.connect(f"{self.mms_ws_url}/{self.vessel_mrn}")
            print(f"🚢 船舶 {self.vessel_mrn} がMMSに接続しました")
            
            # 接続状態の通知
            await self.vessel_ws.send(json.dumps({
                "type": "connection_status",
                "status": "connected",
                "position": {"latitude": 35.6762, "longitude": 139.6503},
                "timestamp": datetime.now().isoformat()
            }))
            
            return True
        except Exception as e:
            print(f"❌ 船舶接続エラー: {e}")
            return False
    
    async def connect_vts(self):
        """VTS（拠点）のWebSocket接続を確立"""
        try:
            self.vts_ws = await websockets.connect(f"{self.mms_ws_url}/{self.vts_mrn}")
            print(f"🏛️ VTS {self.vts_mrn} がMMSに接続しました")
            return True
        except Exception as e:
            print(f"❌ VTS接続エラー: {e}")
            return False
    
    async def send_websocket_message(self, ws, recipient_mrn: str, message_type: str, 
                                   subject: str, body: str, metadata: Dict = None):
        """WebSocket経由でメッセージを送信"""
        message = {
            "recipient_mrn": recipient_mrn,
            "message_type": message_type,
            "subject": subject,
            "body": body,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            message["metadata"] = metadata
        
        try:
            await ws.send(json.dumps(message))
            print(f"📤 WebSocketメッセージ送信: {subject}")
            return True
        except Exception as e:
            print(f"❌ WebSocketメッセージ送信エラー: {e}")
            return False
    
    def send_rest_message(self, sender_mrn: str, recipient_mrn: str, 
                         message_type: str, subject: str, body: str, metadata: Dict = None):
        """REST API経由でメッセージを送信"""
        url = f"{self.mms_base_url}/api/v1/messages"
        
        payload = {
            "sender_mrn": sender_mrn,
            "recipient_mrn": recipient_mrn,
            "message_type": message_type,
            "subject": subject,
            "body": body
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                print(f"📤 RESTメッセージ送信成功: {subject}")
                return response.json()
            else:
                print(f"❌ RESTメッセージ送信失敗: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ RESTメッセージ送信エラー: {e}")
            return None
    
    async def listen_vessel_messages(self):
        """船舶側でメッセージを受信"""
        try:
            async for message in self.vessel_ws:
                data = json.loads(message)
                print(f"🚢📥 船舶受信: {data.get('subject', 'No Subject')} - {data.get('body', '')}")
                
                # 自動応答の例
                if data.get('message_type') == 'navigation_instruction':
                    await self.send_websocket_message(
                        self.vessel_ws, 
                        data.get('sender_mrn', self.vts_mrn),
                        'acknowledgment',
                        '航行指示確認',
                        '航行指示を受信し、指示に従います。'
                    )
        except websockets.exceptions.ConnectionClosed:
            print("🚢 船舶のWebSocket接続が切断されました")
        except Exception as e:
            print(f"❌ 船舶メッセージ受信エラー: {e}")
    
    async def listen_vts_messages(self):
        """VTS側でメッセージを受信"""
        try:
            async for message in self.vts_ws:
                data = json.loads(message)
                print(f"🏛️📥 VTS受信: {data.get('subject', 'No Subject')} - {data.get('body', '')}")
                
                # 自動応答の例
                if data.get('message_type') == 'position_report':
                    await self.send_websocket_message(
                        self.vts_ws,
                        data.get('sender_mrn', self.vessel_mrn),
                        'acknowledgment',
                        '位置報告確認',
                        '位置報告を受信しました。航行を継続してください。'
                    )
        except websockets.exceptions.ConnectionClosed:
            print("🏛️ VTSのWebSocket接続が切断されました")
        except Exception as e:
            print(f"❌ VTSメッセージ受信エラー: {e}")
    
    async def demo_vessel_position_reports(self):
        """船舶位置報告のデモ"""
        positions = [
            {"lat": 35.6762, "lng": 139.6503, "course": 90, "speed": 12},
            {"lat": 35.6765, "lng": 139.6520, "course": 85, "speed": 12},
            {"lat": 35.6768, "lng": 139.6540, "course": 80, "speed": 11},
            {"lat": 35.6770, "lng": 139.6560, "course": 75, "speed": 10}
        ]
        
        for i, pos in enumerate(positions):
            await asyncio.sleep(5)  # 5秒間隔
            
            body = f"緯度: {pos['lat']}, 経度: {pos['lng']}, 針路: {pos['course']}°, 速力: {pos['speed']}kts"
            metadata = {
                "position": pos,
                "vessel_status": "under_way_using_engine",
                "ais_class": "A"
            }
            
            await self.send_websocket_message(
                self.vessel_ws,
                self.vts_mrn,
                'position_report',
                f'位置報告 #{i+1}',
                body,
                metadata
            )
    
    async def demo_vessel_port_entry(self):
        """船舶入港要請のデモ"""
        await asyncio.sleep(10)
        
        # 入港要請
        await self.send_websocket_message(
            self.vessel_ws,
            self.port_mrn,
            'port_entry_request',
            '横浜港入港要請',
            'ETA: 14:30, 積荷: コンテナ1500TEU',
            {
                "eta": "2024-01-15T14:30:00Z",
                "vessel_info": {
                    "imo": "1234567",
                    "name": "MV DEMO SHIP",
                    "type": "container_ship",
                    "length": 300,
                    "beam": 45,
                    "draft": 12.5
                },
                "cargo_info": {
                    "type": "containers",
                    "quantity": 1500,
                    "dangerous_goods": False
                }
            }
        )
    
    async def demo_emergency_scenario(self):
        """緊急事態のデモ"""
        await asyncio.sleep(20)
        
        # 緊急警報
        await self.send_websocket_message(
            self.vessel_ws,
            self.vts_mrn,
            'distress_alert',
            '緊急警報 - エンジン故障',
            'エンジン故障により航行不能。緊急支援要請。位置: 35.6770, 139.6560',
            {
                "urgency": "emergency",
                "position": {"lat": 35.6770, "lng": 139.6560},
                "assistance_required": ["towing", "technical_support"],
                "emergency_contact": "+81-3-1234-5678"
            }
        )
    
    async def demo_vts_instructions(self):
        """VTS指示のデモ"""
        await asyncio.sleep(15)
        
        # 航行指示
        await self.send_websocket_message(
            self.vts_ws,
            self.vessel_mrn,
            'navigation_instruction',
            '航行指示',
            '分離航路の右側通行を維持してください。現在の交通量により、速力を12ノット以下に制限します。',
            {
                "urgency": "normal",
                "compliance_required": True,
                "valid_until": "2024-01-15T16:00:00Z"
            }
        )
        
        await asyncio.sleep(10)
        
        # 気象警報
        await self.send_websocket_message(
            self.vts_ws,
            self.vessel_mrn,
            'weather_alert',
            '気象警報',
            '強風警報: 東京湾内で北風15-20m/s、波高2-3m。航行注意。',
            {
                "alert_type": "wind_warning",
                "wind_speed": "15-20",
                "wave_height": "2-3",
                "valid_until": "2024-01-15T18:00:00Z"
            }
        )
    
    def demo_rest_api_usage(self):
        """REST APIの使用例"""
        print("\n📡 REST API使用例:")
        
        # メッセージ送信
        self.send_rest_message(
            self.vessel_mrn,
            self.vts_mrn,
            'status_update',
            '船舶状態更新',
            '現在の状態: 航行中、目的地: 横浜港、予定到着時刻: 14:30'
        )
        
        # メッセージ履歴の取得
        try:
            response = requests.get(f"{self.mms_base_url}/api/v1/messages")
            if response.status_code == 200:
                messages = response.json()
                print(f"📋 メッセージ履歴: {len(messages.get('messages', []))}件")
            else:
                print(f"❌ メッセージ履歴取得エラー: {response.status_code}")
        except Exception as e:
            print(f"❌ REST API呼び出しエラー: {e}")
        
        # アクティブ接続の確認
        try:
            response = requests.get(f"{self.mms_base_url}/api/v1/connections")
            if response.status_code == 200:
                connections = response.json()
                print(f"🔗 アクティブ接続: {len(connections.get('connections', []))}件")
            else:
                print(f"❌ 接続状態取得エラー: {response.status_code}")
        except Exception as e:
            print(f"❌ REST API呼び出しエラー: {e}")
    
    async def run_demo(self):
        """メインデモの実行"""
        print("🚀 MCP船舶メッセージング デモを開始します...")
        print("📌 MMSサービスが localhost:8083 で起動していることを確認してください\n")
        
        # 接続の確立
        vessel_connected = await self.connect_vessel()
        vts_connected = await self.connect_vts()
        
        if not vessel_connected or not vts_connected:
            print("❌ 接続に失敗しました。デモを終了します。")
            return
        
        # REST APIのデモ
        self.demo_rest_api_usage()
        
        # 並行してメッセージのやり取りを実行
        tasks = [
            asyncio.create_task(self.listen_vessel_messages()),
            asyncio.create_task(self.listen_vts_messages()),
            asyncio.create_task(self.demo_vessel_position_reports()),
            asyncio.create_task(self.demo_vessel_port_entry()),
            asyncio.create_task(self.demo_vts_instructions()),
            asyncio.create_task(self.demo_emergency_scenario())
        ]
        
        print("\n🎭 デモシナリオを実行中...")
        print("⏰ 30秒間のデモを実行します。Ctrl+Cで終了できます。\n")
        
        try:
            # 30秒間実行
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=30.0)
        except asyncio.TimeoutError:
            print("\n⏰ デモ時間が終了しました")
        except KeyboardInterrupt:
            print("\n🛑 ユーザーによりデモが中断されました")
        
        # 接続のクリーンアップ
        if self.vessel_ws:
            await self.vessel_ws.close()
        if self.vts_ws:
            await self.vts_ws.close()
        
        print("✅ デモが完了しました")

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚢 MCP 船舶メッセージング デモ")
    print("=" * 60)
    
    demo = MCPMessagingDemo()
    
    try:
        asyncio.run(demo.run_demo())
    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")

if __name__ == "__main__":
    main()
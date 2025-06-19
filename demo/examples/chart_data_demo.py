#!/usr/bin/env python3
"""
MCP海図データ送受信デモ

このスクリプトは、船舶と拠点間での海図データ（航路計画、測深データ、航行警報）の
送受信をシミュレートします。
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import websockets
import requests
from dataclasses import dataclass, asdict

# データクラス定義
@dataclass
class Waypoint:
    """航路点"""
    sequence_number: int
    latitude: float
    longitude: float
    planned_speed: float  # knots
    planned_eta: str
    turn_radius: float = None
    notes: str = None

@dataclass
class RoutePlan:
    """航路計画"""
    route_id: str
    vessel_mrn: str
    route_name: str
    departure_port: str
    arrival_port: str
    planned_etd: str
    planned_eta: str
    waypoints: List[Waypoint]
    route_status: str = "planned"
    optimization_criteria: str = "shortest"

@dataclass
class BathymetricPoint:
    """測深点データ"""
    latitude: float
    longitude: float
    depth: float  # meters
    timestamp: str
    quality_indicator: int  # 1-5, 1が最高品質
    measurement_method: str = "single-beam"

@dataclass
class NavigationalWarning:
    """航行警報"""
    warning_id: str
    warning_type: str
    severity: str
    area_wkt: str
    valid_from: str
    valid_to: str
    description: str
    issued_by: str

class ChartDataDemo:
    def __init__(self):
        self.mms_base_url = "http://localhost:8083"
        self.mms_ws_url = "ws://localhost:8083/ws"
        self.vessel_mrn = "urn:mrn:mcp:vessel:imo:1234567"
        self.vts_mrn = "urn:mrn:mcp:shore:authority:vts:tokyo-bay"
        self.vessel_ws = None
        self.vts_ws = None
        
    def create_sample_route_plan(self) -> RoutePlan:
        """サンプル航路計画を作成"""
        now = datetime.now()
        etd = now + timedelta(hours=2)
        eta = etd + timedelta(hours=8)
        
        waypoints = []
        
        # 東京湾から大阪湾への航路
        route_points = [
            (35.45, 139.65, 12.0),  # 東京湾出口
            (35.20, 139.70, 15.0),  # 相模湾
            (35.00, 139.50, 18.0),  # 伊豆沖
            (34.70, 138.90, 18.0),  # 遠州灘
            (34.50, 137.00, 16.0),  # 熊野灘
            (34.40, 135.20, 12.0),  # 紀伊水道
            (34.60, 135.40, 10.0),  # 大阪湾入口
        ]
        
        for i, (lat, lon, speed) in enumerate(route_points):
            if i == 0:
                wp_eta = etd
            else:
                # 前の点からの距離と速度から到着時刻を計算
                prev_point = route_points[i-1]
                distance = self._calculate_distance(
                    prev_point[0], prev_point[1], lat, lon
                )
                travel_time = distance / prev_point[2]  # hours
                wp_eta = waypoints[i-1].planned_eta
                wp_eta = datetime.fromisoformat(wp_eta) + timedelta(hours=travel_time)
            
            waypoints.append(Waypoint(
                sequence_number=i+1,
                latitude=lat,
                longitude=lon,
                planned_speed=speed,
                planned_eta=wp_eta.isoformat() if isinstance(wp_eta, datetime) else wp_eta,
                turn_radius=0.5 if i > 0 and i < len(route_points)-1 else None,
                notes=f"WP{i+1} - {'出発' if i==0 else '到着' if i==len(route_points)-1 else '通過点'}"
            ))
        
        return RoutePlan(
            route_id=f"ROUTE-{int(time.time())}",
            vessel_mrn=self.vessel_mrn,
            route_name="東京-大阪定期航路",
            departure_port="JPTYO",  # 東京港
            arrival_port="JPOSA",    # 大阪港
            planned_etd=etd.isoformat(),
            planned_eta=eta.isoformat(),
            waypoints=waypoints
        )
    
    def _calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """2点間の距離を計算（海里）"""
        # 簡易計算（実際はより正確な測地線距離計算が必要）
        import math
        R = 3440.065  # 地球半径（海里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def generate_bathymetric_data(self, center_lat: float, center_lon: float, 
                                 num_points: int = 50) -> List[BathymetricPoint]:
        """測深データを生成"""
        points = []
        base_depth = 50.0  # 基準水深
        
        for i in range(num_points):
            # ランダムな位置（中心から±0.1度の範囲）
            lat = center_lat + random.uniform(-0.1, 0.1)
            lon = center_lon + random.uniform(-0.1, 0.1)
            
            # 深度の変化（基準±20m）
            depth = base_depth + random.uniform(-20, 20)
            
            # ノイズを含む品質指標
            quality = random.choices([1, 2, 3, 4, 5], 
                                   weights=[50, 30, 15, 4, 1])[0]
            
            points.append(BathymetricPoint(
                latitude=lat,
                longitude=lon,
                depth=depth,
                timestamp=datetime.now().isoformat(),
                quality_indicator=quality,
                measurement_method="multi-beam" if quality <= 2 else "single-beam"
            ))
        
        return points
    
    def create_navigational_warning(self) -> NavigationalWarning:
        """航行警報を作成"""
        warning_types = [
            ("obstruction", "沈没船による航行障害"),
            ("restricted_area", "海上工事による通行制限"),
            ("weather", "強風・高波警報"),
            ("military_exercise", "射撃訓練区域")
        ]
        
        warning_type, description = random.choice(warning_types)
        
        # 警告エリア（簡易的な矩形）
        base_lat = 35.0 + random.uniform(-0.5, 0.5)
        base_lon = 139.0 + random.uniform(-0.5, 0.5)
        area_wkt = f"POLYGON(({base_lon} {base_lat}, " \
                  f"{base_lon+0.1} {base_lat}, " \
                  f"{base_lon+0.1} {base_lat+0.1}, " \
                  f"{base_lon} {base_lat+0.1}, " \
                  f"{base_lon} {base_lat}))"
        
        now = datetime.now()
        valid_from = now
        valid_to = now + timedelta(hours=random.randint(6, 48))
        
        return NavigationalWarning(
            warning_id=f"WARN-{int(time.time())}",
            warning_type=warning_type,
            severity=random.choice(["critical", "major", "minor"]),
            area_wkt=area_wkt,
            valid_from=valid_from.isoformat(),
            valid_to=valid_to.isoformat(),
            description=description,
            issued_by=self.vts_mrn
        )
    
    async def connect_vessel(self):
        """船舶のWebSocket接続"""
        try:
            self.vessel_ws = await websockets.connect(
                f"{self.mms_ws_url}/{self.vessel_mrn}"
            )
            print(f"🚢 船舶 {self.vessel_mrn} が接続しました")
            return True
        except Exception as e:
            print(f"❌ 船舶接続エラー: {e}")
            return False
    
    async def connect_vts(self):
        """VTSのWebSocket接続"""
        try:
            self.vts_ws = await websockets.connect(
                f"{self.mms_ws_url}/{self.vts_mrn}"
            )
            print(f"🏛️ VTS {self.vts_mrn} が接続しました")
            return True
        except Exception as e:
            print(f"❌ VTS接続エラー: {e}")
            return False
    
    async def send_route_plan(self):
        """航路計画を送信"""
        route_plan = self.create_sample_route_plan()
        
        # RTZ形式のXMLを簡易的に作成
        rtz_content = self._generate_rtz_xml(route_plan)
        
        message = {
            "recipient_mrn": self.vts_mrn,
            "message_type": "route_exchange",
            "subject": f"航路計画: {route_plan.route_name}",
            "body": f"航路計画を送信します。出発: {route_plan.departure_port}, " \
                   f"到着: {route_plan.arrival_port}",
            "attachments": [{
                "filename": f"{route_plan.route_id}.rtz",
                "content_type": "application/x-rtz",
                "data": rtz_content
            }],
            "metadata": {
                "route_id": route_plan.route_id,
                "waypoint_count": len(route_plan.waypoints),
                "total_distance": self._calculate_total_distance(route_plan.waypoints)
            }
        }
        
        await self.vessel_ws.send(json.dumps(message))
        print(f"📤 航路計画を送信: {route_plan.route_name}")
        print(f"   航路点数: {len(route_plan.waypoints)}")
        print(f"   出発: {route_plan.departure_port} → 到着: {route_plan.arrival_port}")
    
    def _generate_rtz_xml(self, route_plan: RoutePlan) -> str:
        """簡易的なRTZ XMLを生成"""
        waypoints_xml = ""
        for wp in route_plan.waypoints:
            waypoints_xml += f"""
        <waypoint id="{wp.sequence_number}">
            <position lat="{wp.latitude}" lon="{wp.longitude}"/>
            <leg speed="{wp.planned_speed}"/>
            <extensions>
                <extension name="eta" value="{wp.planned_eta}"/>
                <extension name="notes" value="{wp.notes or ''}"/>
            </extensions>
        </waypoint>"""
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<route version="1.1" xmlns="http://www.cirm.org/RTZ/1/1">
    <routeInfo routeName="{route_plan.route_name}" routeStatus="{route_plan.route_status}">
        <extensions>
            <extension name="departure_port" value="{route_plan.departure_port}"/>
            <extension name="arrival_port" value="{route_plan.arrival_port}"/>
            <extension name="vessel_mrn" value="{route_plan.vessel_mrn}"/>
        </extensions>
    </routeInfo>
    <waypoints>{waypoints_xml}
    </waypoints>
</route>"""
    
    def _calculate_total_distance(self, waypoints: List[Waypoint]) -> float:
        """航路の総距離を計算"""
        total = 0.0
        for i in range(1, len(waypoints)):
            total += self._calculate_distance(
                waypoints[i-1].latitude, waypoints[i-1].longitude,
                waypoints[i].latitude, waypoints[i].longitude
            )
        return round(total, 1)
    
    async def stream_bathymetric_data(self):
        """測深データをストリーミング送信"""
        print("📊 測深データのストリーミングを開始...")
        
        # 3つのエリアで測深データを生成
        areas = [
            (35.45, 139.65, "東京湾"),
            (35.00, 139.50, "伊豆沖"),
            (34.50, 137.00, "熊野灘")
        ]
        
        for lat, lon, area_name in areas:
            points = self.generate_bathymetric_data(lat, lon, 30)
            
            message = {
                "recipient_mrn": self.vts_mrn,
                "message_type": "bathymetric_stream",
                "subject": f"測深データ - {area_name}",
                "body": f"{area_name}の測深データ（{len(points)}点）",
                "data": [asdict(p) for p in points],
                "metadata": {
                    "area_name": area_name,
                    "center_position": {"lat": lat, "lon": lon},
                    "point_count": len(points),
                    "average_depth": sum(p.depth for p in points) / len(points)
                }
            }
            
            await self.vessel_ws.send(json.dumps(message))
            print(f"   📍 {area_name}: {len(points)}点送信 " \
                  f"(平均水深: {message['metadata']['average_depth']:.1f}m)")
            
            await asyncio.sleep(2)  # 送信間隔
    
    async def send_navigational_warning(self):
        """航行警報を送信"""
        warning = self.create_navigational_warning()
        
        message = {
            "recipient_mrn": self.vessel_mrn,
            "message_type": "navigational_warning",
            "subject": f"航行警報 - {warning.warning_type}",
            "body": warning.description,
            "data": asdict(warning),
            "metadata": {
                "urgency": warning.severity,
                "affected_area": warning.area_wkt,
                "duration_hours": self._calculate_duration_hours(
                    warning.valid_from, warning.valid_to
                )
            }
        }
        
        await self.vts_ws.send(json.dumps(message))
        print(f"⚠️ 航行警報を送信: {warning.description}")
        print(f"   重要度: {warning.severity}")
        print(f"   有効期間: {message['metadata']['duration_hours']}時間")
    
    def _calculate_duration_hours(self, from_str: str, to_str: str) -> float:
        """期間を時間単位で計算"""
        from_dt = datetime.fromisoformat(from_str)
        to_dt = datetime.fromisoformat(to_str)
        return (to_dt - from_dt).total_seconds() / 3600
    
    async def listen_vessel_messages(self):
        """船舶側でメッセージを受信"""
        try:
            async for message in self.vessel_ws:
                data = json.loads(message)
                msg_type = data.get('message_type', '')
                
                if msg_type == 'navigational_warning':
                    warning_data = data.get('data', {})
                    print(f"🚢📥 航行警報受信: {warning_data.get('description', '')}")
                    print(f"     警報タイプ: {warning_data.get('warning_type', '')}")
                    print(f"     重要度: {warning_data.get('severity', '')}")
                else:
                    print(f"🚢📥 メッセージ受信: {data.get('subject', '')}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🚢 船舶の接続が切断されました")
    
    async def listen_vts_messages(self):
        """VTS側でメッセージを受信"""
        try:
            async for message in self.vts_ws:
                data = json.loads(message)
                msg_type = data.get('message_type', '')
                
                if msg_type == 'route_exchange':
                    attachments = data.get('attachments', [])
                    if attachments:
                        print(f"🏛️📥 航路計画受信: {data.get('subject', '')}")
                        metadata = data.get('metadata', {})
                        print(f"     航路点数: {metadata.get('waypoint_count', 0)}")
                        print(f"     総距離: {metadata.get('total_distance', 0):.1f}海里")
                        
                elif msg_type == 'bathymetric_stream':
                    metadata = data.get('metadata', {})
                    print(f"🏛️📥 測深データ受信: {data.get('subject', '')}")
                    print(f"     データ点数: {metadata.get('point_count', 0)}")
                    print(f"     平均水深: {metadata.get('average_depth', 0):.1f}m")
                    
                else:
                    print(f"🏛️📥 メッセージ受信: {data.get('subject', '')}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🏛️ VTSの接続が切断されました")
    
    def send_chart_update_rest(self):
        """REST APIで海図更新通知を送信"""
        url = f"{self.mms_base_url}/api/v1/messages"
        
        update_info = {
            "update_id": f"UPDATE-{int(time.time())}",
            "chart_area": "JP-TOKYO-BAY",
            "version": "2024.1.15",
            "changes": [
                "新規沈没船の位置追加",
                "航路標識の位置修正",
                "水深データの更新"
            ],
            "effective_date": datetime.now().isoformat()
        }
        
        payload = {
            "sender_mrn": self.vts_mrn,
            "recipient_mrn": self.vessel_mrn,
            "message_type": "chart_update",
            "subject": "海図更新通知 - 東京湾",
            "body": "東京湾エリアの海図が更新されました。最新版をダウンロードしてください。",
            "metadata": update_info
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                print("📡 REST API経由で海図更新通知を送信")
                print(f"   エリア: {update_info['chart_area']}")
                print(f"   バージョン: {update_info['version']}")
            else:
                print(f"❌ 送信失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ REST APIエラー: {e}")
    
    async def run_demo(self):
        """デモを実行"""
        print("=" * 60)
        print("🗺️ MCP 海図データ送受信デモ")
        print("=" * 60)
        print()
        
        # 接続確立
        vessel_connected = await self.connect_vessel()
        vts_connected = await self.connect_vts()
        
        if not vessel_connected or not vts_connected:
            print("❌ 接続に失敗しました")
            return
        
        # メッセージリスナーを開始
        listen_tasks = [
            asyncio.create_task(self.listen_vessel_messages()),
            asyncio.create_task(self.listen_vts_messages())
        ]
        
        print("\n🎯 デモシナリオ実行中...\n")
        
        try:
            # 1. 航路計画の送信
            await self.send_route_plan()
            await asyncio.sleep(3)
            
            # 2. 測深データのストリーミング
            await self.stream_bathymetric_data()
            await asyncio.sleep(2)
            
            # 3. 航行警報の送信
            await self.send_navigational_warning()
            await asyncio.sleep(2)
            
            # 4. REST APIで海図更新通知
            self.send_chart_update_rest()
            await asyncio.sleep(2)
            
            print("\n✅ デモシナリオ完了")
            print("⏰ 5秒後に終了します...")
            
            # 追加メッセージを待つ
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ デモ実行エラー: {e}")
            
        finally:
            # クリーンアップ
            for task in listen_tasks:
                task.cancel()
            
            if self.vessel_ws:
                await self.vessel_ws.close()
            if self.vts_ws:
                await self.vts_ws.close()
            
            print("\n👋 デモを終了しました")

def main():
    """メイン関数"""
    demo = ChartDataDemo()
    
    try:
        asyncio.run(demo.run_demo())
    except KeyboardInterrupt:
        print("\n🛑 ユーザーによりデモが中断されました")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()
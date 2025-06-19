#!/bin/bash

echo "🎯 MCPデモシナリオを実行中..."

# 色の定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# APIベースURL
MIR_API="http://localhost:8081/api/v1"
MSR_API="http://localhost:8082/api/v1"
MMS_API="http://localhost:8083/api/v1"

echo ""
echo -e "${BLUE}📝 シナリオ: 海事サービスの登録から利用まで${NC}"
echo ""

# 1. 組織の確認
echo -e "${YELLOW}1. 組織情報の確認${NC}"
echo "   デモ組織一覧を取得..."
curl -s "$MIR_API/organizations" | jq '.organizations[] | {mrn: .mrn, name: .name}'
echo ""

# 2. 新しい組織の作成
echo -e "${YELLOW}2. 新しい組織の作成${NC}"
echo "   テスト組織を作成..."
curl -s -X POST "$MIR_API/organizations" \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "urn:mrn:mcp:org:demo:test-company",
    "name": "Demo Test Company",
    "country": "JP",
    "description": "デモシナリオ用のテスト組織",
    "contact_email": "test@demo-company.com"
  }' | jq '{mrn: .mrn, name: .name, status: "created"}'
echo ""

# 3. サービス仕様の確認
echo -e "${YELLOW}3. 利用可能なサービス仕様の確認${NC}"
echo "   登録済みサービス仕様..."
curl -s "$MSR_API/serviceSpecifications" | jq '.specifications[] | {mrn: .mrn, name: .name, status: .status}'
echo ""

# 4. 新しいサービス仕様の作成
echo -e "${YELLOW}4. 新しいサービス仕様の作成${NC}"
echo "   船舶管理サービス仕様を作成..."
curl -s -X POST "$MSR_API/serviceSpecifications" \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "urn:mrn:mcp:service:demo:vessel-management",
    "name": "Vessel Management Service",
    "version": "1.0.0",
    "description": "船舶の運航管理とモニタリングサービス",
    "keywords": ["vessel", "management", "monitoring"],
    "status": "released",
    "organization_mrn": "urn:mrn:mcp:org:demo:test-company"
  }' | jq '{mrn: .mrn, name: .name, status: "created"}'
echo ""

# 5. サービスインスタンスの作成
echo -e "${YELLOW}5. サービスインスタンスの作成${NC}"
echo "   東京湾エリア用サービスインスタンス..."
curl -s -X POST "$MSR_API/serviceInstances" \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "urn:mrn:mcp:instance:demo:vessel-management:tokyo-bay",
    "name": "Tokyo Bay Vessel Management",
    "version": "1.0.0",
    "service_specification_mrn": "urn:mrn:mcp:service:demo:vessel-management",
    "organization_mrn": "urn:mrn:mcp:org:demo:test-company",
    "endpoint_uri": "http://vessel-mgmt-demo.mcp.local/api",
    "endpoint_type": "REST",
    "status": "active",
    "coverage_area_wkt": "POLYGON((139.5 35.4, 140.0 35.4, 140.0 35.8, 139.5 35.8, 139.5 35.4))",
    "metadata": {
      "region": "Tokyo Bay",
      "language": "ja",
      "contact": "tokyo-ops@demo-company.com"
    }
  }' | jq '{mrn: .mrn, name: .name, status: "created"}'
echo ""

# 6. サービス検索
echo -e "${YELLOW}6. サービス検索のテスト${NC}"
echo "   キーワード検索 (weather)..."
curl -s "$MSR_API/search/services?keywords=weather&limit=3" | jq '{count: .count, services: [.services[] | {mrn: .mrn, name: .name}]}'
echo ""

echo "   地理的検索 (東京湾周辺)..."
curl -s "$MSR_API/search/services?location=139.7,35.6&radius=50&limit=3" | jq '{count: .count, services: [.services[] | {mrn: .mrn, name: .name}]}'
echo ""

# 7. メッセージ送信
echo -e "${YELLOW}7. メッセージ送信のテスト${NC}"
echo "   船舶から海上保安庁へのメッセージ..."
MESSAGE_RESPONSE=$(curl -s -X POST "$MMS_API/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_mrn": "urn:mrn:mcp:vessel:imo:9876543",
    "recipient_mrn": "urn:mrn:mcp:shore:authority:jcg",
    "message_type": "position_report",
    "priority": "normal",
    "subject": "Position Report - Demo Vessel",
    "body": "Position: 35.6762°N, 139.6503°E, Course: 045°, Speed: 12 knots"
  }')

echo "$MESSAGE_RESPONSE" | jq '{message_id: .message_id, status: .status}'
MESSAGE_ID=$(echo "$MESSAGE_RESPONSE" | jq -r '.message_id')
echo ""

# 8. メッセージ状況確認
echo -e "${YELLOW}8. メッセージ配信状況の確認${NC}"
echo "   メッセージステータス..."
sleep 3  # 配信処理を待つ
curl -s "$MMS_API/messages/$MESSAGE_ID/status" | jq '{message_id: .message_id, status: .status, details: .details}'
echo ""

# 9. 統計情報
echo -e "${YELLOW}9. システム統計情報${NC}"
echo "   通信チャネル統計..."
curl -s "$MMS_API/channels/stats" | jq '{total_messages: .total_messages, delivered: .delivered_messages, channels: [.channels[] | {name: .name, type: .type, availability: .availability}]}'
echo ""

echo -e "${GREEN}✅ デモシナリオが完了しました！${NC}"
echo ""
echo "🔍 詳細確認のコマンド例:"
echo "  組織一覧:         curl $MIR_API/organizations | jq"
echo "  サービス一覧:     curl $MSR_API/serviceInstances | jq"
echo "  メッセージ一覧:   curl $MMS_API/messages | jq"
echo "  アクティブ接続:   curl $MMS_API/connections | jq"
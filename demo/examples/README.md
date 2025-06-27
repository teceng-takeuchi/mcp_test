# MCP メッセージング デモ例

このディレクトリには、MCP（Maritime Connectivity Platform）のメッセージング機能を体験するためのデモとサンプルコードが含まれています。

## 含まれるファイル

### 1. messaging_demo.html
**ブラウザベースのインタラクティブデモ**

- WebSocket接続を使用したリアルタイムメッセージング
- 船舶と拠点（VTS）の両方の視点でのUI
- クイックアクションボタンで典型的なメッセージを送信
- メッセージ履歴の表示

**使用方法:**
```bash
# MCPデモ環境が起動していることを確認
cd /path/to/mcp_test/demo
./scripts/health-check.sh

# ブラウザでHTMLファイルを開く
open examples/messaging_demo.html
```

### 2. messaging_demo.py
**Pythonベースの自動デモスクリプト**

- WebSocketとREST APIの両方の使用例
- 自動化されたメッセージ送受信シナリオ
- 位置報告、入港要請、緊急警報などのシミュレーション
- エラーハンドリングと接続管理

**使用方法:**
```bash
# 必要な依存関係をインストール
pip install websockets requests

# デモスクリプトを実行
python examples/messaging_demo.py
```

## デモシナリオ

### 1. 基本的なメッセージフロー
1. 船舶とVTS（拠点）がMMSに接続
2. 船舶が定期的な位置報告を送信
3. VTSが航行指示で応答
4. 船舶が確認応答を送信

### 2. 入港手続きフロー
1. 船舶が入港要請を送信
2. 港湾管制が入港許可を送信
3. 必要に応じて水先人の手配

### 3. 緊急事態対応フロー
1. 船舶が緊急警報を送信
2. VTSが即座に応答
3. 支援船の派遣調整

## MRN（Maritime Resource Name）の例

### 船舶
- `urn:mrn:mcp:vessel:imo:1234567` - IMO番号ベース
- `urn:mrn:mcp:vessel:mmsi:987654321` - MMSI番号ベース

### 拠点
- `urn:mrn:mcp:shore:authority:vts:tokyo-bay` - 東京湾VTS
- `urn:mrn:mcp:shore:port:yokohama` - 横浜港管制
- `urn:mrn:mcp:shore:pilot:tokyo` - 東京水先区

## メッセージタイプ

### 船舶→拠点
- `position_report` - 位置報告
- `port_entry_request` - 入港要請
- `distress_alert` - 遭難警報
- `status_update` - 状態更新

### 拠点→船舶
- `navigation_instruction` - 航行指示
- `port_clearance` - 入港許可
- `weather_alert` - 気象警報
- `acknowledgment` - 確認応答

## トラブルシューティング

### 接続エラー
```bash
# MMSサービスの状態確認
curl http://localhost:8083/health

# WebSocket接続のテスト
wscat -c ws://localhost:8083/ws/urn:mrn:mcp:vessel:imo:1234567
```

### メッセージ送信エラー
```bash
# REST APIでのメッセージ送信テスト
curl -X POST http://localhost:8083/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sender_mrn": "urn:mrn:mcp:vessel:imo:1234567",
    "recipient_mrn": "urn:mrn:mcp:shore:authority:vts:tokyo-bay",
    "message_type": "position_report",
    "subject": "Test Message",
    "body": "This is a test message"
  }'
```

### アクティブ接続の確認
```bash
# 現在のWebSocket接続を確認
curl http://localhost:8083/api/v1/connections
```

## 実装のポイント

### WebSocket接続管理
- 自動再接続機能の実装
- 接続状態の監視
- エラー時の適切な処理

### メッセージの重複防止
- 一意のメッセージIDの生成
- 送信済みメッセージの追跡
- タイムアウト処理

### セキュリティ考慮事項
- MRNの検証
- メッセージの署名・検証
- 不正なメッセージの拒否

## 海図データデモ

### chart_data_demo.py
**Pythonベースの海図データ送受信デモ**

- 航路計画（RTZ形式）の送信
- 測深データのストリーミング
- 航行警報の配信
- REST APIによる海図更新通知

**使用方法:**
```bash
# デモスクリプトを実行
python examples/chart_data_demo.py
```

### chart_viewer.html
**ブラウザベースの海図データビューアー**

- インタラクティブな地図表示（Leaflet使用）
- 航路の可視化
- 測深データのヒートマップ表示
- 航行警報エリアの表示
- リアルタイムデータ受信

**使用方法:**
```bash
# ブラウザでHTMLファイルを開く
open examples/chart_viewer.html
```

## 海図データの種類

### 航路計画データ
- RTZ (Route Exchange Format) 形式
- 航路点、速度、ETA情報
- 最適化基準（最短、最安全、最経済的）

### 測深データ
- バッチ送信とストリーミング送信
- 品質指標付きの水深情報
- 測定方法（シングルビーム、マルチビーム）

### 航行警報
- 障害物、制限区域、気象警報
- WKT形式での地理情報
- 重要度レベル（critical, major, minor）

## 関連ドキュメント

- [MCP船舶メッセージング実装ガイド](../../docs/MCP船舶メッセージング実装ガイド.md)
- [MCP海図データ送受信ガイド](../../docs/MCP海図データ送受信ガイド.md)
- [MCP技術仕様](../../docs/MCP技術仕様.md)
- [デモ環境README](../README.md)
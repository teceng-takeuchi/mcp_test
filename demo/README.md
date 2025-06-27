# MCP Demo Environment

Maritime Connectivity Platform (MCP) のデモ環境です。MCPの3つのコアコンポーネント（MIR、MSR、MMS）を実際に動かして体験できます。

## 概要

このデモ環境では以下のコンポーネントが動作します：

- **MIR (Maritime Identity Registry)**: 海事組織とアイデンティティ管理
- **MSR (Maritime Service Registry)**: 海事サービスの登録と検索
- **MMS (Maritime Messaging Service)**: 海事メッセージング
- **PostgreSQL**: データベース
- **Redis**: キャッシュとセッション管理
- **Keycloak**: アイデンティティブローカー（認証）
- **Nginx**: リバースプロキシ
- **Kafka & Zookeeper**: メッセージブローカー

## 前提条件

- Docker 20.10以上
- Docker Compose 2.0以上
- 8GB以上のRAM
- 10GB以上の空きディスク容量

## クイックスタート

### 1. デモ環境の起動

```bash
# プロジェクトルートで実行
cd demo

# 全サービスを起動
./scripts/start.sh
```

または手動で：

```bash
cd demo
docker-compose up -d
```

### 2. サービスの確認

起動には数分かかります。以下のコマンドで状態を確認できます：

```bash
# すべてのサービスの状態を確認
docker-compose ps

# ログの確認
docker-compose logs -f
```

### 3. アクセスURL

| サービス | URL | 説明 |
|---------|-----|------|
| MIR API | http://localhost:8081 | 組織・アイデンティティ管理 |
| MSR API | http://localhost:8082 | サービス登録・検索 |
| MMS API | http://localhost:8083 | メッセージング |
| Nginx Gateway | http://localhost | 統合API ゲートウェイ |
| Keycloak | http://localhost:8080 | 認証サーバー |

### 4. API ドキュメント

各サービスのSwagger UIでAPIを確認・テストできます：

- MIR: http://localhost:8081/docs
- MSR: http://localhost:8082/docs
- MMS: http://localhost:8083/docs

## 使用例

### MIR - 組織管理

```bash
# 組織一覧の取得
curl http://localhost:8081/api/v1/organizations

# 新しい組織の作成
curl -X POST http://localhost:8081/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "urn:mrn:mcp:org:example:test",
    "name": "Test Organization",
    "country": "JP",
    "description": "テスト組織"
  }'

# 特定組織の取得
curl http://localhost:8081/api/v1/organizations/urn:mrn:mcp:org:example:test
```

### MSR - サービス管理

```bash
# サービス仕様一覧の取得
curl http://localhost:8082/api/v1/serviceSpecifications

# サービスインスタンス一覧の取得
curl http://localhost:8082/api/v1/serviceInstances

# サービス検索（キーワード）
curl "http://localhost:8082/api/v1/search/services?keywords=weather"

# サービス検索（地理的範囲）
curl "http://localhost:8082/api/v1/search/services?location=139.7,35.6&radius=10"
```

### MMS - メッセージング

```bash
# メッセージ送信
curl -X POST http://localhost:8083/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sender_mrn": "urn:mrn:mcp:vessel:imo:1234567",
    "recipient_mrn": "urn:mrn:mcp:shore:authority:vts",
    "message_type": "text",
    "subject": "Position Report",
    "body": "Current position: 35.6762° N, 139.6503° E"
  }'

# メッセージ一覧の取得
curl http://localhost:8083/api/v1/messages

# アクティブな接続一覧
curl http://localhost:8083/api/v1/connections
```

## WebSocket接続（MMS）

MMSはWebSocketを通じてリアルタイムメッセージングをサポートします：

```javascript
// JavaScript例
const ws = new WebSocket('ws://localhost:8083/ws/urn:mrn:mcp:vessel:imo:1234567');

ws.onopen = function(event) {
    console.log('Connected to MMS');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received message:', data);
};

// メッセージ送信
ws.send(JSON.stringify({
    "recipient_mrn": "urn:mrn:mcp:shore:authority:vts",
    "message_type": "text",
    "subject": "Test Message",
    "body": "Hello from vessel!"
}));
```

## デモデータ

デモ環境には以下のサンプルデータが含まれています：

### 組織
- `urn:mrn:mcp:org:demo:maritime-authority` - Demo Maritime Authority
- `urn:mrn:mcp:org:demo:shipping-company` - Demo Shipping Company  
- `urn:mrn:mcp:org:demo:port-authority` - Demo Port Authority

### サービス
- Weather Information Service (天気情報)
- Vessel Tracking Service (船舶追跡)
- Port Information Service (港湾情報)

## 管理コマンド

### 環境の停止

```bash
# すべてのサービスを停止
./scripts/stop.sh

# または
docker-compose stop
```

### 環境のリセット

```bash
# すべてのデータを削除して再起動
./scripts/reset.sh

# または
docker-compose down -v
docker-compose up -d
```

### ログの確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f mir
docker-compose logs -f msr
docker-compose logs -f mms
```

### 健康状態の確認

```bash
# 全サービスの健康チェック
./scripts/health-check.sh
```

**✅ 正常動作確認済みサービス:**
- MIR (Maritime Identity Registry) - 組織・アイデンティティ管理
- MSR (Maritime Service Registry) - サービス登録・検索  
- MMS (Maritime Messaging Service) - メッセージング
- Keycloak - 認証サーバー
- PostgreSQL - データベース（PostGIS拡張含む）
- Redis - キャッシュ・セッション管理

**📝 注意事項:**
- Nginxリバースプロキシは起動していますが、ヘルスチェックから除外されています
- 各サービスには直接アクセス可能です（個別ポート経由）

## 開発

### 個別サービスの開発

各サービスは独立して開発・テストできます：

```bash
# MIRのみ再ビルド・再起動
docker-compose up -d --build mir

# MSRのみ再ビルド・再起動
docker-compose up -d --build msr

# MMSのみ再ビルド・再起動
docker-compose up -d --build mms
```

### 設定のカスタマイズ

環境変数は`.env`ファイルで変更できます：

```bash
# データベースパスワードの変更例
echo "DB_PASSWORD=your_secure_password" >> .env
```

## トラブルシューティング

### よくある問題

1. **ポートが使用済み**
   ```bash
   # 使用中のポートを確認
   lsof -i :8080
   lsof -i :8081
   lsof -i :8082
   lsof -i :8083
   ```

2. **メモリ不足**
   ```bash
   # Dockerのメモリ使用量を確認
   docker stats
   ```

3. **データベース接続エラー**
   ```bash
   # PostgreSQLの状態を確認
   docker-compose exec postgres pg_isready -U mcp
   ```

4. **サービスが起動しない**
   ```bash
   # 依存関係を確認
   docker-compose up postgres redis
   # その後他のサービス
   docker-compose up -d
   ```

5. **MSRの地理空間機能エラー**
   ```bash
   # PostGIS拡張が正しく読み込まれているか確認
   docker-compose exec postgres psql -U mcp -d msr_db -c "SELECT postgis_version();"
   ```

6. **NumPy/Shapely依存関係エラー**
   ```bash
   # MSRコンテナを再ビルド
   docker-compose up -d --build msr
   ```

### ログの分析

```bash
# エラーログのみ表示
docker-compose logs | grep -i error

# 特定時間のログ
docker-compose logs --since="2024-01-01T00:00:00"
```

## セキュリティ注意事項

⚠️ **重要**: このデモ環境は学習・評価目的のみです。

- デフォルトパスワードを使用しています
- 認証・認可は簡略化されています
- 本番環境では使用しないでください

## 参考資料

- [MCP概要](../docs/MCP概要.md)
- [MCP技術仕様](../docs/MCP技術仕様.md)
- [MCP実装例](../docs/MCP実装例.md)
- [Docker環境セットアップ](../docs/Docker環境セットアップ.md)

## ライセンス

このデモ環境はMITライセンスの下で提供されています。
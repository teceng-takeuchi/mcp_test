# Maritime Connectivity Platform (MCP) Demo Project

🚢 **MCP学習・研究・デモ用プロジェクト**

Maritime Connectivity Platform (MCP) の3つのコアコンポーネント（MIR、MSR、MMS）を学習し、実際に体験できる包括的なプロジェクトです。

## 🎯 プロジェクト目的

- MCPの理解を深めるための詳細なドキュメント提供
- 実際に動作するMCPデモ環境の提供
- 海事デジタル化とサービス指向アーキテクチャの学習支援

## 📁 プロジェクト構成

```
mcp_test/
├── 📚 docs/              # 包括的なMCPドキュメント
├── 🎮 demo/              # 動作するデモ環境  
├── 📄 README.md          # このファイル
└── 📋 CLAUDE.md          # 開発者向けガイド
```

## 🚀 クイックスタート

### 1. デモ環境を体験する

最短でMCPを体験したい場合：

```bash
# デモ環境を起動
cd demo
./scripts/start.sh

# 体験シナリオを実行
./scripts/demo.sh
```

### 2. ドキュメントで学習する

MCPを理解したい場合、まずドキュメントを読んでください：

- 📖 [MCP概要](docs/MCP概要.md) - MCPの基本概念
- 🔧 [MCP技術仕様](docs/MCP技術仕様.md) - 技術詳細
- 🏗️ [MCP模擬環境構築ガイド](docs/MCP模擬環境構築ガイド.md) - 環境構築指針
- 🐳 [Docker環境セットアップ](docs/Docker環境セットアップ.md) - Docker詳細
- 💻 [MCP実装例](docs/MCP実装例.md) - Python実装例

## 🏗️ MCPアーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Platform                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   🆔 MIR     │    │   📋 MSR     │    │   💬 MMS     │ │
│  │ (Identity)   │◄───┤ (Service)    │◄───┤ (Messaging)  │ │
│  │              │    │ Registry     │    │              │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 🆔 MIR (Maritime Identity Registry)
- **機能**: 海事組織とアイデンティティの管理
- **役割**: 認証・認可、証明書管理
- **ポート**: 8081

### 📋 MSR (Maritime Service Registry)
- **機能**: 海事サービスの登録、検索、管理
- **役割**: サービス仕様管理、サービス検索
- **ポート**: 8082

### 💬 MMS (Maritime Messaging Service)
- **機能**: 海事メッセージング、リアルタイム通信
- **役割**: メッセージルーティング、WebSocket通信
- **ポート**: 8083

## 🎮 デモ環境詳細

### 前提条件
- Docker 20.10以上
- Docker Compose 2.0以上
- 8GB以上のRAM
- 10GB以上の空きディスク容量

### 起動方法

```bash
cd demo
./scripts/start.sh
```

### アクセスURL

| サービス | URL | 説明 |
|---------|-----|------|
| 🌐 統合API Gateway | http://localhost | 全サービス統合エンドポイント |
| 🆔 MIR API | http://localhost:8081/docs | アイデンティティ管理API |
| 📋 MSR API | http://localhost:8082/docs | サービス登録・検索API |
| 💬 MMS API | http://localhost:8083/docs | メッセージングAPI |
| 🔐 Keycloak | http://localhost:8080 | 認証サーバー |

### 管理コマンド

```bash
# 環境管理
./scripts/start.sh        # 起動
./scripts/stop.sh         # 停止
./scripts/reset.sh        # リセット

# 監視・デバッグ
./scripts/health-check.sh # ヘルスチェック
./scripts/demo.sh         # デモシナリオ実行

# Docker操作
docker-compose logs -f    # ログ確認
docker-compose ps         # 状態確認
```

## 📖 ドキュメント詳細

### 🎯 学習順序（推奨）

1. **[MCP概要](docs/MCP概要.md)** ← まずここから
   - MCPとは何か
   - 3つのコアコンポーネント
   - 基本概念と用語

2. **[MCP技術仕様](docs/MCP技術仕様.md)**
   - アーキテクチャ詳細
   - API仕様
   - セキュリティ要件

3. **[MCP実装例](docs/MCP実装例.md)**
   - Python/FastAPI実装
   - 各コンポーネントのコード例
   - テスト方法

4. **[Docker環境セットアップ](docs/Docker環境セットアップ.md)**
   - Docker Compose設定
   - 環境変数
   - トラブルシューティング

5. **[MCP模擬環境構築ガイド](docs/MCP模擬環境構築ガイド.md)**
   - 本格的な環境構築
   - セキュリティ考慮事項
   - 運用のベストプラクティス

## 🔧 技術スタック

### バックエンド
- **Python 3.11** - プログラミング言語
- **FastAPI** - Webフレームワーク
- **SQLAlchemy** - ORM
- **PostgreSQL** - データベース
- **Redis** - キャッシュ・セッション
- **Kafka** - メッセージブローカー

### インフラストラクチャ
- **Docker & Docker Compose** - コンテナ化
- **Nginx** - リバースプロキシ
- **Keycloak** - アイデンティティ管理

### 地理空間・暗号化
- **Shapely** - 地理空間データ処理
- **cryptography** - PKI・証明書管理

## 🎯 使用例・シナリオ

### 基本操作例

```bash
# 組織の作成
curl -X POST http://localhost:8081/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "urn:mrn:mcp:org:example:shipping",
    "name": "Example Shipping Company",
    "country": "JP"
  }'

# サービス検索
curl "http://localhost:8082/api/v1/search/services?keywords=weather"

# メッセージ送信
curl -X POST http://localhost:8083/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sender_mrn": "urn:mrn:mcp:vessel:imo:1234567",
    "recipient_mrn": "urn:mrn:mcp:shore:authority:vts",
    "subject": "Position Report",
    "body": "Current position: 35.6762°N, 139.6503°E"
  }'
```

### デモシナリオ

自動化されたデモシナリオを実行できます：

```bash
cd demo
./scripts/demo.sh
```

このシナリオでは以下を体験できます：
- 🏢 組織の登録・管理
- 📋 サービス仕様の作成
- 🔍 サービスの検索（キーワード・地理的範囲）
- 💬 メッセージの送受信
- 📊 統計情報の確認

## 🚨 注意事項

⚠️ **重要**: このプロジェクトは学習・評価・デモ目的のみです。

- デフォルトパスワードを使用
- 認証・認可は簡略化
- セキュリティ設定は本番レベルではない
- **本番環境では使用しないでください**

## 🛠️ トラブルシューティング

### よくある問題

1. **ポート競合**
   ```bash
   # ポート使用状況確認
   lsof -i :8080
   lsof -i :8081
   lsof -i :8082
   lsof -i :8083
   ```

2. **メモリ不足**
   ```bash
   # Dockerメモリ使用量確認
   docker stats
   ```

3. **起動失敗**
   ```bash
   # ログ確認
   docker-compose logs -f
   
   # 段階的起動
   docker-compose up postgres redis  # まずDB
   docker-compose up -d              # 次に全体
   ```

4. **データベース問題**
   ```bash
   # DB接続確認
   docker-compose exec postgres pg_isready -U mcp
   ```

### ヘルプ

問題が解決しない場合：

1. `demo/scripts/health-check.sh` でシステム状態を確認
2. `demo/scripts/reset.sh` で環境をリセット
3. ドキュメントのトラブルシューティング項目を確認

## 📚 参考資料

### 公式リソース
- [MCP公式サイト](https://maritimeconnectivity.net/)
- [MCP技術文書](https://docs.maritimeconnectivity.net/)
- [MCPコンソーシアム](https://www.linkedin.com/company/maritime-connectivity-platform-consortium)

### 関連技術
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://docs.docker.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Keycloak](https://www.keycloak.org/documentation)

### 標準規格
- IALA Guideline G1128 (サービス仕様)
- IALA Guideline G1183 (セキュアアイデンティティ)
- RTCM Standard 13900.0 (MMS)

## 🤝 コントリビューション

このプロジェクトは学習目的のため、以下の貢献を歓迎します：

- 📝 ドキュメントの改善
- 🐛 バグレポート
- 💡 機能提案
- 🧪 テストケースの追加

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

---

**🚢 Happy Maritime Computing! ⚓**
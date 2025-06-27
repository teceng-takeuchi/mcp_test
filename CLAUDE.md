# CLAUDE.md

このファイルは、このリポジトリのコードを扱う際のClaude Code (claude.ai/code) への指針を提供します。

## プロジェクト概要

「mcp_test」はMaritime Connectivity Platform (MCP) の学習・研究・デモ用プロジェクトです。MCPの3つのコアコンポーネント（MIR、MSR、MMS）の包括的なドキュメントと動作するデモ環境を提供します。

## MCPについて

このプロジェクトにおいてMCPという単語はMaritime Connectivity Platformの事を指します。

## 開発セットアップ

### ドキュメント閲覧
MCPの理解を深めるために、まず`/docs`ディレクトリのドキュメントを参照してください：

1. **MCP概要.md** - MCPの基本概念と全体像
2. **MCP技術仕様.md** - 技術的な詳細仕様
3. **MCP模擬環境構築ガイド.md** - 環境構築の指針
4. **Docker環境セットアップ.md** - Docker環境の詳細
5. **MCP実装例.md** - Python/FastAPIベースの実装例

### デモ環境の起動
実際にMCPを体験するには、`/demo`ディレクトリのデモ環境を使用してください：

```bash
cd demo
./scripts/start.sh
```

**✅ 動作確認済み（2025年6月19日時点）:**
全てのコアMCPサービスが正常に動作することを確認済みです：
- MIR、MSR、MMSの3つの主要サービス
- PostgreSQL（PostGIS拡張付き）、Redis、Keycloak
- 地理空間検索、Pydantic v2対応、NumPy互換性対応済み

### 必要な前提条件
- Docker 20.10以上
- Docker Compose 2.0以上
- 8GB以上のRAM
- 10GB以上の空きディスク容量

## プロジェクト構造

```
mcp_test/
├── docs/                           # 包括的なMCPドキュメント
│   ├── MCP概要.md
│   ├── MCP技術仕様.md
│   ├── MCP模擬環境構築ガイド.md
│   ├── Docker環境セットアップ.md
│   └── MCP実装例.md
├── demo/                           # 動作するデモ環境
│   ├── docker-compose.yml         # 全サービス定義
│   ├── .env                        # 環境変数
│   ├── mir/                        # Maritime Identity Registry
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── msr/                        # Maritime Service Registry
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── mms/                        # Maritime Messaging Service
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── nginx/                      # リバースプロキシ
│   │   └── nginx.conf
│   ├── postgres/                   # データベース初期化
│   │   └── init.sql
│   ├── scripts/                    # 管理スクリプト
│   │   ├── start.sh               # 環境起動
│   │   ├── stop.sh                # 環境停止
│   │   ├── reset.sh               # 環境リセット
│   │   ├── health-check.sh        # ヘルスチェック
│   │   └── demo.sh                # デモシナリオ実行
│   └── README.md                   # デモ環境ガイド
├── package.json                    # プロジェクト設定
├── package-lock.json
└── CLAUDE.md                       # このファイル
```

## MCPコンポーネント

### MIR (Maritime Identity Registry)
- **ポート**: 8081
- **機能**: 海事組織とアイデンティティの管理
- **技術**: Python/FastAPI + PostgreSQL
- **API**: http://localhost:8081/docs

### MSR (Maritime Service Registry)
- **ポート**: 8082  
- **機能**: 海事サービスの登録、検索、管理
- **技術**: Python/FastAPI + PostgreSQL + 地理空間検索
- **API**: http://localhost:8082/docs

### MMS (Maritime Messaging Service)
- **ポート**: 8083
- **機能**: 海事メッセージング、WebSocket通信
- **技術**: Python/FastAPI + WebSocket + Redis
- **API**: http://localhost:8083/docs

## デモ環境の使用方法

### 起動
```bash
cd demo
./scripts/start.sh
```

### 体験シナリオ実行
```bash
cd demo
./scripts/demo.sh
```

### 停止・リセット
```bash
./scripts/stop.sh    # 停止
./scripts/reset.sh   # 完全リセット
```

### ヘルスチェック
```bash
./scripts/health-check.sh
```

**注記**: ヘルスチェックでは以下のサービスを確認します：
- MIR, MSR, MMS（MCPコアサービス）
- Keycloak（認証サーバー）  
- PostgreSQL, Redis（データストア）

## アクセスURL

- **統合API Gateway**: http://localhost
- **MIR API**: http://localhost:8081/docs
- **MSR API**: http://localhost:8082/docs  
- **MMS API**: http://localhost:8083/docs
- **Keycloak**: http://localhost:8080

## 注記

- デモ環境は学習・評価目的のみです
- デフォルトパスワードを使用しています
- 本番環境では使用しないでください
- 必要に応じてこのファイルは適時編集すること
    - 編集する場合はユーザーに確認を求めて
    - 追記の場合は確認不要

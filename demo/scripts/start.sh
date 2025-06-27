#!/bin/bash

echo "🚢 MCPデモ環境を起動しています..."

# 現在のディレクトリを確認
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.ymlが見つかりません。demoディレクトリで実行してください。"
    exit 1
fi

# Docker Composeで起動
echo "📦 Dockerサービスを起動中..."
docker-compose up -d

# 起動状況をチェック
echo "⏳ サービスの起動を待機中..."
sleep 10

# ヘルスチェック
echo "🔍 サービスの状態をチェック中..."
docker-compose ps

echo ""
echo "✅ MCPデモ環境の起動が完了しました！"
echo ""
echo "🌐 アクセスURL:"
echo "  - MIR API:      http://localhost:8081"
echo "  - MSR API:      http://localhost:8082" 
echo "  - MMS API:      http://localhost:8083"
echo "  - Nginx Gateway: http://localhost"
echo "  - Keycloak:     http://localhost:8080"
echo ""
echo "📚 API ドキュメント:"
echo "  - MIR Swagger:  http://localhost:8081/docs"
echo "  - MSR Swagger:  http://localhost:8082/docs"
echo "  - MMS Swagger:  http://localhost:8083/docs"
echo ""
echo "🔧 管理コマンド:"
echo "  - 停止:         ./scripts/stop.sh"
echo "  - リセット:     ./scripts/reset.sh"
echo "  - ヘルスチェック: ./scripts/health-check.sh"
echo ""
echo "📋 ログ確認: docker-compose logs -f"
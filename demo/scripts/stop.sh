#!/bin/bash

echo "🛑 MCPデモ環境を停止しています..."

# 現在のディレクトリを確認
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.ymlが見つかりません。demoディレクトリで実行してください。"
    exit 1
fi

# Docker Composeで停止
docker-compose stop

echo ""
echo "✅ MCPデモ環境が停止しました。"
echo ""
echo "🔧 その他の操作:"
echo "  - 完全削除（データも削除）: ./scripts/reset.sh"
echo "  - 再起動:                   ./scripts/start.sh"
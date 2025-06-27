#!/bin/bash

echo "🔄 MCPデモ環境をリセットしています..."

# 現在のディレクトリを確認
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.ymlが見つかりません。demoディレクトリで実行してください。"
    exit 1
fi

# 確認プロンプト
read -p "⚠️  すべてのデータが削除されます。続行しますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ リセットをキャンセルしました。"
    exit 1
fi

# すべてのコンテナとボリュームを削除
echo "🗑️  コンテナとボリュームを削除中..."
docker-compose down -v

# イメージも削除するかオプション
read -p "🐳 Dockerイメージも削除しますか？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Dockerイメージを削除中..."
    docker-compose down --rmi all -v
fi

# 再起動
echo "🚀 環境を再起動中..."
./scripts/start.sh
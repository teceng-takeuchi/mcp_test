#!/bin/bash

echo "🔍 MCPデモ環境のヘルスチェックを実行中..."

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ヘルスチェック関数
check_service() {
    local service_name="$1"
    local url="$2"
    local max_retries=3
    
    echo -n "  ${service_name}: "
    
    for i in $(seq 1 $max_retries); do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        fi
        sleep 2
    done
    
    echo -e "${RED}❌ FAILED${NC}"
    return 1
}

echo ""
echo "🌐 サービス状態:"

# 各サービスをチェック
check_service "MIR          " "http://localhost:8081/health"
check_service "MSR          " "http://localhost:8082/health"  
check_service "MMS          " "http://localhost:8083/health"
check_service "Nginx Gateway" "http://localhost/health"
check_service "Keycloak     " "http://localhost:8080/health"

echo ""
echo "🐳 Docker コンテナ状態:"
docker-compose ps

echo ""
echo "💾 データベース接続テスト:"
if docker-compose exec -T postgres pg_isready -U mcp > /dev/null 2>&1; then
    echo -e "  PostgreSQL: ${GREEN}✅ OK${NC}"
else
    echo -e "  PostgreSQL: ${RED}❌ FAILED${NC}"
fi

if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "  Redis:      ${GREEN}✅ OK${NC}"
else
    echo -e "  Redis:      ${RED}❌ FAILED${NC}"
fi

echo ""
echo "📊 リソース使用状況:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -6

echo ""
echo "🔗 便利なコマンド:"
echo "  ログ確認:     docker-compose logs -f [service_name]"
echo "  シェル接続:   docker-compose exec [service_name] bash"
echo "  DB接続:       docker-compose exec postgres psql -U mcp"
echo "  Redis接続:    docker-compose exec redis redis-cli"
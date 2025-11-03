#!/bin/bash

# Configuración
TARGET_URL="http://localhost:8081"
REQUESTS_PER_SECOND=1000
DURATION_MINUTES=30
CONCURRENT_REQUESTS=100

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Load Test Script ===${NC}"
echo -e "${YELLOW}Target:${NC} $TARGET_URL"
echo -e "${YELLOW}Requests/sec:${NC} $REQUESTS_PER_SECOND"
echo -e "${YELLOW}Duration:${NC} $DURATION_MINUTES minutes"
echo -e "${YELLOW}Concurrent:${NC} $CONCURRENT_REQUESTS"
echo ""

# Función para enviar una petición
send_request() {
    local id=$1
    curl -s -o /dev/null -w "Request $id - Status: %{http_code} - Time: %{time_total}s\n" "$TARGET_URL"
}

# Calcular cuántas peticiones totales
TOTAL_REQUESTS=$((REQUESTS_PER_SECOND * DURATION_MINUTES * 60))
# Calcular delay en bash puro (microsegundos)
DELAY_US=$((1000000 / REQUESTS_PER_SECOND))
DELAY_DISPLAY=$(awk "BEGIN {printf \"%.3f\", 1/$REQUESTS_PER_SECOND}")

echo -e "${GREEN}Starting load test...${NC}"
echo -e "${YELLOW}Total requests:${NC} $TOTAL_REQUESTS"
echo -e "${YELLOW}Delay between requests:${NC} ${DELAY_DISPLAY}s"
echo ""

START_TIME=$(date +%s)
SUCCESS_COUNT=0
ERROR_COUNT=0

# Loop principal
for i in $(seq 1 $TOTAL_REQUESTS); do
    # Lanzar peticiones en paralelo
    for j in $(seq 1 $CONCURRENT_REQUESTS); do
        {
            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET_URL")
            if [ "$RESPONSE" = "200" ]; then
                ((SUCCESS_COUNT++))
            else
                ((ERROR_COUNT++))
            fi
        } &
    done
    
    # Mostrar progreso cada 50 requests
    if [ $((i % 50)) -eq 0 ]; then
        ELAPSED=$(($(date +%s) - START_TIME))
        if [ $ELAPSED -gt 0 ]; then
            RPS=$(((SUCCESS_COUNT + ERROR_COUNT) / ELAPSED))
        else
            RPS=0
        fi
        echo -e "${GREEN}Progress:${NC} $i/$TOTAL_REQUESTS requests | ${GREEN}Success:${NC} $SUCCESS_COUNT | ${RED}Errors:${NC} $ERROR_COUNT | ${YELLOW}RPS:${NC} $RPS"
    fi
    
    # Esperar antes del siguiente batch (usando microsegundos para mayor precisión)
    sleep 0."$(printf "%06d" $((DELAY_US)))"
    
    # Esperar a que terminen las peticiones en paralelo
    wait
done

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo ""
echo -e "${GREEN}=== Test Complete ===${NC}"
echo -e "${YELLOW}Total time:${NC} ${TOTAL_TIME}s"
echo -e "${GREEN}Successful requests:${NC} $SUCCESS_COUNT"
echo -e "${RED}Failed requests:${NC} $ERROR_COUNT"
if [ $TOTAL_TIME -gt 0 ]; then
    AVG_RPS=$(((SUCCESS_COUNT + ERROR_COUNT) / TOTAL_TIME))
    echo -e "${YELLOW}Average RPS:${NC} $AVG_RPS"
fi
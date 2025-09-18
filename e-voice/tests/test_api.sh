#!/bin/bash

# REST API 接口测试脚本
# 用于测试 rest.py 中的HTTP接口

SERVER_URL="http://localhost:5000"
AUDIO_FILE="../resource/1分20.wav"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== REST API 接口测试 ===${NC}"
echo "服务器地址: $SERVER_URL"
echo "音频文件: $AUDIO_FILE"
echo

# 检查服务器是否运行
echo "检查服务器状态..."
if ! curl -s --connect-timeout 5 $SERVER_URL/ > /dev/null; then
    echo -e "${RED}✗ 服务器未运行或无法连接${NC}"
    echo "请确保运行: python rest.py"
    exit 1
else
    echo -e "${GREEN}✓ 服务器正在运行${NC}"
fi
echo

# 测试1: 健康检查接口
echo -e "${CYAN}1. 测试健康检查接口 GET /${NC}"
response=$(curl -s -w "%{http_code}" -X GET $SERVER_URL/)
http_code="${response: -3}"
body="${response%???}"
echo "HTTP状态码: $http_code"
echo "响应内容: $body"
if [ "$http_code" = "200" ] && [ "$body" = "success" ]; then
    echo -e "${GREEN}结果: ✓ 成功${NC}"
else
    echo -e "${RED}结果: ✗ 失败${NC}"
fi
echo

# 测试2: Embedding接口
echo -e "${CYAN}2. 测试Embedding接口 POST /embedding${NC}"
response=$(curl -s -w "%{http_code}" -X POST $SERVER_URL/embedding \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "message": "hello"}')
http_code="${response: -3}"
body="${response%???}"
echo "HTTP状态码: $http_code"
echo "响应内容: $body"
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}结果: ✓ 成功${NC}"
else
    echo -e "${RED}结果: ✗ 失败${NC}"
fi
echo

# 测试3: 语音注册接口
echo -e "${CYAN}3. 测试语音注册接口 POST /voice-register${NC}"
if [ -f "$AUDIO_FILE" ]; then
    echo "音频文件: $AUDIO_FILE"
    file_size=$(ls -lh "$AUDIO_FILE" | awk '{print $5}')
    echo "文件大小: $file_size"
    
    echo "发送请求中..."
    response=$(curl -s -w "%{http_code}" -X POST $SERVER_URL/voice-register \
      -F "audio=@$AUDIO_FILE" \
      -F "username=test_user" \
      -F "userid=123")
    http_code="${response: -3}"
    body="${response%???}"
    echo "HTTP状态码: $http_code"
    echo "响应内容: $body"
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}结果: ✓ 成功${NC}"
        # 如果有jq工具，格式化JSON输出
        if command -v jq >/dev/null 2>&1; then
            echo "格式化响应:"
            echo "$body" | jq .
        fi
    else
        echo -e "${RED}结果: ✗ 失败${NC}"
    fi
else
    echo -e "${YELLOW}音频文件不存在: $AUDIO_FILE${NC}"
    echo -e "${YELLOW}结果: ⚠ 跳过${NC}"
    echo "可用的音频文件:"
    find ../resource/ -name "*.wav" -o -name "*.mp3" 2>/dev/null | head -3
fi
echo

# 测试4: CORS检查
echo -e "${CYAN}4. 测试CORS支持${NC}"
cors_response=$(curl -s -X OPTIONS $SERVER_URL/voice-register \
  -H "Origin: http://localhost:3000" \
  -D -)
cors_headers=$(echo "$cors_response" | grep -i "access-control")
echo "CORS响应头:"
echo "$cors_headers"
if [[ "$cors_headers" == *"Access-Control-Allow-Origin"* ]]; then
    echo -e "${GREEN}结果: ✓ 支持CORS${NC}"
else
    echo -e "${RED}结果: ✗ 不支持CORS${NC}"
fi
echo

# 测试5: 错误处理测试
echo -e "${CYAN}5. 测试错误处理${NC}"
response=$(curl -s -w "%{http_code}" -X POST $SERVER_URL/voice-register \
  -F "username=test_user" \
  -F "userid=123")
http_code="${response: -3}"
body="${response%???}"
echo "无音频文件请求 - HTTP状态码: $http_code"
if [ "$http_code" = "400" ]; then
    echo -e "${GREEN}结果: ✓ 正确返回400错误${NC}"
else
    echo -e "${YELLOW}结果: ⚠ 状态码异常${NC}"
fi
echo

# 测试6: 响应时间
echo -e "${CYAN}6. 测试响应时间${NC}"
time_result=$(curl -s -w "%{time_total}" -o /dev/null $SERVER_URL/)
echo "健康检查接口响应时间: ${time_result}秒"
echo

echo -e "${CYAN}=== 测试完成 ===${NC}"
echo -e "${GREEN}如果所有测试通过，您的REST API服务正常工作！${NC}" 
#!/bin/bash
# 启动高性能异步 WebSocket 服务
# 使用原生 websockets 库，与 FunASR Demo 一致
# 
# 使用方法:
#   ./start_wss_demo.sh                    # 默认端口 10096，无 SSL
#   ./start_wss_demo.sh --ssl              # 默认端口 10096，启用 SSL
#   ./start_wss_demo.sh --port 10097       # 自定义端口
#   ./start_wss_demo.sh --port 10097 --ssl # 自定义端口 + SSL
#
# 注意: 此服务独立于主 Flask 服务 (rest.py)

# 默认配置
PORT=10096
HOST="0.0.0.0"
USE_SSL=false
CERTFILE=""
KEYFILE=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --ssl)
            USE_SSL=true
            shift
            ;;
        --certfile)
            CERTFILE="$2"
            shift 2
            ;;
        --keyfile)
            KEYFILE="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 切换到脚本所在目录
cd "$(dirname "$0")"

# SSL 证书路径（默认使用项目中的 ssl_key）
if [ "$USE_SSL" = true ]; then
    if [ -z "$CERTFILE" ]; then
        CERTFILE="ssl_key/server.crt"
    fi
    if [ -z "$KEYFILE" ]; then
        KEYFILE="ssl_key/server.key"
    fi
    
    # 检查证书文件是否存在
    if [ ! -f "$CERTFILE" ]; then
        echo "❌ 证书文件不存在: $CERTFILE"
        exit 1
    fi
    if [ ! -f "$KEYFILE" ]; then
        echo "❌ 密钥文件不存在: $KEYFILE"
        exit 1
    fi
fi

echo "🚀 启动高性能异步 WebSocket 服务..."
echo "   地址: $HOST"
echo "   端口: $PORT"
if [ "$USE_SSL" = true ]; then
    echo "   SSL: 已启用"
    echo "   证书: $CERTFILE"
    echo "   密钥: $KEYFILE"
else
    echo "   SSL: 未启用 (使用 --ssl 启用)"
fi
echo ""
echo "📝 协议说明:"
echo "   1. 连接后首先发送配置 JSON (chunk_size, mode, is_speaking 等)"
echo "   2. 之后直接发送二进制音频帧 (PCM 16kHz 16bit)"
echo "   3. 停止时发送 is_speaking=false 的 JSON"
echo ""

# 构建命令 - 直接运行 wss_demo.py（避免触发 server 包的数据库依赖）
CMD="python server/wss_demo.py --host $HOST --port $PORT"
if [ "$USE_SSL" = true ]; then
    CMD="$CMD --certfile $CERTFILE --keyfile $KEYFILE"
fi

echo "执行: $CMD"
echo ""
exec $CMD


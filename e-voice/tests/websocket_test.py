#!/usr/bin/env python3
"""
WebSocket连接测试脚本
用于验证实时语音识别的WebSocket连接是否正常
"""

import asyncio
import websockets
import json
import base64
import time

async def test_websocket():
    """测试WebSocket连接和消息处理"""
    uri = "ws://localhost:8210/ws/recognize"
    
    try:
        print(f"正在连接: {uri}")
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接成功!")
            
            # 发送开始消息
            start_message = {
                "type": "start"
            }
            await websocket.send(json.dumps(start_message))
            print("已发送开始消息")
            
            # 等待响应
            response = await websocket.recv()
            print(f"收到响应: {response}")
            
            # 发送结束消息
            end_message = {
                "type": "end"
            }
            await websocket.send(json.dumps(end_message))
            print("已发送结束消息")
            
            # 等待最终响应
            response = await websocket.recv()
            print(f"收到最终响应: {response}")
            
    except Exception as e:
        print(f"WebSocket测试失败: {e}")

if __name__ == "__main__":
    print("开始WebSocket连接测试...")
    asyncio.run(test_websocket())
    print("测试完成") 
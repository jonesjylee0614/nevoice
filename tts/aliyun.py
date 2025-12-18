import uuid

# 模型名 qwen3-tts-flash
import requests
import os
import time

# 获取环境变量中的 DASHSCOPE_API_KEY
api_key = os.getenv('DASHSCOPE_API_KEY')

# 设置请求 URL
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'

# 设置请求头
headers = {
    "Authorization": f"Bearer {api_key}",
}

# 记录最后一次请求的时间
last_request_time = 0
# 设置请求间隔（秒）- 每秒最多3次请求
request_interval = 1.0 / 3

def rate_limit():
    """
    控制请求频率，确保请求之间有足够的时间间隔
    """
    global last_request_time
    now = time.time()
    
    # 计算距离上次请求需要等待的时间
    time_since_last_request = now - last_request_time
    if time_since_last_request < request_interval:
        # 如果距离上次请求时间不足，需要等待
        wait_time = request_interval - time_since_last_request
        time.sleep(wait_time)
        
    # 更新最后一次请求时间
    last_request_time = time.time()

def qwen_tts(text: str, out_path: str):
    # 控制请求频率
    rate_limit()
    
    # 设置请求体数据
    data = {
        "model": "qwen3-tts-flash-2025-11-27",
        "input": {
            "text": text,
            "voice": "Eric",  # 四川-程川 Eric 参考文档  https://help.aliyun.com/zh/model-studio/qwen-tts?spm=a2c4g.11186623.0.0.4855435aIsBNJk#bac280ddf5a1u
            "language_type": "Chinese"
        }
    }

    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        r"""
        {
          "output": {
            "audio": {
              "data": "",
              "expires_at": 1766026609,
              "id": "audio_1fe30542-1c05-4162-b61c-3bd02f344d4e",
              "url": "http://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/1d/80/20251217/f87e520c/34f65d98-6da4-40dc-90ac-c4bac8c28f57.wav?Expires=1766026609&OSSAccessKeyId=LTAI5tKPD3TMqf2Lna1fASuh&Signature=fU8C43BGtsOA0WLlezkayjHFjzk="
            },
            "finish_reason": "stop"
          },
          "usage": {
            "characters": 13
          },
          "request_id": "1fe30542-1c05-4162-b61c-3bd02f344d4e"
        }
        """

        # 获取响应数据
        response_data = res.json()
        # 获取音频数据
        audio_url = response_data['output']['audio']['url']
        # 确保输出路径的目录存在
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # 将音频数据写入文件
        with open(out_path, 'wb') as f:
            f.write(requests.get(audio_url).content)
            return True
    else:
        # 打印详细错误信息
        print(f'Request failed with status code: {res.status_code} res: {res.text} ')

        os.makedirs(os.path.dirname('./logs/error.txt'), exist_ok=True)

        # 把错误信息保存到文件
        with open('./logs/error.txt', 'a') as f:
            f.write(f'Request failed with status code: {res.status_code} res: {res.text}\n' )
        # 把错误的词保存到文件
        with open('./logs/word.txt', 'a') as f:
            f.write(f'{text}\n')
    # 发起 POST 请求
    return False

if __name__ == '__main__':
    unique_id = str(uuid.uuid4())
    output_wav_path = f'./v_qwen/{unique_id}.wav'

    res = qwen_tts("帅哥，过来耍撒", output_wav_path)

    # 输出响应结果
    print(f'生成结果：{res} {output_wav_path}')
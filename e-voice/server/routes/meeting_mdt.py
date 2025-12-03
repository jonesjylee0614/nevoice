"""MDT会议相关接口

提供声纹匹配、AI总结等功能
"""

from flask import Blueprint, request, jsonify
import traceback

bp = Blueprint('meeting_mdt', __name__, url_prefix='/meeting/mdt')


@bp.route('/match-speaker', methods=['POST'])
def match_speaker():
    """
    声纹匹配接口
    
    请求参数:
    - audio_data: base64编码的音频数据
    - participant_user_ids: 可选，参会人员ID列表，用于限制匹配范围
    
    返回:
    - recognized: bool, 是否匹配成功
    - speaker_id: int, 匹配到的用户ID
    - speaker_name: str, 用户名
    - recognition_note: str, 识别备注
    - recognition_score: float, 相似度分数
    """
    try:
        data = request.get_json()
        audio_data = data.get('audio_data')
        participant_user_ids = data.get('participant_user_ids', [])
        
        if not audio_data:
            return jsonify({
                'recognized': False,
                'speaker_name': '未知发言人',
                'recognition_note': '未提供音频数据'
            })
        
        # 调用声纹匹配
        result = match_speaker_from_audio(audio_data, participant_user_ids)
        return jsonify(result)
        
    except Exception as e:
        print(f"声纹匹配失败: {traceback.format_exc()}")
        return jsonify({
            'recognized': False,
            'speaker_name': '未知发言人',
            'recognition_note': f'声纹匹配失败: {str(e)}'
        }), 500


def match_speaker_from_audio(audio_base64: str, participant_user_ids: list = None):
    """
    从音频数据匹配发言人
    
    复用现有能力：
    1. pipeline.spk_v_pipeline.embeddings() - 提取声纹特征
    2. es.voice.search_voice_vector() - ES向量搜索
    """
    import base64
    import tempfile
    import os
    
    try:
        # 解码音频数据
        audio_bytes = base64.b64decode(audio_base64)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            result = match_speaker_from_wav_file(temp_path, participant_user_ids)
            return result
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"声纹匹配异常: {traceback.format_exc()}")
        return {
            'recognized': False,
            'speaker_name': '未知发言人',
            'recognition_note': f'匹配异常: {str(e)}'
        }


def match_speaker_from_wav_file(wav_path: str, participant_user_ids: list = None):
    """
    从WAV文件匹配发言人
    
    复用现有能力：
    1. pipeline.spk_v_pipeline.embeddings() - 提取声纹特征
    2. es.voice.search_voice_vector() - ES向量搜索
    """
    try:
        # 提取声纹特征（复用现有能力）
        from pipeline.spk_v_pipeline import embeddings
        embedding_list = embeddings([wav_path])
        
        if not embedding_list or len(embedding_list) == 0:
            return {
                'recognized': False,
                'speaker_name': '未知发言人',
                'recognition_note': '无法提取声纹特征'
            }
        
        embedding = embedding_list[0]
        
        # 向量搜索（复用现有能力）
        from es.voice import search_voice_vector
        results = search_voice_vector(embedding, top_k=3)
        
        if results:
            best = results[0]
            
            # 可选：过滤参会人员
            if participant_user_ids and best.get('userid') not in participant_user_ids:
                # 继续查找符合条件的
                for r in results:
                    if r.get('userid') in participant_user_ids:
                        best = r
                        break
                else:
                    return {
                        'recognized': False,
                        'speaker_name': '未知发言人',
                        'recognition_note': '声纹未匹配到参会人员'
                    }
            
            return {
                'recognized': True,
                'speaker_id': best.get('userid'),
                'speaker_name': best.get('username', '未知'),
                'recognition_note': f'声纹识别匹配成功',
                'recognition_score': best.get('_score', 0)
            }
        
        return {
            'recognized': False,
            'speaker_name': '未知发言人',
            'recognition_note': '声纹库中无匹配结果'
        }
            
    except ImportError as e:
        # 模块未加载，返回默认结果
        print(f"声纹模块未加载: {e}")
        return {
            'recognized': False,
            'speaker_name': '未知发言人',
            'recognition_note': '声纹服务暂不可用'
        }
    except Exception as e:
        print(f"声纹匹配异常: {traceback.format_exc()}")
        return {
            'recognized': False,
            'speaker_name': '未知发言人',
            'recognition_note': f'匹配异常: {str(e)}'
        }


def match_speaker_from_pcm(pcm_bytes: bytes, sample_rate: int = 16000, participant_user_ids: list = None):
    """
    从PCM字节数据匹配发言人（用于实时语音识别）
    
    Args:
        pcm_bytes: PCM音频数据（16bit, mono）
        sample_rate: 采样率
        participant_user_ids: 可选，参会人员ID列表
    
    Returns:
        声纹匹配结果
    """
    import tempfile
    import os
    import wave
    
    try:
        # 音频长度检查（至少1秒）
        min_samples = sample_rate  # 1秒的样本数
        actual_samples = len(pcm_bytes) // 2  # 16bit = 2bytes
        
        if actual_samples < min_samples:
            return {
                'recognized': False,
                'speaker_name': '未知发言人',
                'recognition_note': f'音频太短({actual_samples}/{min_samples}样本)，无法进行声纹匹配'
            }
        
        # 保存到临时WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name
        
        try:
            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_bytes)
            
            result = match_speaker_from_wav_file(temp_path, participant_user_ids)
            return result
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"PCM声纹匹配异常: {traceback.format_exc()}")
        return {
            'recognized': False,
            'speaker_name': '未知发言人',
            'recognition_note': f'匹配异常: {str(e)}'
        }


@bp.route('/generate-summary', methods=['POST'])
def generate_summary():
    """
    生成AI会议总结
    
    请求参数:
    - meeting_id: 会议ID
    - dialogs: 对话列表 [{speaker_name, speaker_role, speak_time, text}]
    - meeting_info: 会议信息 {title, description, host_name}
    
    返回:
    - summary: 生成的总结文本
    """
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        dialogs = data.get('dialogs', [])
        meeting_info = data.get('meeting_info', {})
        
        if not dialogs:
            return jsonify({
                'summary': '',
                'message': '暂无对话记录'
            })
        
        # 构建上下文
        context = build_meeting_context(dialogs, meeting_info)
        
        # 调用LLM生成总结
        summary = call_llm_for_summary(context)
        
        return jsonify({
            'summary': summary,
            'message': '总结生成成功'
        })
        
    except Exception as e:
        print(f"生成总结失败: {traceback.format_exc()}")
        return jsonify({
            'summary': '',
            'message': f'生成失败: {str(e)}'
        }), 500


def build_meeting_context(dialogs: list, meeting_info: dict) -> str:
    """构建会议上下文"""
    lines = []
    
    # 会议信息
    if meeting_info.get('title'):
        lines.append(f"会议主题：{meeting_info['title']}")
    if meeting_info.get('host_name'):
        lines.append(f"主持人：{meeting_info['host_name']}")
    if meeting_info.get('description'):
        lines.append(f"会议说明：{meeting_info['description']}")
    
    lines.append("")
    lines.append("会议记录：")
    
    # 对话内容
    for d in dialogs:
        speaker = d.get('speaker_name', '未知')
        role = d.get('speaker_role', '')
        time = d.get('speak_time', '')
        text = d.get('text', '')
        
        if role:
            lines.append(f"[{time}] {speaker}（{role}）: {text}")
        else:
            lines.append(f"[{time}] {speaker}: {text}")
    
    return "\n".join(lines)


def call_llm_for_summary(context: str) -> str:
    """
    调用阿里云百炼（DashScope）LLM生成总结
    
    使用 OpenAI 兼容的 API 格式调用
    """
    import requests
    
    # 获取配置
    from config.config import conf
    
    try:
        llm_conf = conf['llm']
        api_url = llm_conf.get('api_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        api_key = llm_conf.get('api_key', '')
        model = llm_conf.get('model', 'qwen-turbo')
    except Exception as e:
        print(f"读取LLM配置失败: {e}")
        return "配置错误：请在配置文件中设置 [llm] 配置项"
    
    if not api_key or api_key == 'your-api-key-here':
        return "未配置API Key：请在配置文件中设置 api_key"
    
    # 构建系统提示词
    system_prompt = """你是一位专业的医院会议纪要专家，擅长整理和总结多学科团队(MDT)会议内容。
请根据会议记录生成结构化的会议总结，要求：
1. 语言简洁专业
2. 突出关键决策和结论
3. 明确后续跟进事项
4. 如有提及，标注责任人分配"""
    
    # 构建用户提示词
    user_prompt = f"""请根据以下会议记录生成总结：

{context}

请按以下格式输出：
## 会议总结

### 一、主要议题
- [列出本次会议讨论的主要议题]

### 二、关键决策
- [列出会议达成的关键决策和结论]

### 三、后续跟进事项
- [列出需要跟进的事项]

### 四、责任人分配
- [如有明确提及，列出责任人分配情况]

### 五、其他备注
- [其他需要记录的内容]"""
    
    try:
        # 构建请求
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        # 发送请求
        response = requests.post(
            f'{api_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = response.text
            print(f"LLM API 请求失败: status={response.status_code}, error={error_msg}")
            return f"AI服务请求失败 (HTTP {response.status_code})"
        
        result = response.json()
        
        # 解析响应
        if 'choices' in result and len(result['choices']) > 0:
            summary = result['choices'][0]['message']['content']
            return summary.strip()
        else:
            print(f"LLM API 响应格式异常: {result}")
            return "AI服务响应格式异常"
            
    except requests.exceptions.Timeout:
        print("LLM API 请求超时")
        return "AI服务请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        print(f"LLM API 网络错误: {e}")
        return f"网络错误: {str(e)}"
    except Exception as e:
        print(f"LLM调用异常: {traceback.format_exc()}")
        return f"总结生成失败: {str(e)}"


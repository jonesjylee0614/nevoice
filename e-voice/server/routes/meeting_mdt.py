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
    调用LLM生成总结
    
    可以接入：
    - OpenAI API
    - 通义千问 API
    - 百川 API
    - 其他LLM服务
    """
    # TODO: 实际接入LLM API
    # 这里返回模拟结果，实际需要替换为真实的LLM调用
    
    prompt = f"""
你是一位医院会议纪要专家。请根据以下会议记录生成总结：

{context}

请按以下格式输出总结：
1. 会议主要议题
2. 关键决策和结论
3. 后续跟进事项
4. 责任人分配（如有）
"""
    
    # 模拟返回结果
    # 实际应该调用 LLM API
    try:
        # 尝试导入和调用LLM
        # from some_llm_sdk import generate
        # return generate(prompt)
        
        # 暂时返回模拟结果
        return f"""## 会议总结

### 1. 主要议题
- 根据会议记录分析主要讨论内容

### 2. 关键决策
- 待补充具体决策内容

### 3. 后续跟进
- 待补充跟进事项

### 4. 责任人分配
- 待补充责任人

---
*注：当前为模拟总结，请配置LLM服务后获取真实总结*
"""
    except Exception as e:
        return f"总结生成失败: {str(e)}"


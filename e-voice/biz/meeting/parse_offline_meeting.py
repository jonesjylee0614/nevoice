import os
import traceback
from collections import defaultdict
from datetime import datetime

from loguru import logger
from pydub import AudioSegment

from config.config import conf
from db.domain.meeting_offline_detail import insert_datas
from es.voice import multi_search_voice_vector
from pipeline.spk_v_pipeline import embeddings
from speech_recognition.spk import spk_pipeline

meeting_conf = conf["meeting"]


def process_audio_task(input_file, meetinginfo, opuser):
    """
    异步处理音频任务的函数
    这里实现你的实际业务逻辑，比如说话人识别、语音转文字等
    """
    try:
        logger.info(f"开始处理音频任务: {input_file}")

        # 会议时间时间戳
        meeting_timestamp = datetime.strptime(
            meetinginfo["meetingTime"], "%Y-%m-%d %H:%M:%S"
        ).timestamp()
        timestamp = int(datetime.now().timestamp() * 1000)
        # 1、加载音频文件
        audio = AudioSegment.from_file(input_file)

        # 2、说话人识别 + 语音转文字
        rec_result = spk_pipeline.generate(input_file)

        sentences = rec_result[0]["sentence_info"]

        folder = f"{meeting_conf['offline_wav_path']}/detail/{meetinginfo['meetingId']}/{timestamp}"
        if not os.path.exists(folder):
            os.makedirs(folder)

        # 先按spk分组
        spk_wavs = defaultdict(list)
        index_wavfile = {}
        i = 0
        for sentence in sentences:
            i = i + 1
            # 截取音频片段
            audio_segment = audio[sentence["start"] : sentence["end"]]
            # 导出截取的音频
            filename = (
                f"{meetinginfo['meetingId']}_{sentence['start']}_{sentence['end']}.wav"
            )
            wav_file = f"{folder}/{filename}"
            audio_segment.export(wav_file, format="wav")
            spk_wavs[sentence["spk"]].append(wav_file)
            index_wavfile[i] = f"{timestamp}/{filename}"

        # 限制每组数量 5
        spk_wavs2_limit = 5
        spk_wavs2 = {}
        for spk, items in spk_wavs.items():
            # 如果items长度超过max_per_group，则截取
            items = items[:spk_wavs2_limit] if len(items) > spk_wavs2_limit else items
            spk_wavs2[spk] = items
        # 查询向量库取用户id
        spk_ids = search_users_by_vector(spk_wavs2)

        i = 0
        details = []
        for sentence in sentences:
            i = i + 1
            # 保存语句片段到会议详情
            details.append(
                (
                    opuser["userid"],
                    opuser["username"],
                    opuser["userid"],
                    opuser["username"],
                    i,  # sort
                    spk_ids[sentence["spk"]],
                    datetime.fromtimestamp(
                        meeting_timestamp + sentence["start"] / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    # spk_time
                    sentence["text"],  # text
                    index_wavfile[i],  # wav_path
                    0,  # train_status
                    0,  # train_id
                    meetinginfo["meetingId"],
                )
            )
        # 批量插入
        insert_datas(details)

        logger.info(f"音频任务处理完成: {input_file}")
        return {"status": "completed", "result": "处理结果示例"}
    except Exception as e:
        logger.error(f"音频处理任务失败: {str(e)}")
        # 打印完整的堆栈跟踪信息
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


# 通过语料查询向量数据库内的用户ID
def search_users_by_vector(spk_wavs2):
    res = {}
    for k, wavs in spk_wavs2.items():
        embs = embeddings(wavs)
        users = multi_search_voice_vector(embs)
        res[k] = users[0]["userid"] if len(users) > 0 else 0

    return res

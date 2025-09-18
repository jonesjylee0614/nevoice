# 会议时间时间戳
from datetime import datetime

# 时间格式化
ori_time = '2023-05-05 09:05:05'
meeting_timestamp = datetime.strptime(ori_time, '%Y-%m-%d %H:%M:%S').timestamp()
# 时间戳+10380毫秒
spk_time = datetime.fromtimestamp(meeting_timestamp + 10380 / 1000).strftime('%Y-%m-%d %H:%M:%S')
print(ori_time)
print(spk_time)

# if else 快速赋值
b = False
res = 1 if b else 0
print(res)

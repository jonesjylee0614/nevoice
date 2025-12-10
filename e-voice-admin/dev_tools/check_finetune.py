#!/usr/bin/env python3
"""检查语料表"""
import pymysql

DB_CONFIG = {
    'host': '192.168.1.4',
    'port': 3306,
    'user': 'root',
    'password': 'Jz@szM982io',
    'database': 'evoice'
}

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 查询语料总数
    cursor.execute('SELECT COUNT(*) FROM finetune_voice_detail')
    count = cursor.fetchone()[0]
    print(f'语料总数: {count}')
    
    if count > 0:
        cursor.execute('SELECT id, meeting_id, meeting_detail_id, LEFT(text, 50) FROM finetune_voice_detail ORDER BY id DESC LIMIT 5')
        print('最新记录:')
        for r in cursor.fetchall():
            print(f'  ID:{r[0]}, 会议ID:{r[1]}, 对话ID:{r[2]}, 文本:{r[3]}')
    
    # 查询会议38的对话
    print('\n会议38的对话记录:')
    cursor.execute('SELECT id, text, audio_path FROM mdt_meeting_dialog WHERE meeting_id = 38')
    for r in cursor.fetchall():
        print(f'  ID:{r[0]}, 文本:{r[1][:50] if r[1] else None}..., 音频:{r[2]}')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()


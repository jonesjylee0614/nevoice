#!/usr/bin/env python3
"""批量导入热词到数据库 - 使用批量插入提高性能"""
import pymysql
import time
from datetime import datetime

DB_CONFIG = {
    'host': '192.168.1.4',
    'port': 3306,
    'user': 'root',
    'password': 'Jz@szM982io',
    'database': 'evoice'
}

HOTWORD_FILE = r'D:\WorkSpace\code\2025\evoice\nevoice\e-voice\zh_correct\custom_word_freq.txt'
BATCH_SIZE = 1000  # 每批插入的数量

def main():
    print(f'开始导入热词...')
    print(f'文件路径: {HOTWORD_FILE}')
    
    # 读取文件
    print('读取文件中...')
    with open(HOTWORD_FILE, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    
    total_words = len(words)
    print(f'共读取 {total_words} 个热词')
    
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 获取已存在的热词
    print('检查已存在的热词...')
    cursor.execute('SELECT word FROM voice_hotword')
    existing_words = set(row[0] for row in cursor.fetchall())
    print(f'数据库中已有 {len(existing_words)} 个热词')
    
    # 过滤出需要插入的新热词
    new_words = [w for w in words if w not in existing_words]
    print(f'需要新增 {len(new_words)} 个热词')
    
    if not new_words:
        print('没有需要导入的新热词')
        cursor.close()
        conn.close()
        return
    
    # 批量插入
    print(f'开始批量插入（每批 {BATCH_SIZE} 条）...')
    start_time = time.time()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    insert_count = 0
    for i in range(0, len(new_words), BATCH_SIZE):
        batch = new_words[i:i + BATCH_SIZE]
        
        # 构建批量插入SQL
        values_list = []
        for word in batch:
            mogrified = cursor.mogrify("(%s, 1, %s, %s)", (word, now, now))
            # Python 3 pymysql mogrify 可能返回 bytes 或 str
            if isinstance(mogrified, bytes):
                mogrified = mogrified.decode('utf-8')
            values_list.append(mogrified)
        values = ', '.join(values_list)
        
        sql = f"""INSERT INTO voice_hotword (word, status, create_time, update_time) 
                  VALUES {values}
                  ON DUPLICATE KEY UPDATE word=word"""
        
        try:
            cursor.execute(sql)
            conn.commit()
            insert_count += len(batch)
            
            # 显示进度
            progress = insert_count / len(new_words) * 100
            elapsed = time.time() - start_time
            rate = insert_count / elapsed if elapsed > 0 else 0
            print(f'\r进度: {insert_count}/{len(new_words)} ({progress:.1f}%) - {rate:.0f} 条/秒', end='', flush=True)
            
        except Exception as e:
            print(f'\n批次 {i//BATCH_SIZE + 1} 插入失败: {e}')
            conn.rollback()
    
    elapsed = time.time() - start_time
    print(f'\n\n✅ 导入完成！')
    print(f'  总计插入: {insert_count} 条')
    print(f'  耗时: {elapsed:.1f} 秒')
    print(f'  平均速度: {insert_count/elapsed:.0f} 条/秒')
    
    # 验证
    cursor.execute('SELECT COUNT(*) FROM voice_hotword')
    final_count = cursor.fetchone()[0]
    print(f'  数据库总热词: {final_count} 条')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()


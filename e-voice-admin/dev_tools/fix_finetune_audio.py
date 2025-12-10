#!/usr/bin/env python3
"""修复 finetune/audio 路由的 component 配置"""
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

    # 1. 查询当前 finetune 相关菜单配置
    print('当前 finetune 相关菜单配置：')
    cursor.execute("SELECT id, title, routePath, component FROM business_auth_rule WHERE routePath LIKE '%finetune%' OR component LIKE '%finetune%'")
    for row in cursor.fetchall():
        print(f'  ID:{row[0]}, 标题:{row[1]}, 路由:{row[2]}, 组件:{row[3]}')

    # 2. 修复：将 /finetune/audio 的 component 从 /finetune/audio/index 改为 /finetune/detail/index
    print('\n修复 finetune/audio 组件路径...')
    cursor.execute("""
        UPDATE business_auth_rule 
        SET component = '/finetune/detail/index' 
        WHERE routePath = '/finetune/audio' OR routePath = 'audio'
    """)
    affected = cursor.rowcount
    conn.commit()
    print(f'  已更新 {affected} 条记录')

    # 3. 验证修复结果
    print('\n修复后的配置：')
    cursor.execute("SELECT id, title, routePath, component FROM business_auth_rule WHERE routePath LIKE '%finetune%' OR component LIKE '%finetune%'")
    for row in cursor.fetchall():
        print(f'  ID:{row[0]}, 标题:{row[1]}, 路由:{row[2]}, 组件:{row[3]}')

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""添加热词管理菜单到数据库"""
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

    # 1. 查询语音能力菜单的ID作为父菜单
    print('查询语音能力父菜单...')
    cursor.execute("SELECT id, title, routePath FROM business_auth_rule WHERE routePath = '/voice' OR title = '语音能力'")
    parent = cursor.fetchone()
    
    if not parent:
        print('❌ 未找到语音能力父菜单，请先创建')
        cursor.close()
        conn.close()
        return
    
    parent_id = parent[0]
    print(f'  找到父菜单: ID={parent_id}, 标题={parent[1]}, 路由={parent[2]}')

    # 2. 检查热词管理菜单是否已存在
    cursor.execute("SELECT id FROM business_auth_rule WHERE routePath = 'hotword' AND pid = %s", (parent_id,))
    existing = cursor.fetchone()
    
    if existing:
        print(f'⚠️ 热词管理菜单已存在 (ID={existing[0]})，跳过创建')
    else:
        # 3. 获取当前最大weigh值
        cursor.execute("SELECT MAX(weigh) FROM business_auth_rule WHERE pid = %s", (parent_id,))
        max_weigh = cursor.fetchone()[0] or 0
        new_weigh = max_weigh + 1

        # 4. 插入热词管理菜单
        print('插入热词管理菜单...')
        cursor.execute("""
            INSERT INTO business_auth_rule (pid, title, routePath, component, icon, weigh, type, status, create_time, update_time)
            VALUES (%s, '热词管理', 'hotword', '/voice/hotword/index', 'icon-file', %s, 1, 1, NOW(), NOW())
        """, (parent_id, new_weigh))
        menu_id = cursor.lastrowid
        conn.commit()
        print(f'✅ 热词管理菜单已创建 (ID={menu_id})')

        # 5. 添加子权限（操作按钮）
        print('添加操作权限...')
        permissions = [
            ('热词列表', 'vh:base', 2),
            ('热词编辑', 'vh:edit', 2),
            ('热词删除', 'vh:del', 2),
            ('状态更新', 'vh:upStatus', 2),
            ('批量导入', 'vh:import', 2),
            ('导出', 'vh:export', 2),
            ('同步文件', 'vh:sync', 2),
        ]
        
        for title, perms, perm_type in permissions:
            cursor.execute("""
                INSERT INTO business_auth_rule (pid, title, perms, type, status, create_time, update_time)
                VALUES (%s, %s, %s, %s, 1, NOW(), NOW())
            """, (menu_id, title, perms, perm_type))
        
        conn.commit()
        print(f'✅ 已添加 {len(permissions)} 个操作权限')

    # 6. 显示最终结果
    print('\n当前语音能力下的菜单:')
    cursor.execute("""
        SELECT id, title, routePath, component, perms, type, status 
        FROM business_auth_rule 
        WHERE pid = %s OR id = %s
        ORDER BY weigh DESC
    """, (parent_id, parent_id))
    
    for row in cursor.fetchall():
        type_str = {0: '目录', 1: '菜单', 2: '按钮'}.get(row[5], '未知')
        status_str = '启用' if row[6] == 1 else '禁用'
        print(f'  ID:{row[0]}, 标题:{row[1]}, 路由:{row[2]}, 组件:{row[3]}, 权限:{row[4]}, 类型:{type_str}, 状态:{status_str}')

    cursor.close()
    conn.close()
    print('\n✅ 完成！')

if __name__ == '__main__':
    main()


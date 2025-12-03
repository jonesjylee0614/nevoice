#!/usr/bin/env python3
"""检查菜单和权限配置"""
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

    # 1. 检查MDT会议菜单
    print('MDT会议菜单配置：')
    cursor.execute("SELECT id, title, locale, routePath FROM business_auth_rule WHERE routePath LIKE '%mdt%'")
    for row in cursor.fetchall():
        print(f'  ID:{row[0]}, 标题:{row[1]}, Locale:{row[2]}, 路由:{row[3]}')

    # 2. 检查gofly用户的角色权限
    print('\ngofly用户角色权限：')
    cursor.execute("""
        SELECT r.id, r.name, r.rules 
        FROM business_account a 
        JOIN business_auth_role_access ra ON a.id = ra.uid 
        JOIN business_auth_role r ON ra.role_id = r.id 
        WHERE a.username = 'gofly'
    """)
    for row in cursor.fetchall():
        print(f'  角色ID:{row[0]}, 角色名:{row[1]}')
        rules = row[2] or ''
        rule_ids = [r for r in rules.split(',') if r]
        print(f'  拥有权限数量: {len(rule_ids)}')
        print(f'  权限ID列表: {rules}')

    # 3. 查看所有顶级菜单
    print('\n所有顶级菜单（pid=0）：')
    cursor.execute("SELECT id, title, routePath FROM business_auth_rule WHERE pid = 0 ORDER BY orderNo")
    top_menus = cursor.fetchall()
    for row in top_menus:
        print(f'  ID:{row[0]}, 标题:{row[1]}, 路由:{row[2]}')

    # 4. 修复：将MDT菜单的title改为中文
    print('\n修复MDT菜单标题...')
    cursor.execute("UPDATE business_auth_rule SET title = 'MDT会议' WHERE routePath = '/meeting/mdt'")
    cursor.execute("UPDATE business_auth_rule SET title = '会议详情' WHERE routePath = '/meeting/mdt/detail'")
    conn.commit()
    print('  已更新菜单标题')

    # 5. 修复：将所有顶级菜单的ID添加到gofly角色的rules中
    print('\n修复gofly角色权限...')
    # 获取所有菜单ID
    cursor.execute("SELECT id FROM business_auth_rule")
    all_menu_ids = [str(row[0]) for row in cursor.fetchall()]
    all_rules = ','.join(sorted(all_menu_ids, key=lambda x: int(x)))
    
    # 更新超级管理组的权限为所有菜单
    cursor.execute("UPDATE business_auth_role SET rules = %s WHERE id = 1", (all_rules,))
    conn.commit()
    print(f'  已更新超级管理组权限，共 {len(all_menu_ids)} 个菜单')

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()


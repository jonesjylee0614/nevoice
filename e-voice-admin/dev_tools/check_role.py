#!/usr/bin/env python3
"""检查用户角色权限"""
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

    # 获取gofly用户的角色
    cursor.execute("""
        SELECT a.id, a.username, r.id as role_id, r.name, r.rules 
        FROM business_account a 
        JOIN business_auth_role_access ra ON a.id = ra.uid 
        JOIN business_auth_role r ON ra.role_id = r.id 
        WHERE a.username = 'gofly'
    """)
    
    print('gofly用户角色：')
    for row in cursor.fetchall():
        print(f'  用户ID:{row[0]}, 用户名:{row[1]}, 角色ID:{row[2]}, 角色名:{row[3]}')
        rules = row[4] or ''
        rule_ids = [r for r in rules.split(',') if r]
        print(f'    权限ID数量: {len(rule_ids)}')
        print(f'    包含首页(8): {"8" in rule_ids}')
        
        if '8' not in rule_ids:
            print('    添加首页权限...')
            rule_ids.append('8')
            new_rules = ','.join(sorted(set(rule_ids), key=lambda x: int(x) if x.isdigit() else 0))
            cursor.execute('UPDATE business_auth_role SET rules = %s WHERE id = %s', (new_rules, row[2]))
            conn.commit()
            print('    ✅ 已添加')
        else:
            print('    ✅ 首页权限已存在')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()


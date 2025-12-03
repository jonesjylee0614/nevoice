#!/usr/bin/env python3
"""重置用户密码脚本 / 检查首页菜单"""
import pymysql
import hashlib
import sys

DB_CONFIG = {
    'host': '192.168.1.4',
    'port': 3306,
    'user': 'root',
    'password': 'Jz@szM982io',
    'database': 'evoice'
}

def check_home_menu():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 检查首页菜单
    cursor.execute("SELECT id, title, routePath, routeName, pid FROM business_auth_rule WHERE routePath LIKE '%home%' OR routeName = 'home' OR title LIKE '%首页%'")
    print("首页相关菜单：")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  ID:{row[0]}, 标题:{row[1]}, 路由:{row[2]}, 名称:{row[3]}, 父级:{row[4]}")
    
    if not rows:
        print("  ❌ 没有找到首页菜单，需要添加！")
        # 添加首页菜单
        from datetime import datetime
        now = datetime.now()
        cursor.execute("""
            INSERT INTO business_auth_rule (
                uid, title, locale, orderNo, type, pid, icon, 
                routePath, routeName, component, redirect, permission,
                status, isExt, keepalive, requiresAuth, 
                hideInMenu, hideChildrenInMenu, activeMenu, noAffix,
                create_time, update_time
            ) VALUES (
                1, '首页', 'menu.home', 1, 1, 0, 'icon-home',
                '/home', 'home', '/dashboard/workplace/index', '', '',
                0, 0, 0, 1, 0, 0, 1, 1, %s, %s
            )
        """, (now, now))
        conn.commit()
        print("  ✅ 已添加首页菜单")
        
        # 获取新增菜单ID
        home_menu_id = cursor.lastrowid
        print(f"  首页菜单ID: {home_menu_id}")
        
        # 添加到所有角色
        cursor.execute("SELECT id, rules FROM business_auth_role")
        for role_id, rules in cursor.fetchall():
            existing_ids = set(rules.split(',')) if rules else set()
            existing_ids.add(str(home_menu_id))
            new_rules = ','.join(sorted(existing_ids, key=lambda x: int(x) if x.isdigit() else 0))
            cursor.execute("UPDATE business_auth_role SET rules = %s WHERE id = %s", (new_rules, role_id))
        conn.commit()
        print("  ✅ 已更新所有角色权限")
    
    cursor.close()
    conn.close()

def reset_password():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 查询现有账号
    cursor.execute("SELECT id, username, nickname, salt FROM business_account WHERE status = 0 LIMIT 10")
    print("现有账号：")
    accounts = cursor.fetchall()
    for row in accounts:
        print(f"  ID:{row[0]}, 用户名:{row[1]}, 昵称:{row[2]}, Salt:{row[3]}")
    
    if not accounts:
        print("没有找到可用账号")
        return
    
    # 使用第一个账号的salt
    account = accounts[0]
    account_id = account[0]
    username = account[1]
    salt = account[3] or ''
    
    # 计算密码：MD5(password + salt)
    new_password = 'admin123'
    password_hash = hashlib.md5((new_password + salt).encode()).hexdigest()
    
    print(f"\n重置 {username} 的密码...")
    print(f"  Salt: {salt}")
    print(f"  Password Hash: {password_hash}")
    
    cursor.execute(
        "UPDATE business_account SET password = %s WHERE id = %s",
        (password_hash, account_id)
    )
    conn.commit()
    
    print(f"\n✅ 密码已重置！")
    print(f"  用户名: {username}")
    print(f"  密码: {new_password}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'home':
        check_home_menu()
    else:
        reset_password()


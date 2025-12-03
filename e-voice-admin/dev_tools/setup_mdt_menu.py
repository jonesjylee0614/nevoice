#!/usr/bin/env python3
"""
MDT会议菜单配置脚本
用于在evoice数据库中创建MDT会议菜单并配置角色权限
"""
import pymysql
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': '192.168.1.4',
    'port': 3306,
    'user': 'root',
    'password': 'Jz@szM982io',
    'database': 'evoice',
    'charset': 'utf8mb4'
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def check_menu_exists(cursor, route_path):
    """检查菜单是否已存在"""
    cursor.execute(
        "SELECT id FROM business_auth_rule WHERE routePath = %s",
        (route_path,)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def insert_menu(cursor, menu_data):
    """插入菜单记录"""
    sql = """
    INSERT INTO business_auth_rule (
        uid, title, locale, orderNo, type, pid, icon, 
        routePath, routeName, component, redirect, permission,
        status, isExt, keepalive, requiresAuth, 
        hideInMenu, hideChildrenInMenu, activeMenu, noAffix,
        create_time, update_time
    ) VALUES (
        %(uid)s, %(title)s, %(locale)s, %(orderNo)s, %(type)s, %(pid)s, %(icon)s,
        %(routePath)s, %(routeName)s, %(component)s, %(redirect)s, %(permission)s,
        %(status)s, %(isExt)s, %(keepalive)s, %(requiresAuth)s,
        %(hideInMenu)s, %(hideChildrenInMenu)s, %(activeMenu)s, %(noAffix)s,
        %(create_time)s, %(update_time)s
    )
    """
    cursor.execute(sql, menu_data)
    return cursor.lastrowid

def update_role_rules(cursor, role_id, new_menu_ids):
    """更新角色权限"""
    # 获取当前rules
    cursor.execute("SELECT rules FROM business_auth_role WHERE id = %s", (role_id,))
    result = cursor.fetchone()
    if result:
        current_rules = result[0] or ''
        existing_ids = set(current_rules.split(',')) if current_rules else set()
        existing_ids.update(str(mid) for mid in new_menu_ids)
        new_rules = ','.join(sorted(existing_ids, key=lambda x: int(x) if x.isdigit() else 0))
        cursor.execute(
            "UPDATE business_auth_role SET rules = %s WHERE id = %s",
            (new_rules, role_id)
        )
        return True
    return False

def main():
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    new_menu_ids = []
    
    try:
        # 1. 检查/创建"会议管理"目录
        meeting_parent_id = check_menu_exists(cursor, '/meeting')
        if not meeting_parent_id:
            print("创建'会议管理'目录菜单...")
            meeting_parent_id = insert_menu(cursor, {
                'uid': 1, 'title': '会议管理', 'locale': 'menu.meeting',
                'orderNo': 30, 'type': 0, 'pid': 0, 'icon': 'icon-calendar',
                'routePath': '/meeting', 'routeName': 'meeting', 'component': 'LAYOUT',
                'redirect': '', 'permission': '', 'status': 0, 'isExt': 0,
                'keepalive': 0, 'requiresAuth': 1, 'hideInMenu': 0,
                'hideChildrenInMenu': 0, 'activeMenu': 1, 'noAffix': 0,
                'create_time': now, 'update_time': now
            })
            new_menu_ids.append(meeting_parent_id)
            print(f"  创建成功，ID: {meeting_parent_id}")
        else:
            print(f"'会议管理'目录已存在，ID: {meeting_parent_id}")
        
        # 2. 检查/创建"MDT会议"菜单
        mdt_menu_id = check_menu_exists(cursor, '/meeting/mdt')
        if not mdt_menu_id:
            print("创建'MDT会议'菜单...")
            mdt_menu_id = insert_menu(cursor, {
                'uid': 1, 'title': 'MDT会议', 'locale': 'menu.meeting.mdt',
                'orderNo': 1, 'type': 1, 'pid': meeting_parent_id, 'icon': '',
                'routePath': '/meeting/mdt', 'routeName': 'meetingMdt',
                'component': '/meeting/mdt/index', 'redirect': '',
                'permission': 'meeting:mdt:list', 'status': 0, 'isExt': 0,
                'keepalive': 1, 'requiresAuth': 1, 'hideInMenu': 0,
                'hideChildrenInMenu': 0, 'activeMenu': 1, 'noAffix': 0,
                'create_time': now, 'update_time': now
            })
            new_menu_ids.append(mdt_menu_id)
            print(f"  创建成功，ID: {mdt_menu_id}")
        else:
            print(f"'MDT会议'菜单已存在，ID: {mdt_menu_id}")
        
        # 3. 检查/创建"会议详情"菜单（隐藏）
        detail_menu_id = check_menu_exists(cursor, '/meeting/mdt/detail')
        if not detail_menu_id:
            print("创建'会议详情'菜单...")
            detail_menu_id = insert_menu(cursor, {
                'uid': 1, 'title': '会议详情', 'locale': 'menu.meeting.mdt.detail',
                'orderNo': 2, 'type': 1, 'pid': meeting_parent_id, 'icon': '',
                'routePath': '/meeting/mdt/detail', 'routeName': 'meetingMdtDetail',
                'component': '/meeting/mdt/Detail', 'redirect': '',
                'permission': 'meeting:mdt:detail', 'status': 0, 'isExt': 0,
                'keepalive': 0, 'requiresAuth': 1, 'hideInMenu': 1,
                'hideChildrenInMenu': 0, 'activeMenu': 1, 'noAffix': 0,
                'create_time': now, 'update_time': now
            })
            new_menu_ids.append(detail_menu_id)
            print(f"  创建成功，ID: {detail_menu_id}")
        else:
            print(f"'会议详情'菜单已存在，ID: {detail_menu_id}")
        
        # 4. 创建按钮权限
        button_permissions = [
            ('新建会议', 'meeting:mdt:add', 1),
            ('编辑会议', 'meeting:mdt:edit', 2),
            ('删除会议', 'meeting:mdt:delete', 3),
        ]
        
        for title, permission, order in button_permissions:
            cursor.execute(
                "SELECT id FROM business_auth_rule WHERE permission = %s",
                (permission,)
            )
            if not cursor.fetchone():
                print(f"创建'{title}'按钮权限...")
                btn_id = insert_menu(cursor, {
                    'uid': 1, 'title': title, 'locale': '',
                    'orderNo': order, 'type': 2, 'pid': mdt_menu_id, 'icon': '',
                    'routePath': '', 'routeName': '', 'component': '',
                    'redirect': '', 'permission': permission, 'status': 0,
                    'isExt': 0, 'keepalive': 0, 'requiresAuth': 1,
                    'hideInMenu': 0, 'hideChildrenInMenu': 0,
                    'activeMenu': 1, 'noAffix': 0,
                    'create_time': now, 'update_time': now
                })
                new_menu_ids.append(btn_id)
                print(f"  创建成功，ID: {btn_id}")
            else:
                print(f"'{title}'按钮权限已存在")
        
        # 5. 更新角色权限
        if new_menu_ids:
            print("\n更新角色权限...")
            # 获取所有角色
            cursor.execute("SELECT id, name FROM business_auth_role")
            roles = cursor.fetchall()
            for role_id, role_name in roles:
                if update_role_rules(cursor, role_id, new_menu_ids):
                    print(f"  已更新角色: {role_name} (ID: {role_id})")
        
        conn.commit()
        print("\n✅ 菜单配置完成！")
        print(f"新增菜单ID列表: {new_menu_ids}")
        
        # 显示所有会议相关菜单
        print("\n当前会议相关菜单:")
        cursor.execute("""
            SELECT id, title, routePath, type, pid 
            FROM business_auth_rule 
            WHERE routePath LIKE '%meeting%' OR title LIKE '%会议%'
            ORDER BY pid, orderNo
        """)
        for row in cursor.fetchall():
            menu_type = {0: '目录', 1: '菜单', 2: '按钮'}.get(row[3], '未知')
            print(f"  ID:{row[0]}, 标题:{row[1]}, 路由:{row[2]}, 类型:{menu_type}, 父ID:{row[4]}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 错误: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()


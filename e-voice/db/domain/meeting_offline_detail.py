from db.db import get_dbcursor, check_db


# 插入数据
def insert_data(creator_id, creator_name, sort, spk_user_id, spk_time, text, wav_path, meeting_id):
    cur = get_dbcursor()
    conn = check_db()

    sql = f"""
insert into meeting_offline_detail (create_time, update_time, creator_id, creator_name, updater_id, updater_name,
                                    sort, spk_user_id, spk_time, text, wav_path, train_status, train_id, meeting_id)
values (now(),now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
    val = (creator_id, creator_name, creator_id, creator_name, sort, spk_user_id, spk_time, text, wav_path, 0, 0,
           meeting_id)
    cur.execute(sql, val)
    conn.commit()
    print(f"插入记录ID: {cur.lastrowid}")


# 批量插入
def insert_datas(data_list):
    cur = get_dbcursor()
    conn = check_db()
    sql = f"""
insert into meeting_offline_detail (create_time, update_time, creator_id, creator_name, updater_id, updater_name,
                                    sort, spk_user_id, spk_time, text, wav_path, train_status, train_id, meeting_id)
values (now(),now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
    cur.executemany(sql, data_list)
    conn.commit()
    print(f"插入了 {cur.rowcount} 条记录")


if __name__ == '__main__':
    insert_data(1, "张三", 1, 1, "2021-01-01 00:00:00", "这是一段测试数据", "test.wav", 1)
    insert_datas([
        (1, 'admin', 1, 'admin', 1, 1, "2021-01-01 00:00:00", "1", "test.wav", 0, 0, 1),
        (1, 'admin', 1, 'admin', 1, 1, "2021-01-01 00:00:00", "1", "test.wav", 0, 0, 1),
    ])

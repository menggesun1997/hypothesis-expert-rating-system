#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

# 配置数据库路径
DB_PATH = "hypothesis_data.db"

def add_email_column():
    """为comments表添加email列"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查email列是否已存在
        cursor.execute("PRAGMA table_info(comments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email' not in columns:
            # 添加email列
            cursor.execute("ALTER TABLE comments ADD COLUMN email TEXT")
            print("✅ 成功添加email列到comments表")
        else:
            print("ℹ️  email列已存在")
        
        # 显示表结构
        cursor.execute("PRAGMA table_info(comments)")
        print("\n📋 comments表结构:")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
        conn.commit()
        conn.close()
        print("\n✅ 数据库更新完成")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库操作错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == '__main__':
    add_email_column()

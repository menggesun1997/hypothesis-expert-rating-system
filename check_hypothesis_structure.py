#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

# 配置数据库路径
DB_PATH = "hypothesis_data.db"

def check_hypothesis_structure():
    """检查hypothesis表的结构"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("📋 hypothesis表结构:")
        cursor.execute("PRAGMA table_info(hypothesis)")
        columns = cursor.fetchall()
        
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        print(f"\n📊 数据统计:")
        cursor.execute("SELECT COUNT(*) FROM hypothesis")
        total_count = cursor.fetchone()[0]
        print(f"   总假设数量: {total_count}")
        
        cursor.execute("SELECT topic, sub_topic, COUNT(*) FROM hypothesis GROUP BY topic, sub_topic ORDER BY topic, sub_topic")
        topic_subtopic_counts = cursor.fetchall()
        print(f"\n📈 按topic和subtopic分组统计:")
        for topic, subtopic, count in topic_subtopic_counts:
            print(f"   topic{topic} subtopic{subtopic}: {count} 个假设")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ 数据库操作错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == '__main__':
    check_hypothesis_structure()

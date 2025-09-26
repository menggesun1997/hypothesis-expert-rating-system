#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

# 配置数据库路径
DB_PATH = "hypothesis_data.db"

def fix_predefined_comparisons():
    """修复predefined_comparisons表中的hypothesis_content_en字段"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("🔧 开始修复predefined_comparisons表的hypothesis_content_en字段...")
        
        # 获取所有需要修复的记录
        cursor.execute("""
            SELECT id, original_hypothesis_id, topic_name, hypothesis_rank
            FROM predefined_comparisons
        """)
        
        records = cursor.fetchall()
        print(f"📊 找到 {len(records)} 条记录需要修复")
        
        # 为每条记录更新hypothesis_content_en字段
        for record_id, original_hypothesis_id, topic_name, hypothesis_rank in records:
            # 从原始hypothesis表中获取正确的hypothesis_content
            cursor.execute("""
                SELECT hypothesis_content FROM hypothesis WHERE id = ?
            """, (original_hypothesis_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                # 更新hypothesis_content_en字段
                cursor.execute("""
                    UPDATE predefined_comparisons 
                    SET hypothesis_content_en = ? 
                    WHERE id = ?
                """, (result[0], record_id))
                print(f"   ✅ {topic_name} rank{hypothesis_rank}: 已更新hypothesis_content_en")
            else:
                print(f"   ⚠️  {topic_name} rank{hypothesis_rank}: 未找到原始内容")
        
        # 提交更改
        conn.commit()
        
        # 验证修复结果
        print(f"\n📋 验证修复结果（前5条）:")
        cursor.execute("""
            SELECT topic_name, hypothesis_rank, 
                   substr(hypothesis_content_en, 1, 50) as content_preview
            FROM predefined_comparisons 
            ORDER BY topic_name, hypothesis_rank 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"   {row[0]} rank{row[1]}: {row[2]}...")
        
        conn.close()
        print(f"\n✅ predefined_comparisons表修复完成！")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库操作错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == '__main__':
    fix_predefined_comparisons()

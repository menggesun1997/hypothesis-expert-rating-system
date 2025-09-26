#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import random

# 配置数据库路径
DB_PATH = "hypothesis_data.db"

# 定义需要抽取的topic和subtopic组合
TOPIC_SUBTOPIC_PAIRS = [
    (1, 1),   # topic1中的subtop1
    (2, 0),   # topic2中的subtop0
    (3, 2),   # topic3中的subtop2
    (4, 0),   # topic4中的subtop0
    (5, 3),   # topic5中的subtop3
    (6, 2),   # topic6中的subtop2
    (7, 0),   # topic7中的subtop0
    (8, 2),   # topic8中的subtop2
    (9, 2),   # topic9中的subtop2
    (10, 0),  # topic10中的subtop0
    (10, 4),  # topic10中的subtop4
    (11, 3),  # topic11中的subtop3
]

def rebuild_predefined_comparisons():
    """重新构建predefined_comparisons表格"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("🔄 开始重新构建predefined_comparisons表格...")
        
        # 1. 删除现有的predefined_comparisons表
        print("🗑️  删除现有的predefined_comparisons表...")
        cursor.execute("DROP TABLE IF EXISTS predefined_comparisons")
        
        # 2. 重新创建predefined_comparisons表
        print("🏗️  创建新的predefined_comparisons表...")
        cursor.execute("""
            CREATE TABLE predefined_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT NOT NULL,
                hypothesis_rank INTEGER NOT NULL,
                -- 原始hypothesis表的所有字段
                original_hypothesis_id INTEGER,
                model_source TEXT,
                topic INTEGER,
                sub_topic INTEGER,
                strategy TEXT,
                hypothesis_content_en TEXT,
                hypothesis_content_zh TEXT,
                novelty_score REAL,
                significance_score REAL,
                soundness_score REAL,
                feasibility_score REAL,
                overall_winner_score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. 为每个topic-subtopic组合抽取8个假设
        for topic, subtopic in TOPIC_SUBTOPIC_PAIRS:
            topic_name = f"topic{topic}"
            print(f"\n📊 处理 {topic_name} 的 subtopic{subtopic}...")
            
            # 从hypothesis表中查询该topic和subtopic的所有假设
            cursor.execute("""
                SELECT id, model_source, topic, sub_topic, strategy, hypothesis_id, hypothesis_content,
                       feedback_results, novelty_score, significance_score, soundness_score,
                       feasibility_score, overall_winner_score
                FROM hypothesis 
                WHERE topic = ? AND sub_topic = ?
            """, (topic, subtopic))
            
            hypotheses = cursor.fetchall()
            print(f"   找到 {len(hypotheses)} 个假设")
            
            if len(hypotheses) == 0:
                print(f"   ⚠️  警告：{topic_name} subtopic{subtopic} 没有找到假设")
                continue
            
            # 随机选择8个假设（如果总数少于8个，则选择全部）
            num_to_select = min(8, len(hypotheses))
            selected_hypotheses = random.sample(hypotheses, num_to_select)
            print(f"   随机选择了 {num_to_select} 个假设")
            
            # 将选中的假设插入到predefined_comparisons表
            for rank, hypothesis in enumerate(selected_hypotheses, 1):
                cursor.execute("""
                    INSERT INTO predefined_comparisons (
                        topic_name, hypothesis_rank, original_hypothesis_id, model_source,
                        topic, sub_topic, strategy, hypothesis_content_en, hypothesis_content_zh,
                        novelty_score, significance_score, soundness_score, feasibility_score,
                        overall_winner_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic_name,
                    rank,
                    hypothesis[0],  # id
                    hypothesis[1],  # model_source
                    hypothesis[2],  # topic
                    hypothesis[3],  # sub_topic
                    hypothesis[4],  # strategy
                    hypothesis[5],  # hypothesis_id (作为content_en)
                    '',  # hypothesis_content_zh (空字符串)
                    hypothesis[8],  # novelty_score
                    hypothesis[9],  # significance_score
                    hypothesis[10], # soundness_score
                    hypothesis[11], # feasibility_score
                    hypothesis[12]  # overall_winner_score
                ))
            
            print(f"   ✅ {topic_name} 完成，插入了 {num_to_select} 个假设")
        
        # 4. 提交更改
        conn.commit()
        
        # 5. 显示统计信息
        print(f"\n📈 统计信息:")
        cursor.execute("SELECT COUNT(*) FROM predefined_comparisons")
        total_count = cursor.fetchone()[0]
        print(f"   总假设数量: {total_count}")
        
        cursor.execute("SELECT topic_name, COUNT(*) FROM predefined_comparisons GROUP BY topic_name ORDER BY topic_name")
        topic_counts = cursor.fetchall()
        for topic_name, count in topic_counts:
            print(f"   {topic_name}: {count} 个假设")
        
        conn.close()
        print(f"\n✅ predefined_comparisons表格重建完成！")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库操作错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == '__main__':
    rebuild_predefined_comparisons()

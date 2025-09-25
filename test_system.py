#!/usr/bin/env python3
"""
专家评分系统测试脚本
"""

import sys
import os
sys.path.append('.')

from app import init_hypothesis_pools, create_rating_tables, get_comparison_pair
import sqlite3

def test_database_connection():
    """测试数据库连接"""
    print("1. 测试数据库连接...")
    try:
        conn = sqlite3.connect('../hypothesis_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hypothesis")
        count = cursor.fetchone()[0]
        print(f"   ✓ 数据库连接成功，共有 {count} 条假设")
        conn.close()
        return True
    except Exception as e:
        print(f"   ✗ 数据库连接失败: {e}")
        return False

def test_hypothesis_pools():
    """测试假设池初始化"""
    print("2. 测试假设池初始化...")
    try:
        init_hypothesis_pools()
        from app import TOPIC_HYPOTHESIS_POOLS
        
        if len(TOPIC_HYPOTHESIS_POOLS) == 0:
            print("   ✗ 假设池为空")
            return False
            
        print(f"   ✓ 成功初始化 {len(TOPIC_HYPOTHESIS_POOLS)} 个主题的假设池")
        
        for topic, hypotheses in TOPIC_HYPOTHESIS_POOLS.items():
            if len(hypotheses) != 10:
                print(f"   ✗ {topic} 假设数量不正确: {len(hypotheses)}")
                return False
            print(f"     - {topic}: {len(hypotheses)} 条假设")
        
        return True
    except Exception as e:
        print(f"   ✗ 假设池初始化失败: {e}")
        return False

def test_database_tables():
    """测试数据库表创建"""
    print("3. 测试数据库表创建...")
    try:
        create_rating_tables()
        
        conn = sqlite3.connect('../hypothesis_data.db')
        cursor = conn.cursor()
        
        # 检查ratings表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ratings'")
        if not cursor.fetchone():
            print("   ✗ ratings表未创建")
            return False
        
        # 检查comments表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
        if not cursor.fetchone():
            print("   ✗ comments表未创建")
            return False
        
        print("   ✓ 数据库表创建成功")
        conn.close()
        return True
    except Exception as e:
        print(f"   ✗ 数据库表创建失败: {e}")
        return False

def test_comparison_logic():
    """测试比较逻辑"""
    print("4. 测试比较逻辑...")
    try:
        from app import TOPIC_HYPOTHESIS_POOLS
        
        topic = 'topic1'
        if topic not in TOPIC_HYPOTHESIS_POOLS:
            print(f"   ✗ 主题 {topic} 不存在")
            return False
        
        # 测试多次比较是否返回不同结果
        results = set()
        for i in range(1, 6):
            comparison = get_comparison_pair(topic, i)
            pair_key = f"{comparison['hypothesis_A']['id']}-{comparison['hypothesis_B']['id']}"
            results.add(pair_key)
        
        if len(results) < 3:  # 至少应该有3种不同的配对
            print("   ✗ 比较逻辑可能有问题，配对结果过于相似")
            return False
        
        print("   ✓ 比较逻辑正常")
        return True
    except Exception as e:
        print(f"   ✗ 比较逻辑测试失败: {e}")
        return False

def test_hypothesis_content():
    """测试假设内容格式"""
    print("5. 测试假设内容格式...")
    try:
        from app import TOPIC_HYPOTHESIS_POOLS
        
        topic = 'topic1'
        hypothesis = TOPIC_HYPOTHESIS_POOLS[topic][0]
        content = hypothesis['content']
        
        required_fields = ['title', 'Problem_Statement', 'Motivation', 'Proposed_Method']
        for field in required_fields:
            if field not in content:
                print(f"   ✗ 假设内容缺少字段: {field}")
                return False
        
        print("   ✓ 假设内容格式正确")
        return True
    except Exception as e:
        print(f"   ✗ 假设内容测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("专家评分系统功能测试")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_hypothesis_pools,
        test_database_tables,
        test_comparison_logic,
        test_hypothesis_content
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        print("\n启动系统:")
        print("cd expert_rating_system")
        print("./start_app.sh")
    else:
        print("❌ 部分测试失败，请检查系统配置。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

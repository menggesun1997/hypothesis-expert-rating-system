#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from google import genai
import time
import sys
import os
from pydantic import BaseModel

# 配置数据库路径
DB_PATH = "/Users/sunmengge/Dropbox/hypothesis_expert_rating_system/hypothesis_data.db"
KEYS_PATH = "/Users/sunmengge/Dropbox/idea generation/by_evolution/smg/keys.json"

# 定义翻译结果的数据模型
class TranslationResult(BaseModel):
    title: str
    Problem_Statement: str
    Motivation: str
    Proposed_Method: str
    Step_by_Step_Experiment_Plan: str
    Test_Case_Examples: str
    Fallback_Plan: str

def load_gemini_key():
    """从keys.json文件中读取Gemini API key"""
    try:
        with open(KEYS_PATH, 'r', encoding='utf-8') as f:
            keys_data = json.load(f)
            return keys_data.get('gemini_key')
    except Exception as e:
        print(f"错误：读取API key时发生异常：{e}")
        return None

def translate_hypothesis_content(content_dict, api_key):
    """使用Gemini API翻译整个假设内容"""
    try:
        # 初始化Gemini客户端
        client = genai.Client(api_key=api_key)
        
        # 构建翻译提示
        prompt = f"""请将以下英文科学研究假设翻译成中文，保持学术性和专业性，确保翻译准确且符合中文表达习惯。

        英文内容：
        title: {content_dict.get('title', '')}
        Problem_Statement: {content_dict.get('Problem_Statement', '')}
        Motivation: {content_dict.get('Motivation', '')}
        Proposed_Method: {content_dict.get('Proposed_Method', '')}
        Step_by_Step_Experiment_Plan: {content_dict.get('Step_by_Step_Experiment_Plan', '')}
        Test_Case_Examples: {content_dict.get('Test_Case_Examples', '')}
        Fallback_Plan: {content_dict.get('Fallback_Plan', '')}

        翻译要求：
        1. 保持原文的科学严谨性
        2. 使用准确的学术术语
        3. 确保句子结构清晰
        4. 保持原文的逻辑关系
        5. 返回JSON格式，包含所有翻译后的字段

        请返回JSON格式的翻译结果，格式如下：
        {{
            "title": "翻译后的标题",
            "Problem_Statement": "翻译后的问题陈述",
            "Motivation": "翻译后的动机",
            "Proposed_Method": "翻译后的方法",
            "Step_by_Step_Experiment_Plan": "翻译后的实验计划",
            "Test_Case_Examples": "翻译后的测试案例",
            "Fallback_Plan": "翻译后的备用计划"
        }}"""
        
        # 调用API进行翻译
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if response.text:
            try:
                # 使用正则表达式提取JSON内容
                import re
                
                # 查找JSON对象，从第一个{到最后一个}
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if not json_match:
                    print("警告：未找到JSON格式的内容")
                    return None
                
                text = json_match.group(0)
                
                # 简单的文本清理
                # 移除所有控制字符
                text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
                
                # 尝试解析JSON响应
                translated_data = json.loads(text)
                return translated_data
                
            except json.JSONDecodeError as e:
                print(f"警告：无法解析API返回的JSON格式: {e}")
                print(f"原始内容：{response.text[:300]}...")
                
                # 尝试手动构建JSON对象
                try:
                    # 使用正则表达式提取各个字段
                    title_match = re.search(r'"title":\s*"([^"]*)"', response.text)
                    problem_match = re.search(r'"Problem_Statement":\s*"([^"]*)"', response.text)
                    motivation_match = re.search(r'"Motivation":\s*"([^"]*)"', response.text)
                    method_match = re.search(r'"Proposed_Method":\s*"([^"]*)"', response.text)
                    plan_match = re.search(r'"Step_by_Step_Experiment_Plan":\s*"([^"]*)"', response.text)
                    test_match = re.search(r'"Test_Case_Examples":\s*"([^"]*)"', response.text)
                    fallback_match = re.search(r'"Fallback_Plan":\s*"([^"]*)"', response.text)
                    
                    # 构建翻译结果
                    translated_data = {
                        "title": title_match.group(1) if title_match else "",
                        "Problem_Statement": problem_match.group(1) if problem_match else "",
                        "Motivation": motivation_match.group(1) if motivation_match else "",
                        "Proposed_Method": method_match.group(1) if method_match else "",
                        "Step_by_Step_Experiment_Plan": plan_match.group(1) if plan_match else "",
                        "Test_Case_Examples": test_match.group(1) if test_match else "",
                        "Fallback_Plan": fallback_match.group(1) if fallback_match else ""
                    }
                    
                    print("通过正则表达式提取成功解析JSON")
                    return translated_data
                    
                except Exception as e2:
                    print(f"正则表达式提取也失败: {e2}")
                    return None
        else:
            print("警告：API返回空响应")
            return None
            
    except Exception as e:
        print(f"翻译错误：{e}")
        return None

def translate_hypotheses():
    """翻译所有假设内容"""
    # 加载API key
    api_key = load_gemini_key()
    if not api_key:
        print("无法加载Gemini API key，退出程序")
        return False
    
    print(f"成功加载Gemini API key")
    
    # 连接数据库
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有需要翻译的假设（只翻译hypothesis_content_zh为空的记录）
        cursor.execute("""
            SELECT id, topic_name, hypothesis_rank, hypothesis_content_en
            FROM predefined_comparisons 
            WHERE hypothesis_content_zh IS NULL OR hypothesis_content_zh = ''
            ORDER BY topic_name, hypothesis_rank
        """)
        
        hypotheses = cursor.fetchall()
        
        if not hypotheses:
            print("没有需要翻译的假设")
            return True
        
        print(f"找到 {len(hypotheses)} 个需要翻译的假设")
        
        # 翻译每个假设
        success_count = 0
        for i, (hyp_id, topic_name, rank, content_en) in enumerate(hypotheses, 1):
            print(f"\n进度：{i}/{len(hypotheses)} - 翻译 {topic_name} 第 {rank} 个假设 (ID: {hyp_id})")
            
            if not content_en:
                print(f"跳过：假设内容为空")
                continue
            
            try:
                # 解析英文内容
                content_dict = json.loads(content_en)
                
                # 检查是否有可翻译的内容
                if not content_dict or not any(content_dict.values()):
                    print(f"跳过：没有找到可翻译的文本内容")
                    continue
                
                print(f"  翻译整个假设内容...")
                
                # 翻译整个假设内容
                translated_content = translate_hypothesis_content(content_dict, api_key)
                
                if not translated_content:
                    print(f"  ✗ 翻译失败")
                    continue
                
                print(f"  ✓ 翻译完成")
                
                # 将翻译后的内容保存到数据库
                translated_json = json.dumps(translated_content, ensure_ascii=False, indent=2)
                
                cursor.execute("""
                    UPDATE predefined_comparisons 
                    SET hypothesis_content_zh = ?
                    WHERE id = ?
                """, (translated_json, hyp_id))
                
                conn.commit()
                success_count += 1
                print(f"  ✓ 假设 {hyp_id} 翻译完成并保存")
                
                # 添加延迟避免API限制
                time.sleep(2)
                
            except json.JSONDecodeError as e:
                print(f"  ✗ JSON解析错误：{e}")
                continue
            except Exception as e:
                print(f"  ✗ 翻译假设 {hyp_id} 时发生错误：{e}")
                continue
        
        print(f"\n翻译完成！成功翻译 {success_count}/{len(hypotheses)} 个假设")
        
        # 显示翻译统计
        cursor.execute("""
            SELECT topic_name, COUNT(*) as total, 
                   SUM(CASE WHEN hypothesis_content_zh IS NOT NULL AND hypothesis_content_zh != '' THEN 1 ELSE 0 END) as translated
            FROM predefined_comparisons 
            GROUP BY topic_name
            ORDER BY topic_name
        """)
        
        stats = cursor.fetchall()
        print("\n翻译统计：")
        for topic_name, total, translated in stats:
            print(f"  {topic_name}: {translated}/{total} 已翻译")
        
        return True
        
    except sqlite3.Error as e:
        print(f"数据库错误：{e}")
        return False
    except Exception as e:
        print(f"程序错误：{e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """主函数"""
    print("开始翻译假设内容...")
    print(f"数据库路径：{DB_PATH}")
    print(f"API Key路径：{KEYS_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件不存在 {DB_PATH}")
        return
    
    if not os.path.exists(KEYS_PATH):
        print(f"错误：API Key文件不存在 {KEYS_PATH}")
        return
    
    success = translate_hypotheses()
    
    if success:
        print("\n✓ 翻译任务完成！")
    else:
        print("\n✗ 翻译任务失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()

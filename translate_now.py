#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from google import genai
import time
import os

# 配置数据库路径
DB_PATH = "hypothesis_data.db"
KEYS_PATH = "/Users/sunmengge/Dropbox/idea generation/by_evolution/smg/keys.json"

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
        
        # 构建简化的翻译提示
        title = content_dict.get('title', '')
        problem = content_dict.get('Problem_Statement', '')
        motivation = content_dict.get('Motivation', '')
        method = content_dict.get('Proposed_Method', '')
        plan = content_dict.get('Step_by_Step_Experiment_Plan', '')
        examples = content_dict.get('Test_Case_Examples', '')
        fallback = content_dict.get('Fallback_Plan', '')
        
        prompt = f"""请将以下英文科学研究假设翻译成中文，保持学术性和专业性。

英文内容：
标题: {title}
问题陈述: {problem}
动机: {motivation}
方法: {method}
实验计划: {plan}
测试案例: {examples}
备用计划: {fallback}

请返回JSON格式的翻译结果，格式如下：
{{
    "title": "翻译后的标题",
    "Problem_Statement": "翻译后的问题陈述",
    "Motivation": "翻译后的动机",
    "Proposed_Method": "翻译后的方法",
    "Step_by_Step_Experiment_Plan": "翻译后的实验计划",
    "Test_Case_Examples": "翻译后的测试案例",
    "Fallback_Plan": "翻译后的备用计划"
}}

注意：请确保返回的是有效的JSON格式，避免使用特殊字符和转义字符。"""
        
        # 调用API进行翻译
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if response.text:
            # 清理响应文本
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # 查找JSON对象的开始和结束
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                
                try:
                    # 尝试解析JSON响应
                    translated_data = json.loads(json_text)
                    return translated_data
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"JSON文本: {json_text[:200]}...")
                    return None
        else:
            print("API返回空响应")
            return None
            
    except Exception as e:
        print(f"翻译错误：{e}")
        return None

def translate_all():
    """翻译所有假设内容"""
    # 加载API key
    api_key = load_gemini_key()
    if not api_key:
        print("无法加载Gemini API key")
        return False
    
    print("成功加载Gemini API key")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有需要翻译的记录
    cursor.execute("""
        SELECT id, topic_name, hypothesis_rank, hypothesis_content_en
        FROM predefined_comparisons 
        WHERE hypothesis_content_zh IS NULL OR hypothesis_content_zh = ''
        ORDER BY topic_name, hypothesis_rank
    """)
    
    missing_records = cursor.fetchall()
    print(f"找到 {len(missing_records)} 条需要翻译的记录")
    
    if len(missing_records) == 0:
        print("所有记录都已翻译完成！")
        conn.close()
        return True
    
    success_count = 0
    for i, (hyp_id, topic_name, rank, content_en) in enumerate(missing_records, 1):
        print(f"\n进度：{i}/{len(missing_records)} - 翻译 {topic_name} rank{rank} (ID: {hyp_id})")
        
        try:
            # 解析英文内容
            content_dict = json.loads(content_en)
            print(f"  标题: {content_dict.get('title', '无标题')[:50]}...")
            
            # 翻译内容
            translated_content = translate_hypothesis_content(content_dict, api_key)
            
            if translated_content:
                # 保存翻译结果
                translated_json = json.dumps(translated_content, ensure_ascii=False, indent=2)
                
                cursor.execute("""
                    UPDATE predefined_comparisons 
                    SET hypothesis_content_zh = ?
                    WHERE id = ?
                """, (translated_json, hyp_id))
                
                conn.commit()
                success_count += 1
                print(f"  ✓ 翻译完成并保存")
            else:
                print(f"  ✗ 翻译失败")
            
            # 添加延迟避免API限制
            time.sleep(3)
            
        except Exception as e:
            print(f"  ✗ 处理错误: {e}")
            continue
    
    print(f"\n翻译完成！成功翻译 {success_count}/{len(missing_records)} 个假设")
    
    # 检查最终状态
    cursor.execute("""
        SELECT COUNT(*) FROM predefined_comparisons 
        WHERE hypothesis_content_zh IS NOT NULL AND hypothesis_content_zh != ''
    """)
    total_translated = cursor.fetchone()[0]
    print(f"总翻译进度: {total_translated}/96")
    
    conn.close()
    return True

if __name__ == "__main__":
    print("开始翻译假设内容...")
    print(f"数据库路径：{DB_PATH}")
    print(f"API Key路径：{KEYS_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件不存在 {DB_PATH}")
        exit(1)
    
    if not os.path.exists(KEYS_PATH):
        print(f"错误：API Key文件不存在 {KEYS_PATH}")
        exit(1)
    
    translate_all()

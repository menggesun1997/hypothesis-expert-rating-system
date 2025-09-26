import sqlite3
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 请在生产环境中更改此密钥

# 数据库路径
DB_PATH = 'hypothesis_data.db'

# 每个主题的固定假设池（10条假设）
TOPIC_HYPOTHESIS_POOLS = {}

# 主题描述
TOPIC_DESCRIPTIONS = {
    'topic1': "How can we incorporate existing knowledge bases effectively into LLMs",
    'topic2': "Do these models enhance scientific understanding (of language, cognition, or deep learning technology)? In what ways?",
    'topic3': "How reliably do the current generation of LLMs perform on NLP tasks and applications",
    'topic4': "How is linguistic diversity covered by these LLMs?",
    'topic5': "What are the different systemic failures of such LLMs and recovery strategies and methodologies?",
    'topic6': "How can we evaluate the performance of Large Language Models (LLMs) intrinsically (with no downstream application involved)?",
    'topic7': "How replicable is the performance of Large Language Models (LLMs) in both NLP research and real-life applications?",
    'topic8': "How do Large Language Models (LLMs) capture world knowledge?",
    'topic9': "What are the opportunities Large Language Models (LLMs) offer to NLP research?",
    'topic10': "How can Large Language Models (LLMs) influence how NLP research is done in the future?",
    'topic11': "What are the different ethical and FATE-related considerations regarding the design and use of Large Language Models (LLMs)?"
}

def init_hypothesis_pools():
    """初始化每个主题的固定假设池"""
    global TOPIC_HYPOTHESIS_POOLS
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有主题
    cursor.execute("SELECT DISTINCT topic FROM hypothesis")
    topics = [row[0] for row in cursor.fetchall()]
    
    for topic in topics:
        topic_name = f'topic{topic}'
        
        # 检查是否已经有预定义的假设
        cursor.execute("""
            SELECT COUNT(*) FROM predefined_comparisons 
            WHERE topic_name = ?
        """, (topic_name,))
        
        if cursor.fetchone()[0] == 0:
            # 如果没有预定义假设，则抽取8个
            print(f"Creating predefined hypotheses for {topic_name}...")
            
            # 为每个主题随机选择8条假设，包含所有字段
            cursor.execute("""
                SELECT id, model_source, topic, sub_topic, strategy, hypothesis_id, 
                       hypothesis_content, feedback_results, novelty_score, significance_score,
                       soundness_score, feasibility_score, overall_winner_score
                FROM hypothesis 
                WHERE topic = ? 
                ORDER BY RANDOM() 
                LIMIT 8
            """, (topic,))
            
            hypotheses = []
            for row in cursor.fetchall():
                try:
                    content = json.loads(row[6]) if row[6] else {}
                    hypotheses.append({
                        'id': row[0],
                        'model_source': row[1],
                        'topic': row[2],
                        'sub_topic': row[3],
                        'strategy': row[4],
                        'hypothesis_id': row[5],
                        'content': content,
                        'feedback_results': row[7],
                        'novelty_score': row[8],
                        'significance_score': row[9],
                        'soundness_score': row[10],
                        'feasibility_score': row[11],
                        'overall_winner_score': row[12]
                    })
                except json.JSONDecodeError:
                    continue
            
            # 将8个假设存储到数据库
            if len(hypotheses) >= 8:
                # 使用固定的随机种子确保每次生成相同的假设
                random.seed(42)  # 固定种子
                
                for i, hypothesis in enumerate(hypotheses, 1):
                    cursor.execute("""
                        INSERT INTO predefined_comparisons 
                        (topic_name, hypothesis_rank, original_hypothesis_id, model_source, topic, sub_topic,
                         strategy, hypothesis_id, hypothesis_content_en, feedback_results,
                         novelty_score, significance_score, soundness_score, feasibility_score, overall_winner_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (topic_name, i, hypothesis['id'], hypothesis['model_source'], hypothesis['topic'],
                          hypothesis['sub_topic'], hypothesis['strategy'], hypothesis['hypothesis_id'],
                          json.dumps(hypothesis['content']), hypothesis['feedback_results'],
                          hypothesis['novelty_score'], hypothesis['significance_score'], hypothesis['soundness_score'],
                          hypothesis['feasibility_score'], hypothesis['overall_winner_score']))
                
                print(f"Created 8 predefined hypotheses for {topic_name}")
            
            conn.commit()
        
        # 加载假设池到内存（用于获取假设内容）
        cursor.execute("""
            SELECT id, hypothesis_content 
            FROM hypothesis 
            WHERE topic = ?
        """, (topic,))
        
        hypotheses = []
        for row in cursor.fetchall():
            try:
                content = json.loads(row[1])
                hypotheses.append({
                    'id': row[0],
                    'content': content
                })
            except json.JSONDecodeError:
                continue
        
        TOPIC_HYPOTHESIS_POOLS[topic_name] = hypotheses
    
    conn.close()

def create_rating_tables():
    """创建评分相关的数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建评分表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            expert_id TEXT,
            topic_name TEXT NOT NULL,
            comparison_number INTEGER NOT NULL,
            hypothesis_A_id INTEGER NOT NULL,
            hypothesis_B_id INTEGER NOT NULL,
            novelty_score INTEGER NOT NULL,
            soundness_score INTEGER NOT NULL,
            feasibility_score INTEGER NOT NULL,
            significance_score INTEGER NOT NULL,
            overall_score INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建评论表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            comment_text TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建预定义假设表（存储每个topic的8个假设，包含所有相关字段）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predefined_comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            hypothesis_rank INTEGER NOT NULL,
            -- 原始hypothesis表的所有字段
            original_hypothesis_id INTEGER,
            model_source TEXT,
            topic INTEGER,
            sub_topic INTEGER,
            strategy TEXT,
            hypothesis_id INTEGER,
            hypothesis_content_en TEXT,
            hypothesis_content_zh TEXT,
            feedback_results TEXT,
            novelty_score REAL,
            significance_score REAL,
            soundness_score REAL,
            feasibility_score REAL,
            overall_winner_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(topic_name, hypothesis_rank)
        )
    """)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """主页 - 显示可用的主题"""
    # 从预定义比较对表中获取有比较对的主题
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT topic_name 
        FROM predefined_comparisons 
        ORDER BY topic_name
    """)
    
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('index.html', topics=topics, topic_descriptions=TOPIC_DESCRIPTIONS)

@app.route('/rate/<topic>')
def rate_topic(topic):
    """主题评估页面"""
    # 检查主题是否有预定义的比较对
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM predefined_comparisons 
        WHERE topic_name = ?
    """, (topic,))
    
    if cursor.fetchone()[0] == 0:
        conn.close()
        return "主题不存在或没有预定义的比较对", 404
    
    conn.close()
    
    # 初始化会话
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['topic'] = topic
        session['current_comparison'] = 1
        session['completed_comparisons'] = []
    
    # 重置会话如果主题不匹配
    if session.get('topic') != topic:
        session['session_id'] = str(uuid.uuid4())
        session['topic'] = topic
        session['current_comparison'] = 1
        session['completed_comparisons'] = []
    
    # 检查比较编号是否在有效范围内
    if session['current_comparison'] > 8:
        # 如果超过8个比较，重定向到感谢页面
        return redirect(url_for('thank_you'))
    
    # 获取语言偏好（默认为英文）
    language = request.args.get('lang', 'english')
    
    # 获取当前比较的假设对
    comparison_data = get_comparison_pair(topic, session['current_comparison'], language)
    
    if not comparison_data:
        return f"无法找到 {topic} 的比较对 {session['current_comparison']}。请检查数据库中的预定义比较对。", 404
    
    return render_template('rate_topic.html', 
                         topic=topic,
                         topic_descriptions=TOPIC_DESCRIPTIONS,
                         comparison_data=comparison_data,
                         current_comparison=session['current_comparison'],
                         total_comparisons=8)

def get_comparison_pair(topic, comparison_number, language='english'):
    """从预定义的8个假设中随机选择2个进行比较"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 根据语言选择要获取的列
    content_column = "hypothesis_content_zh" if language == 'chinese' else "hypothesis_content_en"
    
    # 获取该主题的所有预定义假设
    cursor.execute(f"""
        SELECT original_hypothesis_id, hypothesis_rank, {content_column}, model_source, strategy,
               novelty_score, significance_score, soundness_score, feasibility_score, overall_winner_score
        FROM predefined_comparisons 
        WHERE topic_name = ?
        ORDER BY hypothesis_rank
    """, (topic,))
    
    hypotheses = cursor.fetchall()
    if len(hypotheses) < 2:
        print(f"主题 {topic} 的预定义假设数量不足")
        conn.close()
        return None
    
    
    # 随机选择2个不同的假设
    selected_indices = random.sample(range(len(hypotheses)), 2)
    hyp_a_data = hypotheses[selected_indices[0]]
    hyp_b_data = hypotheses[selected_indices[1]]
    
    print(f"从 {topic} 的 {len(hypotheses)} 个假设中选择了: A={hyp_a_data[0]}, B={hyp_b_data[0]}")
    
    # 解析JSON内容
    try:
        hypothesis_A_content = json.loads(hyp_a_data[2]) if hyp_a_data[2] else {}
        hypothesis_B_content = json.loads(hyp_b_data[2]) if hyp_b_data[2] else {}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        hypothesis_A_content = {}
        hypothesis_B_content = {}
    
    conn.close()
    
    print(f"假设内容: A={hypothesis_A_content is not None}, B={hypothesis_B_content is not None}")
    
    return {
        'hypothesis_A': {
            'id': hyp_a_data[0],
            'content': hypothesis_A_content,
            'model_source': hyp_a_data[3],
            'strategy': hyp_a_data[4],
            'novelty_score': hyp_a_data[5],
            'significance_score': hyp_a_data[6],
            'soundness_score': hyp_a_data[7],
            'feasibility_score': hyp_a_data[8],
            'overall_winner_score': hyp_a_data[9]
        },
        'hypothesis_B': {
            'id': hyp_b_data[0],
            'content': hypothesis_B_content,
            'model_source': hyp_b_data[3],
            'strategy': hyp_b_data[4],
            'novelty_score': hyp_b_data[5],
            'significance_score': hyp_b_data[6],
            'soundness_score': hyp_b_data[7],
            'feasibility_score': hyp_b_data[8],
            'overall_winner_score': hyp_b_data[9]
        }
    }

@app.route('/api/submit-rating', methods=['POST'])
def submit_rating():
    """提交评分数据"""
    data = request.json
    
    # 保存评分到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ratings (
            session_id, topic_name, comparison_number,
            hypothesis_A_id, hypothesis_B_id,
            novelty_score, soundness_score, feasibility_score,
            significance_score, overall_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session['session_id'],
        session['topic'],
        data['comparison_number'],
        data['hypothesis_A_id'],
        data['hypothesis_B_id'],
        data['novelty_score'],
        data['soundness_score'],
        data['feasibility_score'],
        data['significance_score'],
        data['overall_score']
    ))
    
    conn.commit()
    conn.close()
    
    # 更新会话状态
    session['current_comparison'] += 1
    session['completed_comparisons'].append(data['comparison_number'])
    
    # 检查是否完成了所有比较
    if session['current_comparison'] > 8:
        session['current_comparison'] = 8  # 防止超出范围
    
    return jsonify({'success': True})

@app.route('/thank-you')
def thank_you():
    """感谢页面"""
    if 'session_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('thank_you.html', 
                         session_id=session['session_id'],
                         topic=session.get('topic'))

@app.route('/api/submit-comment', methods=['POST'])
def submit_comment():
    """提交评论"""
    data = request.json
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO comments (session_id, topic_name, comment_text)
        VALUES (?, ?, ?)
    """, (
        session['session_id'],
        session['topic'],
        data.get('comment', '')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/ratings')
def admin_ratings():
    """管理员页面 - 查看评分结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有评分数据
    cursor.execute("""
        SELECT r.*, h1.hypothesis_content as content_A, h2.hypothesis_content as content_B
        FROM ratings r
        LEFT JOIN hypothesis h1 ON r.hypothesis_A_id = h1.id
        LEFT JOIN hypothesis h2 ON r.hypothesis_B_id = h2.id
        ORDER BY r.timestamp DESC
    """)
    
    ratings = cursor.fetchall()
    conn.close()
    
    return render_template('admin_ratings.html', ratings=ratings)

@app.route('/reset-session')
def reset_session():
    """重置当前会话状态"""
    session.clear()
    return "会话已重置！<br><a href='/'>返回主页</a>"

@app.errorhandler(500)
def internal_error(error):
    """处理500内部服务器错误"""
    import traceback
    error_info = traceback.format_exc()
    print(f"❌ 500错误: {error}")
    print(f"📋 错误详情: {error_info}")
    return f"""
    <h1>服务器内部错误</h1>
    <p>抱歉，服务器遇到了一个内部错误。</p>
    <p><strong>错误信息:</strong> {error}</p>
    <p><a href="/">返回主页</a></p>
    <details>
        <summary>技术详情</summary>
        <pre>{error_info}</pre>
    </details>
    """, 500

@app.errorhandler(404)
def not_found_error(error):
    """处理404错误"""
    return """
    <h1>页面未找到</h1>
    <p>抱歉，您访问的页面不存在。</p>
    <p><a href="/">返回主页</a></p>
    """, 404

if __name__ == '__main__':
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(DB_PATH):
            print(f"❌ 数据库文件不存在: {DB_PATH}")
            print("📁 当前工作目录:", os.getcwd())
            print("📁 目录内容:", os.listdir('.'))
            exit(1)
        
        print(f"✅ 数据库文件存在: {DB_PATH}")
        
        # 初始化假设池和数据库表
        print("🔄 初始化假设池...")
        init_hypothesis_pools()
        print("✅ 假设池初始化完成")
        
        print("🔄 创建评分表...")
        create_rating_tables()
        print("✅ 评分表创建完成")
        
        # Railway环境变量支持
        port = int(os.environ.get('PORT', 5001))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print("🚀 启动专家评分系统...")
        print("📊 支持多主题假设比较和评分")
        print(f"🌐 访问地址: http://{host}:{port}")
        print(f"🔧 调试模式: {debug}")
        
        app.run(debug=debug, host=host, port=port)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

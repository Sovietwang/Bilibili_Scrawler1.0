import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
import requests
import re
import os
import pymysql
from datetime import datetime
import jieba  # 用于中文分词
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import time
from snownlp import SnowNLP  # 用于情感分析
#from fake_useragent import UserAgent #反爬欺骗

# 初始化jieba分词
jieba.initialize()

app = Flask(__name__)
CORS(app)

#user_agents池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
]

# MySQL 连接配置
MYSQL_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),  # MySQL 主机名
    "user": os.getenv("DB_USER", "bili_user"),  # MySQL 用户名
    "password": os.getenv("DB_PASSWORD", "Li114514"),  # MySQL 密码
    "database": os.getenv("DB_NAME", "bili"),  # MySQL 数据库名
    "cursorclass": pymysql.cursors.DictCursor  # 返回字典格式的结果
}

def get_db_connection():
    """获取 MySQL 数据库连接"""
    return pymysql.connect(**MYSQL_CONFIG)

def init_db():
    """初始化数据库"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 创建 users 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    avatar VARCHAR(200) DEFAULT '/default_avatar.png',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建 videos 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bvid VARCHAR(20) UNIQUE NOT NULL,
                    title TEXT,
                    up_name TEXT,
                    cover_url TEXT,
                    view_count INT,
                    like_count INT,
                    coin_count INT,
                    favorite_count INT,
                    description TEXT,
                    duration TEXT,
                    pubdate TEXT,
                    user_id INT DEFAULT NULL
                    
                )
            """)
            # 创建 query_history 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bvid VARCHAR(20) NOT NULL,
                    query_time DATETIME NOT NULL,
                    user_id INT DEFAULT NULL,
                    FOREIGN KEY (bvid) REFERENCES videos (bvid)
                )
            """)

        conn.commit()
        
# 用户
def register_user(username, password):
    """注册新用户"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            """, (username, password))
        conn.commit()

def login_user(username, password):
    """用户登录"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, avatar FROM users
                WHERE username = %s AND password = %s
            """, (username, password))
            return cursor.fetchone()

def save_video_info(bvid, video_info, user_id=None):
    """保存视频信息到数据库"""
    video_dict = {item["key"]: item["value"] for item in video_info}

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 修改为正确的SQL语句，包含user_id字段
            sql = """
                INSERT INTO videos (
                    bvid, title, up_name, cover_url, view_count, like_count,
                    coin_count, favorite_count, description, duration, pubdate, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    up_name = VALUES(up_name),
                    cover_url = VALUES(cover_url),
                    view_count = VALUES(view_count),
                    like_count = VALUES(like_count),
                    coin_count = VALUES(coin_count),
                    favorite_count = VALUES(favorite_count),
                    description = VALUES(description),
                    duration = VALUES(duration),
                    pubdate = VALUES(pubdate),
                    user_id = VALUES(user_id)
            """
            params = (
                bvid,
                video_dict.get("标题", ""),
                video_dict.get("UP主", ""),
                video_dict.get("封面", ""),
                video_dict.get("播放量", 0),
                video_dict.get("点赞数", 0),
                video_dict.get("投币数", 0),
                video_dict.get("收藏数", 0),
                video_dict.get("视频简介", ""),
                video_dict.get("视频时长", ""),
                video_dict.get("发布时间", ""),
                user_id  # 添加user_id参数
            )
            cursor.execute(sql, params)
        conn.commit()

def save_query_history(bvid, user_id=None):
    """保存查询历史记录"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO query_history (bvid, query_time,user_id)
                VALUES (%s, %s, %s)
            """, (bvid, datetime.now().isoformat(), user_id))
        conn.commit()

def get_query_history(user_id=None):
    """获取查询历史记录"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if user_id is not None:
                cursor.execute("""
                    SELECT bvid, query_time FROM query_history
                    WHERE user_id = %s
                    ORDER BY query_time DESC
                    LIMIT 100
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT bvid, query_time FROM query_history
                    WHERE user_id IS NULL
                    ORDER BY query_time DESC
                    LIMIT 100
                """)
            history = cursor.fetchall()

            return [{"bvid": item["bvid"], "query_time": item["query_time"]} for item in history]

def extract_bvid(url_or_bvid):
    bvid_pattern = re.compile(r"(BV[0-9A-Za-z]{10})")
    match = bvid_pattern.search(url_or_bvid)
    return match.group(0) if match else None

def seconds_to_minutes(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}分{seconds:02d}秒"  # 使用 :02d 确保秒数总是两位数

def get_video_info(bvid):
    """获取视频信息"""
    BASE_URL = "https://api.bilibili.com/x/web-interface/view"
    info_url = f"{BASE_URL}?bvid={bvid}"

    headers = {
        "User-Agent": get_random_user_agent(),
        "Referer": "https://www.bilibili.com/",
    }

    try:
        response, error = make_request_with_retry(info_url, headers)
        if error:
            return None, error

        data = response.json()
        if data.get("code") != 0:
            return None, f"B站API返回错误: {data.get('message')}"

        data = data.get("data", {})
        if not data:
            return None, "未找到视频信息"

        pubdate = data.get("pubdate", "")
        if pubdate:
            pubdate = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d")

        # 获取视频链接和 UP 主主页链接
        video_url = f"https://www.bilibili.com/video/{bvid}"
        up_mid = data.get("owner", {}).get("mid", "")
        up_url = f"https://space.bilibili.com/{up_mid}"

        # 提取视频信息
        video_info = [
            {"key": "封面", "value": data.get("pic", "")},
            {"key": "标题", "value": data.get("title", ""), "link": video_url},
            {"key": "UP主", "value": data.get("owner", {}).get("name", ""),"link":up_url},
            {"key": "播放量", "value": data.get("stat", {}).get("view", "")},
            {"key": "点赞数", "value": data.get("stat", {}).get("like", "")},
            {"key": "投币数", "value": data.get("stat", {}).get("coin", "")},
            {"key": "收藏数", "value": data.get("stat", {}).get("favorite", "")},
            {"key": "转发量", "value": data.get("stat", {}).get("share", "")},
            {"key": "视频简介", "value": data.get("desc", "")},
            {"key": "视频时长", "value": seconds_to_minutes(data.get("duration", ""))},
            {"key": "发布时间", "value": pubdate},
        ]
        return video_info, None
    except Exception as e:
        return None, f"请求失败: {e}"

#获取user_agents池
def get_random_user_agent():
    return random.choice(USER_AGENTS)


def make_request_with_retry(url, headers, max_retries=3, delay_base=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()

            if data.get('code') == -352:
                wait_time = delay_base * (attempt + 1) + random.uniform(0, 5)
                time.sleep(wait_time)
                continue

            return response, None
        except Exception as e:
            if attempt == max_retries - 1:
                return None, str(e)
            wait_time = delay_base * (attempt + 1) + random.uniform(0, 5)
            time.sleep(wait_time)

    return None, f"请求失败，重试{max_retries}次后仍不成功"


def get_video_comments(bvid, max_comments=100):
    """获取视频评论 - 改进版"""
    comments = []
    try:
        # 1. 首先获取视频aid(oid)
        video_info_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
        headers = {
            'User-Agent': get_random_user_agent(),
            'Referer': f'https://www.bilibili.com/video/{bvid}',
            'Origin': 'https://www.bilibili.com'
        }

        time.sleep(2 + random.random())  # 初始延迟

        video_response, error = make_request_with_retry(video_info_url, headers)
        if error:
            return None, f"获取视频信息失败: {error}"

        video_data = video_response.json()
        if video_data.get('code') != 0:
            return None, f"获取视频信息失败: {video_data.get('message')}"

        aid = video_data['data']['aid']

        # 2. 使用新API获取评论
        page = 1
        last_count = 0
        while len(comments) < max_comments:
            # 动态延迟 - 根据已获取评论数调整
            base_delay = 3.0 + (len(comments) / max_comments * 10)
            time.sleep(base_delay + random.uniform(0, 2))

            url = f'https://api.bilibili.com/x/v2/reply/main?next={page}&type=1&oid={aid}&mode=3'

            response, error = make_request_with_retry(url, headers)
            if error:
                return None, error

            data = response.json()
            if data.get('code') == -352:
                time.sleep(30 + random.uniform(0, 15))
                continue

            if not data.get('data') or not data['data'].get('replies'):
                break  # 没有更多评论

            for comment in data['data']['replies']:
                comments.append(comment['content']['message'])
                if len(comments) >= max_comments:
                    break

            print(f"已获取 {len(comments)}/{max_comments} 条评论")

            # 检查是否还有新评论
            if last_count == len(comments):
                break
            last_count = len(comments)

            page += 1

        return comments[:max_comments], None

    except Exception as e:
        return None, f"获取评论失败: {str(e)}"


def analyze_comments(comments):
    """分析评论内容"""
    if not comments:
        return None, "没有评论可分析"

    try:

        # 获取绝对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        stopwords_path = os.path.join(base_dir, 'resources', 'stopwords.txt')

        # 1. 分词处理
        all_text = ' '.join(comments)
        words = jieba.lcut(all_text)

        # 去除停用词和单字词
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            stopwords = set([line.strip() for line in f])

        words = [word for word in words if len(word) > 1 and word not in stopwords]

        # 2. 词频统计
        word_freq = Counter(words)
        top_words = word_freq.most_common(50)

        # 3. 情感分析
        sentiments = []
        for comment in comments:
            try:
                s = SnowNLP(comment)
                sentiments.append(s.sentiments)
            except:
                continue

        # 计算情感分布
        positive = sum(1 for s in sentiments if s > 0.6)
        neutral = sum(1 for s in sentiments if 0.4 <= s <= 0.6)
        negative = sum(1 for s in sentiments if s < 0.4)
        total = len(sentiments)

        if total > 0:
            sentiment_dist = {
                'positive': round(positive / total * 100, 1),
                'neutral': round(neutral / total * 100, 1),
                'negative': round(negative / total * 100, 1)
            }
        else:
            sentiment_dist = {'positive': 0, 'neutral': 0, 'negative': 0}

        # 4. 生成词云图
        try:
            wordcloud_img = generate_wordcloud(word_freq)
            if not wordcloud_img:
                raise ValueError("generate_wordcloud返回了空值")
        except Exception as e:
            print(f"生成词云图失败: {str(e)}")
            wordcloud_img = None

        return {
                   'top_words': top_words,
                   'sentiment_dist': sentiment_dist,
                   'wordcloud': wordcloud_img  # 可能为None
               }, None

    except Exception as e:
        return None, f"分析评论失败: {str(e)}"


def generate_wordcloud(word_freq):
    """生成词云图并返回base64编码"""
    try:
        # 获取绝对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "resources", "SimHei.ttf")

        # 验证字体文件
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字体文件不存在: {font_path}")

        # 验证词频数据
        if not word_freq or len(word_freq) < 3:  # 至少需要3个词
            raise ValueError("词频数据不足")

        # 配置词云（兼容旧版Pillow）
        wc = WordCloud(
            font_path=font_path,
            width=800,
            height=600,
            background_color="white",
            max_words=200,
            collocations=False,  # 禁用词组
            prefer_horizontal=0.9  # 调整水平文本比例
        )

        # 生成词云
        plt.switch_backend('Agg')  # 确保使用非交互式后端
        plt.figure(figsize=(10, 8))

        try:
            wc.generate_from_frequencies(word_freq)
            plt.imshow(wc, interpolation="bilinear")
        except Exception as e:
            # 备用方案：使用系统字体
            print(f"使用指定字体失败，尝试系统默认字体: {e}")
            wc = WordCloud(
                width=800,
                height=600,
                background_color="white",
                max_words=200
            )
            wc.generate_from_frequencies(word_freq)
            plt.imshow(wc, interpolation="bilinear")

        plt.axis("off")

        # 转换为base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", dpi=120, bbox_inches="tight", pad_inches=0)
        plt.close()

        img_buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode('utf-8')}"

    except Exception as e:
        print(f"❌ 词云生成失败: {str(e)}")
        # 返回透明占位图
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


# 添加静态文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 用户相关路由
@app.route("/register", methods=["POST"])
def register():
    """用户注册"""
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    try:
        register_user(username, password)
        return jsonify({"message": "注册成功"}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"error": "用户名已存在"}), 400


@app.route("/login", methods=["POST"])
def login():
    """用户登录"""
    username = request.form.get("username")
    password = request.form.get("password")

    user = login_user(username, password)
    if user:
        return jsonify({
            "message": "登录成功",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "avatar": user["avatar"]
            }
        }), 200
    else:
        return jsonify({"error": "用户名或密码错误"}), 401


@app.route("/user/update", methods=["PUT"])
def update_user():
    """更新用户信息"""
    data = request.get_json()  # 修改为获取JSON数据
    user_id = data.get("user_id")
    new_username = data.get("username")
    new_password = data.get("password")

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 检查用户名是否已存在
            if new_username:
                cursor.execute("""
                    SELECT id FROM users 
                    WHERE username = %s AND id != %s
                """, (new_username, user_id))
                if cursor.fetchone():
                    return jsonify({"error": "用户名已存在"}), 400

                cursor.execute("""
                    UPDATE users SET username = %s 
                    WHERE id = %s
                """, (new_username, user_id))

            # 更新密码
            if new_password:
                cursor.execute("""
                    UPDATE users SET password = %s 
                    WHERE id = %s
                """, (new_password, user_id))

            # 获取更新后的用户信息
            cursor.execute("""
                SELECT id, username, avatar FROM users
                WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()

        conn.commit()

    return jsonify({
        "message": "更新成功",
        "user": user
    })


@app.route("/user/avatar", methods=["POST"])
def upload_avatar():
    """上传用户头像"""
    if 'avatar' not in request.files:
        return jsonify({"error": "未上传文件"}), 400

    file = request.files['avatar']
    user_id = request.form.get('user_id')

    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    # 确保static/avatars目录存在
    upload_folder = os.path.join(app.root_path, 'static', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)

    if file and allowed_file(file.filename):
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"avatar_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        save_path = os.path.join(upload_folder, filename)

        file.save(save_path)

        # 更新数据库 - 使用绝对URL路径
        avatar_url = f"http://127.0.0.1:5000/static/avatars/{filename}"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET avatar = %s 
                    WHERE id = %s
                """, (avatar_url, user_id))
                cursor.execute("""
                    SELECT id, username, avatar FROM users
                    WHERE id = %s
                """, (user_id,))
                user = cursor.fetchone()
            conn.commit()

        return jsonify({
            "message": "头像上传成功",
            "avatar_url": avatar_url,
            "user": user
        })
    else:
        return jsonify({"error": "只支持png, jpg, jpeg, gif格式"}), 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route("/crawl", methods=["POST","GET"])
def crawl():
    """爬取视频信息"""
    if request.method == "GET":
        return jsonify({"message": "后端运行成功！请使用 POST 请求提交 BV 号以获取视频信息。"}), 200

    input = request.form.get("bvid","").strip()
    user_id = request.form.get("user_id")  # 获取user_id

    bvid = extract_bvid(input)
    if not bvid:
        return jsonify({"error":"无效的BV号链接"}),400

    # 获取视频信息
    video_info, error = get_video_info(bvid)
    if error:
        return jsonify({"error": error}), 500

    save_video_info(bvid, video_info, user_id)
    save_query_history(bvid, user_id)
    # 返回结果
    return jsonify({"video_info": video_info})

@app.route("/history/delete", methods=["DELETE"])
def delete_history():
    """清空历史记录"""
    user_id = request.args.get("user_id")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("DELETE FROM query_history WHERE user_id = %s", (user_id,))
            else:
                cursor.execute("DELETE FROM query_history WHERE user_id IS NULL")
        conn.commit()
    return jsonify({"message": "历史记录已清空"}), 200

@app.route("/history/delete/<int:history_id>", methods=["DELETE"])
def delete_single_history(history_id):
    """删除单条历史记录"""
    user_id = request.args.get("user_id")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("DELETE FROM query_history WHERE id = %s AND user_id = %s", (history_id, user_id))
            else:
                cursor.execute("DELETE FROM query_history WHERE id = %s AND user_id IS NULL", (history_id,))
        conn.commit()
    return jsonify({"message": "历史记录已删除"}), 200


# 修改历史记录查询API
@app.route("/history")
def history():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    user_id = request.args.get("user_id", type=int)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("""
                    SELECT h.id, h.bvid, h.query_time, v.title 
                    FROM query_history h
                    LEFT JOIN videos v ON h.bvid = v.bvid
                    WHERE h.user_id = %s
                    ORDER BY h.query_time DESC
                    LIMIT %s OFFSET %s
                """, (user_id, per_page, (page - 1) * per_page))
            else:
                cursor.execute("""
                    SELECT h.id, h.bvid, h.query_time, v.title 
                    FROM query_history h
                    LEFT JOIN videos v ON h.bvid = v.bvid
                    WHERE h.user_id IS NULL
                    ORDER BY h.query_time DESC
                    LIMIT %s OFFSET %s
                """, (per_page, (page - 1) * per_page))
            history = cursor.fetchall()

    return jsonify({
        "history": history,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(history),
            "pages": (len(history) + per_page - 1) // per_page
        }
    })


@app.route("/comments", methods=["GET"])
def get_comments():
    """获取视频评论"""
    bvid = request.args.get("bvid")
    if not bvid:
        return jsonify({"error": "缺少BV号参数"}), 400

    try:
        # 限制最大评论数为50，减少请求压力
        comments, error = get_video_comments(bvid, max_comments=50)
        if error:
            if "频率限制" in error or "352" in error:
                return jsonify({
                    "error": "请求过于频繁，请30分钟后再试",
                    "code": 429
                }), 429
            return jsonify({"error": error}), 500

        return jsonify({
            "comments": comments,
            "count": len(comments) if comments else 0
        })
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    """分析评论"""
    data = request.get_json()
    if not data or 'comments' not in data:
        return jsonify({"error": "缺少评论数据"}), 400

    analysis_result, error = analyze_comments(data['comments'])
    if error:
        return jsonify({"error": error}), 500

    return jsonify(analysis_result)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000,debug=True)
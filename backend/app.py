from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os
import pymysql
from datetime import datetime

app = Flask(__name__)
CORS(app)

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
                    avatar VARCHAR(200) DEFAULT 'default_avatar.png',
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    try:
        response = requests.get(info_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, f"请求失败，状态码: {response.status_code}"

        data = response.json()
        if data.get("code") != 0:
            return None, f"B站API返回错误: {data.get('message')}"

        data = response.json().get("data", {})
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
    except requests.exceptions.RequestException as e:
        return None, f"请求失败: {e}"


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

@app.route("/history/delete/<bvid>", methods=["DELETE"])
def delete_single_history(bvid):
    """删除单条历史记录"""
    user_id = request.args.get("user_id")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("DELETE FROM query_history WHERE bvid = %s AND user_id = %s", (bvid, user_id))
            else:
                cursor.execute("DELETE FROM query_history WHERE bvid = %s AND user_id IS NULL", (bvid,))
        conn.commit()
    return jsonify({"message": f"已删除 BV 号为 {bvid} 的历史记录"}), 200


@app.route("/history")
def history():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    user_id = request.args.get("user_id",type=int)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("SELECT COUNT(*) as total FROM query_history WHERE user_id = %s", (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) as total FROM query_history WHERE user_id IS NULL")
            total = cursor.fetchone()["total"]

            # 获取分页数据 (添加用户过滤)
            if user_id:
                cursor.execute("""
                                SELECT bvid, query_time FROM query_history
                                WHERE user_id = %s
                                ORDER BY query_time DESC
                                LIMIT %s OFFSET %s
                            """, (user_id, per_page, (page - 1) * per_page))
            else:
                cursor.execute("""
                                SELECT bvid, query_time FROM query_history
                                WHERE user_id IS NULL
                                ORDER BY query_time DESC
                                LIMIT %s OFFSET %s
                            """, (per_page, (page - 1) * per_page))
            history = cursor.fetchall()

    return jsonify({
        "history": history,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000,debug=True)
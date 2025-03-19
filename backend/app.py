from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE="Bilibili.db"

def init_db():
    """初始化数据库"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # 创建 videos 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bvid TEXT UNIQUE NOT NULL,
                title TEXT,
                up_name TEXT,
                cover_url TEXT,
                view_count INTEGER,
                like_count INTEGER,
                coin_count INTEGER,
                favorite_count INTEGER,
                description TEXT,
                duration TEXT,
                pubdate TEXT
            )
        """)
        # 创建 query_history 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bvid TEXT NOT NULL,
                query_time TEXT NOT NULL,
                FOREIGN KEY (bvid) REFERENCES videos (bvid)
            )
        """)
        conn.commit()

def save_video_info(bvid, video_info):
    """保存视频信息到数据库"""
    video_dict = {item["key"]: item["value"] for item in video_info}

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO videos (
                bvid, title, up_name, cover_url, view_count, like_count,
                coin_count, favorite_count, description, duration, pubdate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
            video_dict.get("发布时间", "")
        ))
        conn.commit()

def save_query_history(bvid):
    """保存查询历史记录"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO query_history (bvid, query_time)
            VALUES (?, ?)
        """, (bvid, datetime.now().isoformat()))
        conn.commit()

def get_query_history():
    """获取查询历史记录"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bvid, query_time FROM query_history
            ORDER BY query_time DESC
            LIMIT 100
        """)
        history = cursor.fetchall()
        return [{"bvid": item[0], "query_time": item[1]} for item in history]

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


        # 提取视频信息
        video_info = [
            {"key": "封面", "value": data.get("pic", "")},
            {"key": "UP主", "value": data.get("owner", {}).get("name", "")},
            {"key": "播放量", "value": data.get("stat", {}).get("view", "")},
            {"key": "点赞数", "value": data.get("stat", {}).get("like", "")},
            {"key": "投币数", "value": data.get("stat", {}).get("coin", "")},
            {"key": "收藏数", "value": data.get("stat", {}).get("favorite", "")},
            {"key": "视频简介", "value": data.get("desc", "")},
            {"key": "视频时长", "value": seconds_to_minutes(data.get("duration", ""))},
            {"key": "发布时间", "value": pubdate},
        ]
        return video_info, None
    except requests.exceptions.RequestException as e:
        return None, f"请求失败: {e}"

@app.route("/crawl", methods=["POST","GET"])
def crawl():
    """爬取视频信息"""
    if request.method == "GET":
        return jsonify({"message": "后端运行成功！请使用 POST 请求提交 BV 号以获取视频信息。"}), 200

    input = request.form.get("bvid","").strip()

    bvid = extract_bvid(input)
    if not bvid:
        return jsonify({"error":"无效的BV号链接"}),400

    # 获取视频信息
    video_info, error = get_video_info(bvid)
    if error:
        return jsonify({"error": error}), 500

    save_video_info(bvid, video_info)
    save_query_history(bvid)

    # 返回结果
    return jsonify({"video_info": video_info})

@app.route("/history")
def history():
    """获取查询历史记录"""
    history = get_query_history()
    return jsonify({"history": history})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
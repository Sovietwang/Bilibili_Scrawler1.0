from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

    bvid = request.form.get("bvid")
    if not bvid:
        return jsonify({"error": "请输入视频BV号！"}), 400

    # 校验BV号格式
    if not re.match(r"^BV[a-zA-Z0-9]{10}$", bvid):
        return jsonify({"error": "无效的BV号格式！"}), 400

    # 获取视频信息
    video_info, error = get_video_info(bvid)
    if error:
        return jsonify({"error": error}), 500

    # 返回结果
    return jsonify({"video_info": video_info})


if __name__ == "__main__":
    app.run(debug=True)
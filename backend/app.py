from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

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

        data = response.json().get("data", {})
        if not data:
            return None, "未找到视频信息"

        # 提取视频信息
        video_info = {
            "标题": data.get("title"),
            "播放量": data.get("stat", {}).get("view"),
            "UP主": data.get("owner", {}).get("name"),
            "点赞数": data.get("stat", {}).get("like"),
            "投币数": data.get("stat", {}).get("coin"),
            "收藏数": data.get("stat", {}).get("favorite"),
            "视频简介": data.get("desc"),
            "视频时长(秒)": data.get("duration"),
            "发布时间": data.get("pubdate"),
        }
        return video_info, None
    except requests.exceptions.RequestException as e:
        return None, f"请求失败: {e}"

@app.route("/crawl", methods=["POST"])
def crawl():
    """爬取视频信息"""
    bvid = request.form.get("bvid")
    if not bvid:
        return jsonify({"error": "请输入视频BV号！"}), 400

    # 获取视频信息
    video_info, error = get_video_info(bvid)
    if error:
        return jsonify({"error": error}), 500

    # 返回结果
    return jsonify({"video_info": video_info})

if __name__ == "__main__":
    app.run(debug=True)
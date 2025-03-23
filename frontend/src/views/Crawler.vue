<template>
  <div class="crawler-page">
    <h1>数据爬取</h1>
    <div class="input-container">
      <input v-model="bvid" placeholder="请输入视频BV号或链接" />
      <button @click="startCrawl">开始爬取</button>
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="videoInfo" class="result">
      <h2>视频信息</h2>
      <ul>
        <li v-for="(item, index) in videoInfo" :key="index">
          <span v-if="item.key === '封面'">
            <img
              :src="item.value"
              alt="封面"
              style="max-width: 100%; height: auto;"
              
            />
          </span>
          <span v-else-if="item.link">
            <a :href="item.link" target="_blank" class="link">{{ item.value }}</a>
          </span>
          <span v-else>
            <strong>{{ item.key }}:</strong> {{ item.value }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      bvid: "",
      videoInfo: null,
      loading: false,
      error: "",
    };
  },

  computed: {
    // 格式化视频信息为数组，避免显示多余的“·”
    formattedVideoInfo() {
      if (!this.videoInfo) return [];
      return [
        { key: "封面", value: this.videoInfo.封面 },
        { key: "标题", value: this.videoInfo.标题 },
        { key: "UP主", value: this.videoInfo.UP主 },
        { key: "播放量", value: this.videoInfo.播放量 },
        { key: "点赞数", value: this.videoInfo.点赞数 },
        { key: "投币数", value: this.videoInfo.投币数 },
        { key: "收藏数", value: this.videoInfo.收藏数 },
        { key: "视频简介", value: this.videoInfo.视频简介 },
        { key: "视频时长", value: this.videoInfo.视频时长 },
        { key: "发布时间", value: this.videoInfo.发布时间 },
      ];
    }
  },

  methods: {
    async startCrawl() {
      if (!this.bvid) {
        this.error = "请输入视频BV号或链接！";
        return;
      }

      this.loading = true;
      this.error = "";

      try {
        const response = await fetch("http://127.0.0.1:5000/crawl", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: `bvid=${this.bvid}`,
        });

        const data = await response.json();
        if (data.error) {
          this.error = data.error;
        } else {
          this.videoInfo = data.video_info;
          // 保存到 localStorage
          localStorage.setItem("currentVideoInfo", JSON.stringify(data.video_info));
        }
      } catch (err) {
        this.error = "请求失败：" + err.message;
      } finally {
        this.loading = false;
      }

      
    },
  },
  
  mounted() {
    // 从 localStorage 加载上次查询结果
    const savedVideoInfo = localStorage.getItem("currentVideoInfo");
    if (savedVideoInfo) {
      this.videoInfo = JSON.parse(savedVideoInfo);
    }
    // 如果路由中有 BV 号参数，自动查询
    const routeBvid = this.$route.query.bvid;
    if (routeBvid) {
      this.bvid = routeBvid;
      this.startCrawl();
    }
  },
};
</script>

<style scoped>
.crawler-page {
  font-family: Arial, sans-serif;
  max-width: 600px; /* 最大宽度 */
  width: 100%; /* 确保宽度占满父容器 */
  margin: 0 auto; /* 居中 */
  padding: 20px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  box-sizing: border-box; /* 确保 padding 不会影响宽度 */
}

.input-container {
  display: flex;
  gap: 20px;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

button {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  background-color: #1890ff;
  color: white;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #40a9ff;
}

.loading {
  color: #1890ff;
  font-size: 16px;
  text-align: center;
  margin-top: 20px;
}

.error {
  color: #ff4d4f;
  font-size: 16px;
  text-align: center;
  margin-top: 20px;
}

.result {
  margin-top: 20px;
}

.result ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.result li {
  display: flex;
  flex-direction: column;
  padding: 12px;
  margin-bottom: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result li:hover {
  background-color: #e9ecef;
}

.result li strong {
  color: #333;
  margin-bottom: 8px;
}

.result li img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin-bottom: 8px;
}
.link {
  color: #007bff;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
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
            <img :src="item.value" alt="封面" style="max-width: 100%; height: auto;" />
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
    <!-- 在Crawler.vue的template中添加 -->
    <div v-if="videoInfo" class="analysis-section">
      <h2>评论分析</h2>
      <button @click="analyzeComments" :disabled="analysisLoading">
        {{ analysisLoading ? '分析中...' : '分析评论' }}
      </button>

      <div v-if="analysisError" class="error">{{ analysisError }}</div>

      <div v-if="analysisResult" class="analysis-results">
        <!-- 词云图 -->
        <div class="wordcloud-container">
          <h3>评论词云</h3>
          <img :src="analysisResult.wordcloud" alt="词云图" class="wordcloud-img">
        </div>

        <!-- 情感分析 -->
        <div class="sentiment-analysis">
          <h3>情感分布</h3>
          <div class="sentiment-stats">
            <div class="sentiment-item positive">
              <span>积极: {{ analysisResult.sentiment_dist.positive }}%</span>
            </div>
            <div class="sentiment-item neutral">
              <span>中立: {{ analysisResult.sentiment_dist.neutral }}%</span>
            </div>
            <div class="sentiment-item negative">
              <span>消极: {{ analysisResult.sentiment_dist.negative }}%</span>
            </div>
          </div>
        </div>

        <!-- 高频词 -->
        <div class="top-words">
          <h3>高频词汇</h3>
          <div class="word-tags">
            <span v-for="(word, index) in analysisResult.top_words" :key="index" class="word-tag">
              {{ word[0] }} ({{ word[1] }})
            </span>
          </div>
        </div>
      </div>
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
      analysisResult: null,
      analysisLoading: false,
      analysisError: ""
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
        const user = JSON.parse(localStorage.getItem('user'));
        const formData = new FormData();
        formData.append('bvid', this.bvid);
        if (user) {
          formData.append('user_id', user.id);
        }

        const response = await fetch("http://127.0.0.1:5000/crawl", {
          method: "POST",
          body: formData
        });

        const data = await response.json();
        if (data.error) {
          this.error = data.error;
        } else {
          this.videoInfo = data.video_info;
          localStorage.setItem("currentVideoInfo", JSON.stringify(data.video_info));
        }
      } catch (err) {
        this.error = "请求失败：" + (err.message || "请检查网络连接");
        console.error("爬取失败:", err);
      } finally {
        this.loading = false;
      }
    },

    async analyzeComments() {
      if (!this.videoInfo) {
        this.analysisError = "请先获取视频信息";
        return;
      }

      this.analysisLoading = true;
      this.analysisError = "";

      try {
        // 1. 获取评论
        const bvid = this.extractBvid(this.bvid);
        const commentsResponse = await fetch(
          `http://127.0.0.1:5000/comments?bvid=${bvid}&max_comments=100`
        );
        const commentsData = await commentsResponse.json();

        if (commentsData.error || !commentsData.comments) {
          throw new Error(commentsData.error || "无法获取评论");
        }

        // 2. 发送分析请求
        const analysisResponse = await fetch("http://127.0.0.1:5000/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ comments: commentsData.comments }),
        });

        const analysisData = await analysisResponse.json();
        if (analysisData.error) {
          throw new Error(analysisData.error);
        }

        this.analysisResult = analysisData;
      } catch (err) {
        this.analysisError = "分析失败: " + err.message;
        console.error("分析评论失败:", err);
      } finally {
        this.analysisLoading = false;
      }
    },

    extractBvid(input) {
      const bvidPattern = /(BV[0-9A-Za-z]{10})/;
      const match = bvidPattern.exec(input);
      return match ? match[0] : input;
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
  max-width: 600px;
  /* 最大宽度 */
  width: 100%;
  /* 确保宽度占满父容器 */
  margin: 0 auto;
  /* 居中 */
  padding: 20px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  /* 确保 padding 不会影响宽度 */
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

.analysis-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.analysis-results {
  margin-top: 20px;
}

.wordcloud-img {
  max-width: 100%;
  height: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.sentiment-stats {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.sentiment-item {
  padding: 8px 12px;
  border-radius: 4px;
  color: white;
}

.positive {
  background-color: #52c41a;
}

.neutral {
  background-color: #faad14;
}

.negative {
  background-color: #ff4d4f;
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.word-tag {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 14px;
}
</style>
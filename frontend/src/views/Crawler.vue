<template>
  <div class="crawler-page">
    <h1>数据爬取</h1>
    <div class="input-container">
      <input 
        v-model="bvid" 
        placeholder="请输入视频BV号或链接"
        @keyup.enter="startCrawl"
      />
      <button @click="startCrawl" :disabled="combinedLoading">
        {{ combinedLoading ? '处理中...' : '开始爬取' }}
      </button>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="combinedLoading" class="analysis-progress">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progress + '%' }"
        ></div>
      </div>
      <p class="progress-text">{{ statusMessage }}</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error">{{ error }}</div>
    
    <!-- 视频信息 -->
    <div v-if="videoInfo" class="result">
      <h2>视频信息</h2>
      <ul>
        <li v-for="(item, index) in videoInfo" :key="index">
          <span v-if="item.key === '封面'">
            <img :src="item.value" alt="封面" class="cover-image" />
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
    
    <!-- 评论分析区域 -->
    <div v-if="videoInfo" class="analysis-section">
      <h2>评论分析</h2>
      <button 
        @click="analyzeComments" 
        :disabled="analysisLoading || combinedLoading"
        class="analyze-btn"
      >
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
            <span 
              v-for="(word, index) in analysisResult.top_words" 
              :key="index" 
              class="word-tag"
              :style="{ fontSize: getWordSize(word[1]) }"
            >
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
      analysisError: "",
      combinedLoading: false,
      // 新增进度相关状态
      progress: 0,
      statusMessage: "准备开始...",
      progressInterval: null,
      // 用于路由切换拦截
      shouldConfirmLeave: false
    };
  },

  computed: {
    formattedVideoInfo() {
      if (!this.videoInfo) return [];
      return [
        { key: "封面", value: this.videoInfo.封面 },
        { key: "标题", value: this.videoInfo.标题, link: this.videoInfo.标题?.link },
        { key: "UP主", value: this.videoInfo.UP主, link: this.videoInfo.UP主?.link },
        { key: "播放量", value: this.videoInfo.播放量 },
        { key: "点赞数", value: this.videoInfo.点赞数 },
        { key: "投币数", value: this.videoInfo.投币数 },
        { key: "收藏数", value: this.videoInfo.收藏数 },
        { key: "视频简介", value: this.videoInfo.视频简介 },
        { key: "视频时长", value: this.videoInfo.视频时长 },
        { key: "发布时间", value: this.videoInfo.发布时间 },
      ].filter(item => item.value !== undefined);
    }
  },

  methods: {
    async startCrawl() {
      if (!this.bvid) {
        this.error = "请输入视频BV号或链接！";
        return;
      }

      this.combinedLoading = true;
      this.error = "";
      this.analysisError = "";
      this.shouldConfirmLeave = true;
      this.startProgress("正在获取视频信息...");

      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const formData = new FormData();
        formData.append('bvid', this.bvid);
        if (user) {
          formData.append('user_id', user.id);
        }

        // 1. 获取视频信息
        this.updateProgress(20, "正在获取视频信息...");
        const response = await fetch("http://127.0.0.1:5000/crawl", {
          method: "POST",
          body: formData
        });

        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }

        this.videoInfo = data.video_info;
        this.updateProgress(50, "视频信息获取成功");

        // 2. 自动开始分析评论
        await this.analyzeComments();

        // 3. 统一保存数据
        this.saveToLocalStorage();

      } catch (err) {
        this.error = "请求失败：" + (err.message || "请检查网络连接");
        console.error("操作失败:", err);
      } finally {
        this.stopProgress();
        this.combinedLoading = false;
        this.shouldConfirmLeave = false;
      }
    },

    async analyzeComments() {
      if (!this.videoInfo) return;

      this.analysisLoading = true;
      this.shouldConfirmLeave = true;
      this.startProgress("正在分析评论...");

      try {
        const bvid = this.extractBvid(this.bvid);
        
        // 1. 获取评论
        this.updateProgress(30, "正在获取评论...");
        const commentsResponse = await fetch(
          `http://127.0.0.1:5000/comments?bvid=${bvid}`
        );
        const commentsData = await commentsResponse.json();

        if (commentsData.error || !commentsData.comments) {
          throw new Error(commentsData.error || "无法获取评论");
        }

        // 2. 分析评论
        this.updateProgress(60, "正在分析情感...");
        const analysisResponse = await fetch("http://127.0.0.1:5000/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ comments: commentsData.comments }),
        });

        this.updateProgress(80, "正在生成词云...");
        const analysisData = await analysisResponse.json();

        if (analysisData.error) {
          throw new Error(analysisData.error);
        }

        this.analysisResult = analysisData;
        this.updateProgress(100, "分析完成!");

      } catch (err) {
        this.analysisError = "分析失败: " + err.message;
        console.error("分析评论失败:", err);
      } finally {
        this.stopProgress();
        this.analysisLoading = false;
        this.shouldConfirmLeave = false;
      }
    },

    // 进度条相关方法
    startProgress(initialMessage = "处理中...") {
      this.statusMessage = initialMessage;
      this.progress = 0;
      // 基础进度模拟
      this.progressInterval = setInterval(() => {
        if (this.progress < 90) {
          this.progress += 2;
        }
      }, 500);
    },
    
    updateProgress(value, message) {
      this.progress = value;
      this.statusMessage = message;
    },
    
    stopProgress() {
      clearInterval(this.progressInterval);
      this.progress = 100;
      setTimeout(() => {
        this.progress = 0;
      }, 1000);
    },

    // 其他方法
    extractBvid(input) {
      const bvidPattern = /(BV[0-9A-Za-z]{10})/;
      const match = bvidPattern.exec(input);
      return match ? match[0] : input;
    },

    saveToLocalStorage() {
      const saveData = {
        bvid: this.extractBvid(this.bvid),
        videoInfo: this.videoInfo,
        analysisResult: this.analysisResult,
        timestamp: Date.now()
      };
      localStorage.setItem("videoAnalysisData", JSON.stringify(saveData));
    },

    getWordSize(count) {
      // 根据词频计算字体大小
      const baseSize = 12;
      const maxSize = 24;
      return `${Math.min(baseSize + count, maxSize)}px`;
    }
  },

  beforeRouteLeave(to, from, next) {
    if (this.shouldConfirmLeave) {
      const answer = confirm('分析正在进行中，切换页面将中断当前操作。确定要离开吗？');
      if (answer) {
        next();
      } else {
        next(false);
      }
    } else {
      next();
    }
  },

  mounted() {
    // 从 localStorage 加载数据
    const savedData = localStorage.getItem("videoAnalysisData");
    if (savedData) {
      const data = JSON.parse(savedData);
      this.bvid = data.bvid;
      this.videoInfo = data.videoInfo;
      this.analysisResult = data.analysisResult;
    }

    // 路由参数处理
    const routeBvid = this.$route.query.bvid;
    if (routeBvid && routeBvid !== this.bvid) {
      this.bvid = routeBvid;
      this.startCrawl();
    }
  }
};
</script>

<style scoped>
.crawler-page {
  font-family: Arial, sans-serif;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.input-container {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

input {
  flex: 1;
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
  transition: all 0.3s ease;
}

button:hover:not(:disabled) {
  background-color: #40a9ff;
  transform: translateY(-1px);
}

button:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
  transform: none;
}

.analyze-btn {
  background-color: #52c41a;
}

.analyze-btn:hover:not(:disabled) {
  background-color: #73d13d;
}

/* 进度条样式 */
.analysis-progress {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #e8e8e8;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1890ff, #096dd9);
  transition: width 0.5s ease;
}

.progress-text {
  color: #666;
  font-size: 14px;
  text-align: center;
  margin-top: 5px;
}

/* 错误提示 */
.error {
  color: #ff4d4f;
  font-size: 16px;
  text-align: center;
  margin: 20px 0;
  padding: 10px;
  background-color: #fff2f0;
  border-radius: 4px;
  border-left: 3px solid #ff4d4f;
}

/* 视频信息样式 */
.result {
  margin-top: 30px;
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
  transition: all 0.3s ease;
}

.result li:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
}

.result li strong {
  color: #333;
  margin-bottom: 8px;
}

.cover-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin-bottom: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.link {
  color: #1890ff;
  text-decoration: none;
  transition: all 0.2s;
}

.link:hover {
  color: #096dd9;
  text-decoration: underline;
}

/* 分析结果区域 */
.analysis-section {
  margin-top: 40px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.analysis-results {
  margin-top: 20px;
}

.wordcloud-container, .sentiment-analysis, .top-words {
  margin-bottom: 30px;
}

.wordcloud-img {
  max-width: 100%;
  height: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sentiment-stats {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.sentiment-item {
  padding: 8px 15px;
  border-radius: 4px;
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.positive {
  background: linear-gradient(135deg, #52c41a, #389e0d);
}

.neutral {
  background: linear-gradient(135deg, #faad14, #d48806);
}

.negative {
  background: linear-gradient(135deg, #ff4d4f, #cf1322);
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.word-tag {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 15px;
  padding: 5px 12px;
  font-size: 14px;
  color: #096dd9;
  transition: all 0.3s;
}

.word-tag:hover {
  background-color: #bae7ff;
  transform: translateY(-2px);
}
</style>
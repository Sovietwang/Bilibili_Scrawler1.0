<template>
  <div id="app">
    <h1>B站视频爬虫</h1>
    <div class="input-container">
      <input v-model="bvid" placeholder="请输入视频BV号" />
      <button @click="startCrawl">开始爬取</button>
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="videoInfo" class="result">
      <h2>视频信息</h2>
      <ul>
        <li v-for="(value, key) in videoInfo" :key="key">
          <strong>{{ key }}:</strong> {{ value }}
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
  methods: {
    async startCrawl() {
      if (!this.bvid) {
        this.error = "请输入视频BV号！";
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
        }
      } catch (err) {
        this.error = "请求失败：" + err.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.input-container {
  margin-bottom: 20px;
}

input {
  width: 300px;
  padding: 8px;
  font-size: 16px;
}

button {
  padding: 8px 16px;
  font-size: 16px;
  cursor: pointer;
}

.loading,
.error {
  margin-top: 20px;
  color: red;
}

.result {
  margin-top: 20px;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin-bottom: 10px;
}
</style>
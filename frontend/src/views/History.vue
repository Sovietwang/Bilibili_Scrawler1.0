<template>
  <div class="history-page">
    <h1>历史记录</h1>
    <button @click="loadHistory">刷新历史记录</button>
    <div v-if="historyLoading" class="loading">加载中...</div>
    <ul v-else>
      <li v-for="(item, index) in history" :key="index" @click="goToCrawler(item.bvid)">
        <span class="bvid">{{ item.bvid }}</span>
        <span class="timestamp">{{ formatDate(item.query_time) }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      history: [],
      historyLoading: false,
    };
  },
  methods: {
    async loadHistory() {
      this.historyLoading = true;
      try {
        const response = await fetch("http://127.0.0.1:5000/history");
        const data = await response.json();
        this.history = data.history;
      } catch (err) {
        console.error("加载历史失败:", err);
      } finally {
        this.historyLoading = false;
      }
    },
    formatDate(isoString) {
      if (!isoString) return "未知时间";
      return new Date(isoString).toLocaleString();
    },
    goToCrawler(bvid) {
      this.$router.push({ path: "/crawler", query: { bvid } });
    },
  },
  mounted() {
    this.loadHistory();
  },
};
</script>

<style scoped>
.history-page {
  max-width: 800px;
  padding: 20px;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: flex;
  justify-content: space-between;
  max-width: 800px;
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

li:hover {
  background-color: #f8f9fa;
}

.bvid {
  font-family: monospace;
  color: #007bff;
}

.timestamp {
  color: #666;
  font-size: 0.9em;
}
</style>
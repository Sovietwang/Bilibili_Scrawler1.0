<template>
  <div class="history-page">
    <h1>历史记录</h1>
    <div class="actions">
      <button @click="loadHistory" class="refresh-btn">刷新历史记录</button>
      <button @click="deleteAllHistory" class="delete-all-btn">清空历史记录</button>
    </div>
    <div v-if="historyLoading" class="loading">加载中...</div>
    <ul v-else>
      <li v-for="(item, index) in history" :key="index" @click="goToCrawler(item.bvid)">
        <span class="bvid">{{ item.bvid }}</span>
        <span class="timestamp">{{ formatDate(item.query_time) }}</span>
        <button @click="deleteSingleHistory(item.bvid)" class="delete-single">删除</button>
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
        console.log("后端返回的数据：", data); // 打印后端返回的数据
        if (data.history) {
          this.history = data.history;
        } else {
          console.error("后端返回的数据格式不正确：", data);
        }
      } catch (err) {
        console.error("加载历史失败:", err);
      } finally {
        this.historyLoading = false;
      }
    },
    async deleteAllHistory() {
      if (confirm("确定要清空所有历史记录吗？")) {
        try {
          const response = await fetch("http://127.0.0.1:5000/history/delete", {
            method: "DELETE",
          });
          const data = await response.json();
          alert(data.message);
          this.loadHistory(); // 刷新历史记录
        } catch (err) {
          console.error("删除失败:", err);
        }
      }
    },
    async deleteSingleHistory(bvid) {
      if (confirm(`确定要删除 BV 号为 ${bvid} 的历史记录吗？`)) {
        try {
          const response = await fetch(`http://127.0.0.1:5000/history/delete/${bvid}`, {
            method: "DELETE",
          });
          const data = await response.json();
          alert(data.message);
          this.loadHistory(); // 刷新历史记录
        } catch (err) {
          console.error("删除失败:", err);
        }
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

.actions {
  display: flex;
  gap: 10px; /* 按钮之间的间隙 */
  margin-bottom: 20px; /* 按钮组与记录列表之间的间隙 */
}

button {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.refresh-btn {
  background-color: #1890ff;
  color: white;
}

.refresh-btn:hover {
  background-color: #40a9ff;
}

.delete-all-btn {
  background-color: #ff4d4f;
  color: white;
}

.delete-all-btn:hover {
  background-color: #ff7875;
}

.loading {
  color: #1890ff;
  font-size: 16px;
  text-align: center;
  margin-top: 20px;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

li:hover {
  background-color: #e9ecef;
}

.bvid {
  font-family: monospace;
  color: #007bff;
  flex: 1;
  margin-right: 20px;
}

.timestamp {
  color: #666;
  font-size: 0.9em;
  flex: 1;
  margin-right: 20px;
}

.delete-single-btn {
  background-color: #ff4d4f;
  color: white;
  padding: 6px 12px;
  font-size: 14px;
  border-radius: 4px;
}

.delete-single-btn:hover {
  background-color: #ff7875;
}
</style>
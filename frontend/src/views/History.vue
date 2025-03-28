<template>
  <div class="history-page">
    <h1>历史记录</h1>
    <div class="actions">
      <button @click="loadHistory" class="refresh-btn">刷新历史记录</button>
      <button @click="deleteAllHistory" class="delete-all-btn">清空历史记录</button>
    </div>
    
    <div v-if="historyLoading" class="loading">加载中...</div>
    
    <div v-else>
      <!-- 历史记录列表 -->
      <ul class="history-list">
        <li v-for="(item, index) in history" :key="index">
          <span class="bvid" @click="goToCrawler(item.bvid)">{{ item.bvid }}</span>
          <span class="timestamp">{{ formatDate(item.query_time) }}</span>
          <button @click="deleteSingleHistory(item.bvid)" class="delete-single">删除</button>
        </li>
      </ul>
      
      <!-- 分页控件 -->
      <div class="pagination-controls" v-if="pagination.totalItems > 0">
        <button 
          @click="changePage(pagination.currentPage - 1)"
          :disabled="pagination.currentPage === 1"
          class="pagination-btn"
        >
          上一页
        </button>
        
        <span class="page-info">
          第 {{ pagination.currentPage }} 页 / 共 {{ pagination.totalPages }} 页
          (共 {{ pagination.totalItems }} 条记录)
        </span>
        
        <button 
          @click="changePage(pagination.currentPage + 1)"
          :disabled="pagination.currentPage === pagination.totalPages"
          class="pagination-btn"
        >
          下一页
        </button>
      </div>
      
      <div v-if="history.length === 0" class="no-records">
        暂无历史记录
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      history: [],
      historyLoading: false,
      pagination: {
        currentPage: 1,
        itemsPerPage: 10, 
        totalItems: 0,
        totalPages: 1
      }
    };
  },
  methods: {
    async loadHistory() {
      this.historyLoading = true;
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/history?page=${this.pagination.currentPage}&per_page=${this.pagination.itemsPerPage}`
        );
        const data = await response.json();
        
        this.history = data.history || [];
        
        // 更新分页信息
        this.pagination = {
          currentPage: data.pagination?.page || 1,
          itemsPerPage: data.pagination?.per_page || 10,
          totalItems: data.pagination?.total || 0,
          totalPages: data.pagination?.pages || 1
        };
        
      } catch (err) {
        console.error("加载历史失败:", err);
        this.$notify.error({
          title: '错误',
          message: '加载历史记录失败'
        });
      } finally {
        this.historyLoading = false;
      }
    },
    
    changePage(newPage) {
      // 确保新页码在有效范围内
      newPage = Math.max(1, Math.min(newPage, this.pagination.totalPages));
      if (newPage !== this.pagination.currentPage) {
        this.pagination.currentPage = newPage;
        this.loadHistory();
      }
    },
    
    async deleteAllHistory() {
      if (confirm("确定要清空所有历史记录吗？")) {
        try {
          const response = await fetch("http://127.0.0.1:5000/history/delete", {
            method: "DELETE",
          });
          const data = await response.json();
          this.$notify.success({
            title: '成功',
            message: data.message
          });
          this.loadHistory(); // 刷新历史记录
        } catch (err) {
          console.error("删除失败:", err);
          this.$notify.error({
            title: '错误',
            message: '删除历史记录失败'
          });
        }
      }
    },
    
    async deleteSingleHistory(bvid) {
      try {
          const response = await fetch(
            `http://127.0.0.1:5000/history/delete/${bvid}`, 
            { method: "DELETE" }
          );
          if (response.ok) {
          // 直接从本地数据中移除该项
          this.history = this.history.filter(item => item.bvid !== bvid);
          this.pagination.totalItems -= 1;
          
          // 如果当前页没有数据且不是第一页，自动返回上一页
          if (this.history.length === 0 && this.pagination.currentPage > 1) {
            this.changePage(this.pagination.currentPage - 1);
          }
          
          this.$notify.success({
            title: '成功',
            message: `已删除 BV 号为 ${bvid} 的历史记录`
          });
        } else {
          throw new Error('删除失败');
        }
      } catch (err) {
        console.error("删除失败:", err);
        this.$notify.error({
          title: '错误',
          message: '删除记录失败'
        });
      }
    },
    
    formatDate(isoString) {
      if (!isoString) return "未知时间";
      return new Date(isoString).toLocaleString();
    },
    
    goToCrawler(bvid) {
      this.$router.push({ path: "/crawler", query: { bvid } });
    }
  },
  
  mounted() {
    this.loadHistory();
  }
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

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.pagination-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.pagination-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.no-records {
  text-align: center;
  color: #999;
  margin-top: 20px;
  padding: 20px;
}

.history-list {
  min-height: 300px; /* 保持列表高度稳定 */
}

</style>
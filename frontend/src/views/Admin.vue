<template>
  <div class="admin-page">
    <h1 class="page-title">管理员控制台</h1>
    
    <div class="admin-actions">
      <button @click="refreshUsers" class="primary-btn">
        <i class="icon-refresh"></i> 刷新用户列表
      </button>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="user-list">
      <div class="user-card" v-for="user in users" :key="user.id">
        <div class="user-avatar">
          <img :src="user.avatar || '/default_avatar.png'" class="avatar">
        </div>
        
        <div class="user-info">
          <div class="info-item">
            <label>ID:</label>
            <span>{{ user.id }}</span>
          </div>
          <div class="info-item">
            <label>用户名:</label>
            <input v-if="editingUser === user.id" v-model="editForm.username">
            <span v-else>{{ user.username }}</span>
          </div>
          <div class="info-item">
            <label>角色:</label>
            <select v-if="editingUser === user.id" v-model="editForm.role">
              <option value="user">普通用户</option>
              <option value="admin">管理员</option>
            </select>
            <span v-else>{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span>
          </div>
          <div class="info-item">
            <label>注册时间:</label>
            <span>{{ formatDate(user.created_at) }}</span>
          </div>
          
          <div v-if="editingUser === user.id" class="password-fields">
            <div class="info-item">
              <label>新密码:</label>
              <input v-model="editForm.newPassword" type="password" placeholder="留空则不修改">
            </div>
          </div>
        </div>
        
        <div class="user-actions">
          <template v-if="editingUser === user.id">
            <button @click="saveUser(user.id)" class="primary-btn small">
              <i class="icon-save"></i> 保存
            </button>
            <button @click="cancelEdit" class="secondary-btn small">
              <i class="icon-cancel"></i> 取消
            </button>
          </template>
          <template v-else>
            <button @click="startEdit(user)" class="secondary-btn small">
              <i class="icon-edit"></i> 编辑
            </button>
            <button 
              @click="confirmDelete(user.id)" 
              class="danger-btn small"
              v-if="user.id !== currentUser.id"
            >
              <i class="icon-delete"></i> 删除
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: [],
      loading: false,
      editingUser: null,
      editForm: {
        username: '',
        role: 'user',
        newPassword: ''
      },
      currentUser: JSON.parse(localStorage.getItem('user')) || {}
    }
  },
  created() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/admin/users?admin_id=${this.currentUser.id}`
        );
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        this.users = data.users;
      } catch (err) {
        this.$notify.error({
          title: '错误',
          message: '获取用户列表失败: ' + err.message
        });
      } finally {
        this.loading = false;
      }
    },
    
    refreshUsers() {
      this.fetchUsers();
    },
    
    startEdit(user) {
      this.editingUser = user.id;
      this.editForm = {
        username: user.username,
        role: user.role,
        newPassword: ''
      };
    },
    
    cancelEdit() {
      this.editingUser = null;
      this.editForm = {
        username: '',
        role: 'user',
        newPassword: ''
      };
    },
    
    async saveUser(userId) {
      if (!this.editForm.username) {
        this.$notify.error({ title: '错误', message: '用户名不能为空' });
        return;
      }
      
      try {
        const updateData = {
          admin_id: this.currentUser.id,
          user_id: userId,
          update_data: {
            username: this.editForm.username,
            role: this.editForm.role
          }
        };
        
        if (this.editForm.newPassword) {
          updateData.update_data.password = this.editForm.newPassword;
        }
        
        const response = await fetch('http://127.0.0.1:5000/admin/users/update', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updateData)
        });
        
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        
        this.$notify.success({
          title: '成功',
          message: '用户信息已更新'
        });
        
        this.cancelEdit();
        this.fetchUsers();
        
        // 如果修改的是当前登录用户，更新本地存储
        if (userId === this.currentUser.id) {
          localStorage.setItem('user', JSON.stringify(data.user));
          this.currentUser = data.user;
        }
      } catch (err) {
        this.$notify.error({
          title: '错误',
          message: '更新失败: ' + err.message
        });
      }
    },
    
    confirmDelete(userId) {
      if (confirm('确定要删除此用户吗？此操作不可恢复！')) {
        this.deleteUser(userId);
      }
    },
    
    async deleteUser(userId) {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/admin/users/delete?admin_id=${this.currentUser.id}&user_id=${userId}`,
          { method: 'DELETE' }
        );
        
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        
        this.$notify.success({
          title: '成功',
          message: '用户已删除'
        });
        
        this.fetchUsers();
      } catch (err) {
        this.$notify.error({
          title: '错误',
          message: '删除失败: ' + err.message
        });
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '未知';
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
}

.admin-actions {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.user-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.user-avatar {
  flex-shrink: 0;
}

.user-avatar .avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #1890ff;
}

.user-info {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-item label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
}

.info-item input, .info-item select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex-grow: 1;
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.primary-btn.small, 
.secondary-btn.small, 
.danger-btn.small {
  padding: 5px 10px;
  font-size: 12px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #1890ff;
}
</style>
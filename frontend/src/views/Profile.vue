<template>
  <div class="profile-page">
    <h1>个人信息</h1>

    <!-- 未登录状态 -->
    <!-- 未登录状态 -->
    <div v-if="!user" class="auth-container">
      <div class="auth-card">
        <!-- 登录表单 -->
        <div v-if="showLogin" class="auth-form">
          <h2 class="auth-title">用户登录</h2>
          <div class="form-group">
            <label for="loginUsername">用户名</label>
            <input id="loginUsername" v-model="loginUsername" placeholder="请输入用户名" class="form-input">
          </div>
          <div class="form-group">
            <label for="loginPassword">密码</label>
            <input id="loginPassword" v-model="loginPassword" type="password" placeholder="请输入密码" class="form-input">
          </div>
          <button @click="handleLogin" class="primary-btn">登录</button>
          <p class="switch-text">
            没有账号？<a @click="switchToRegister" class="switch-link">注册新账号</a>
          </p>
        </div>

        <!-- 注册表单 -->
        <div v-else class="auth-form">
          <h2 class="auth-title">用户注册</h2>
          <div class="form-group">
            <label for="registerUsername">用户名</label>
            <input id="registerUsername" v-model="registerUsername" placeholder="请输入用户名" class="form-input">
          </div>
          <div class="form-group">
            <label for="registerPassword">密码</label>
            <input id="registerPassword" v-model="registerPassword" type="password" placeholder="请输入密码"
              class="form-input">
          </div>
          <div class="form-group">
            <label for="registerPasswordConfirm">确认密码</label>
            <input id="registerPasswordConfirm" v-model="registerPasswordConfirm" type="password" placeholder="请再次输入密码"
              class="form-input">
          </div>
          <button @click="handleRegister" class="primary-btn">注册</button>
          <p class="switch-text">
            已有账号？<a @click="switchToLogin" class="switch-link">返回登录</a>
          </p>
        </div>
      </div>
    </div>

    <!-- 已登录状态 -->
    <div v-else class="profile-container">
      <div class="profile-card">
        <div class="avatar-section">
          <img :src="user.avatar || '/default_avatar.png'" class="avatar">
          <input type="file" id="avatar-upload" accept="image/*" @change="handleAvatarUpload" style="display: none;">
          <button @click="triggerAvatarUpload" class="secondary-btn">
            <i class="icon-upload"></i> 更换头像
          </button>
        </div>

        <div class="info-section">
          <div class="info-item">
            <label>用户名</label>
            <input v-if="editing" v-model="editUsername" class="form-input">
            <span v-else>{{ user.username }}</span>
          </div>

          <div v-if="showPasswordFields" class="info-item">
            <label>当前密码</label>
            <input v-model="currentPassword" type="password" placeholder="请输入当前密码" class="form-input">
          </div>

          <div v-if="showPasswordFields" class="info-item">
            <label>新密码</label>
            <input v-model="newPassword" type="password" placeholder="请输入新密码" class="form-input">
          </div>

          <div v-if="showPasswordFields" class="info-item">
            <label>确认新密码</label>
            <input v-model="newPasswordConfirm" type="password" placeholder="请再次输入新密码" class="form-input">
          </div>

          <div class="action-buttons">
            <button v-if="!editing" @click="startEditing" class="primary-btn">
              <i class="icon-edit"></i> 编辑资料
            </button>
            <template v-else>
              <button @click="saveProfile" class="primary-btn">
                <i class="icon-save"></i> 保存修改
              </button>
              <button @click="cancelEditing" class="secondary-btn">
                <i class="icon-cancel"></i> 取消
              </button>
            </template>
            <button @click="handleLogout" class="danger-btn">
              <i class="icon-logout"></i> 退出登录
            </button>
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
      user: JSON.parse(localStorage.getItem('user')) || null,
      showLogin: true,
      loginUsername: '',
      loginPassword: '',
      registerUsername: '',
      registerPassword: '',
      registerPasswordConfirm: '',
      editing: false,
      editUsername: '',
      currentPassword: '',
      newPassword: '',
      newPasswordConfirm: '',
      showPasswordFields: false
    }
  },
  methods: {
    switchToRegister() {
      this.showLogin = false;
      this.loginUsername = '';
      this.loginPassword = '';
    },
    switchToLogin() {
      this.showLogin = true;
      this.registerUsername = '';
      this.registerPassword = '';
      this.registerPasswordConfirm = '';
    },
    async handleLogin() {
      if (!this.loginUsername || !this.loginPassword) {
        alert('请输入用户名和密码');
        return;
      }

      try {
        const params = new URLSearchParams();
        params.append('username', this.loginUsername);
        params.append('password', this.loginPassword);

        const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: params
        });

        const data = await response.json();
        if (data.error) {
          alert(data.error);
          return;
        }

        this.user = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));
      } catch (err) {
        alert('登录失败: ' + err.message);
      }
    },
    async handleRegister() {
      if (this.registerPassword !== this.registerPasswordConfirm) {
        alert('两次输入的密码不一致');
        return;
      }

      try {
        const params = new URLSearchParams();
        params.append('username', this.registerUsername);
        params.append('password', this.registerPassword);

        const response = await fetch('http://127.0.0.1:5000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: params
        });

        const data = await response.json();
        if (data.error) {
          alert(data.error);
          return;
        }

        alert('注册成功，请登录');
        this.switchToLogin();
      } catch (err) {
        alert('注册失败: ' + err.message);
      }
    },
    startEditing() {
      this.editing = true;
      this.editUsername = this.user.username;
      this.showPasswordFields = false;
    },
    cancelEditing() {
      this.editing = false;
      this.newPassword = '';
      this.newPasswordConfirm = '';
    },
    startEditing() {
      this.editing = true;
      this.editUsername = this.user.username;
      this.showPasswordFields = false;
    },
    async saveProfile() {
      // 验证用户名
      if (!this.editUsername) {
        this.$notify.error({ title: '错误', message: '用户名不能为空' });
        return;
      }

      // 如果有密码修改，验证密码
      if (this.showPasswordFields) {
        if (!this.currentPassword) {
          this.$notify.error({ title: '错误', message: '请输入当前密码' });
          return;
        }

        if (this.newPassword !== this.newPasswordConfirm) {
          this.$notify.error({ title: '错误', message: '两次输入的新密码不一致' });
          return;
        }
      }

      try {
        const updateData = {
          user_id: this.user.id,
          username: this.editUsername
        };

        // 如果有密码修改，添加密码字段
        if (this.showPasswordFields) {
          updateData.current_password = this.currentPassword;
          updateData.new_password = this.newPassword;
        }

        const response = await fetch('http://127.0.0.1:5000/user/update', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updateData)
        });

        const data = await response.json();
        if (data.error) {
          this.$notify.error({ title: '错误', message: data.error });
          return;
        }

        // 更新本地存储的用户信息
        this.user.username = this.editUsername;
        localStorage.setItem('user', JSON.stringify(this.user));

        this.$notify.success({ title: '成功', message: '资料更新成功' });

        this.editing = false;
        this.currentPassword = '';
        this.newPassword = '';
        this.newPasswordConfirm = '';
      } catch (err) {
        this.$notify.error({ title: '错误', message: '更新失败: ' + err.message });
      }
    },
    triggerAvatarUpload() {
      document.getElementById('avatar-upload').click();
    },
    async handleAvatarUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      if (!file.type.match('image.*')) {
        alert('请选择图片文件');
        return;
      }

      const formData = new FormData();
      formData.append('avatar', file);
      formData.append('user_id', this.user.id);

      try {
        const response = await fetch('http://127.0.0.1:5000/user/avatar', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        if (data.error) {
          alert(data.error);
          return;
        }

        this.user.avatar = data.avatar_url + '?t=' + Date.now();
        localStorage.setItem('user', JSON.stringify(this.user));
        alert('头像更新成功');
      } catch (err) {
        alert('头像上传失败: ' + err.message);
      }
    },
    handleLogout() {
      localStorage.removeItem('user');
      this.user = null;
      this.showLogin = true;
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.profile-page {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
}

/* 卡片样式 */
.auth-card, .profile-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
  margin-bottom: 20px;
}

/* 表单样式 */
.auth-title {
  color: #333;
  text-align: center;
  margin-bottom: 20px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #1890ff;
  outline: none;
}

/* 按钮样式 */
.primary-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  margin-top: 10px;
}

.primary-btn:hover {
  background-color: #40a9ff;
}

.secondary-btn {
  background-color: #fff;
  color: #1890ff;
  border: 1px solid #1890ff;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.secondary-btn:hover {
  background-color: #e6f7ff;
}

.danger-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.danger-btn:hover {
  background-color: #ff7875;
}

/* 切换链接样式 */
.switch-text {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.switch-link {
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.switch-link:hover {
  text-decoration: underline;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #1890ff;
  margin-bottom: 15px;
}

/* 信息区域 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item label {
  font-weight: bold;
  color: #666;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: center;
}

/* 图标样式 */
.icon-upload, .icon-edit, .icon-save, .icon-cancel, .icon-logout {
  margin-right: 5px;
}
</style>
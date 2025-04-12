<template>
  <div class="profile-page">
    <h1>个人信息</h1>

    <!-- 未登录状态 -->
    <div v-if="!user" class="auth-forms">
      <div v-if="showLogin" class="auth-form">
        <h2>登录</h2>
        <input v-model="loginUsername" placeholder="用户名">
        <input v-model="loginPassword" type="password" placeholder="密码">
        <button @click="handleLogin">登录</button>
        <p class="switch-text">没有账号？<a @click="switchToRegister">注册新账号</a></p>
      </div>

      <div v-else class="auth-form">
        <h2>注册</h2>
        <input v-model="registerUsername" placeholder="用户名">
        <input v-model="registerPassword" type="password" placeholder="密码">
        <input v-model="registerPasswordConfirm" type="password" placeholder="确认密码">
        <button @click="handleRegister">注册</button>
        <p class="switch-text">已有账号？<a @click="switchToLogin">返回登录</a></p>
      </div>
    </div>

    <!-- 已登录状态 -->
    <div v-else class="user-info">
      <div class="avatar-section">
        <img :src="user.avatar || '/default_avatar.png'" class="avatar">
        <input type="file" id="avatar-upload" accept="image/*" @change="handleAvatarUpload" style="display: none;">
        <button @click="triggerAvatarUpload" class="upload-btn">更换头像</button>
      </div>

      <div class="info-section">
        <div class="info-item">
          <label>用户名:</label>
          <input v-if="editing" v-model="editUsername">
          <span v-else>{{ user.username }}</span>
        </div>

        <div v-if="showPasswordFields" class="info-item">
          <label>新密码:</label>
          <input v-model="newPassword" type="password" placeholder="留空则不修改">
        </div>

        <div v-if="showPasswordFields" class="info-item">
          <label>确认密码:</label>
          <input v-model="newPasswordConfirm" type="password">
        </div>

        <div class="action-buttons">
          <button v-if="!editing" @click="startEditing" class="edit-btn">编辑资料</button>
          <template v-else>
            <button @click="saveProfile" class="save-btn">保存修改</button>
            <button @click="cancelEditing" class="cancel-btn">取消</button>
          </template>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
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
    async saveProfile() {
      // 验证用户名
      if (!this.editUsername) {
        alert('用户名不能为空');
        return;
      }

      // 验证密码
      if (this.newPassword && this.newPassword !== this.newPasswordConfirm) {
        alert('两次输入的密码不一致');
        return;
      }

      try {
        const updateData = {
          user_id: this.user.id,
          username: this.editUsername
        };

        if (this.newPassword) {
          updateData.password = this.newPassword;
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
          alert(data.error);
          return;
        }

        this.user.username = this.editUsername;
        localStorage.setItem('user', JSON.stringify(this.user));
        this.editing = false;
        this.newPassword = '';
        this.newPasswordConfirm = '';
        alert('资料更新成功');
      } catch (err) {
        alert('更新失败: ' + err.message);
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
.profile-page {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.auth-forms {
  display: flex;
  justify-content: center;
}

.auth-form {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.switch-text {
  margin-top: 15px;
  text-align: center;
}

.switch-text a {
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.switch-text a:hover {
  text-decoration: underline;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #1890ff;
}

.upload-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

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
}

.info-item input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.info-item input:disabled {
  background-color: #f5f5f5;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.edit-btn,
.save-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn {
  padding: 8px 16px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  opacity: 0.9;
}
</style>
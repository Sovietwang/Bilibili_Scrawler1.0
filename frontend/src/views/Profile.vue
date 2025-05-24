<template>
  <div class="profile-page">
    <h1 class="page-title">个人信息</h1>

    <!-- 未登录状态保持不变 -->
    <div v-if="!user" class="auth-container">
      <div class="auth-card">
        <div v-if="showLogin" class="auth-form">
          <h2 class="auth-title">用户登录</h2>
          <div class="form-group">
            <label>登录角色</label>
            <select v-model="loginRole" class="form-input">
              <option value="user">普通用户</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label>用户名</label>
            <input v-model="loginUsername" class="form-input">
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="loginPassword" type="password" class="form-input">
          </div>
          <button @click="handleLogin" class="primary-btn">登录</button>
          <p class="switch-text">
            没有账号？<a @click="switchToRegister" class="switch-link">注册新账号</a>
          </p>
        </div>

        <!-- 修改注册表单 -->
        <div v-else class="auth-form">
          <h2 class="auth-title">用户注册</h2>
          <div class="form-group">
            <label>用户名</label>
            <input v-model="registerUsername" class="form-input">
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="registerPassword" type="password" class="form-input">
          </div>
          <div class="form-group">
            <label>确认密码</label>
            <input v-model="registerPasswordConfirm" type="password" class="form-input">
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
        <!-- 头像上传部分 -->
        <div class="avatar-section">
          <img :src="user.avatar || '/default_avatar.png'" class="avatar">
          <input type="file" id="avatar-upload" accept="image/*" @change="handleAvatarUpload" style="display: none;">
          <button @click="triggerAvatarUpload" class="upload-btn">
            <i class="icon-upload"></i> 更换头像
          </button>
          <p v-if="avatarError" class="error-message">{{ avatarError }}</p>
        </div>

        <!-- 基本信息部分 -->
        <div class="info-section">
          <div class="info-item">
            <label>用户名</label>
            <input v-if="editingUsername" v-model="editUsername" class="form-input" placeholder="请输入新用户名">
            <span v-else>{{ user.username }}</span>
          </div>

          <!-- 密码修改部分 -->
          <div v-if="editingPassword" class="password-form">
            <div class="info-item">
              <label>当前密码</label>
              <input v-model="currentPassword" type="password" placeholder="请输入当前密码" class="form-input">
            </div>
            <div class="info-item">
              <label>新密码</label>
              <input v-model="newPassword" type="password" placeholder="请输入新密码" class="form-input"
                @input="checkPasswordStrength">
              <div class="password-strength" v-if="newPassword">
                密码强度: <span :class="strengthClass">{{ passwordStrength }}</span>
              </div>
            </div>
            <div class="info-item">
              <label>确认新密码</label>
              <input v-model="newPasswordConfirm" type="password" placeholder="请再次输入新密码" class="form-input">
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <!-- 非编辑状态下显示编辑按钮 -->
            <template v-if="!editingUsername && !editingPassword">
              <button @click="startEditing('username')" class="edit-btn">
                <i class="icon-edit"></i> 编辑用户名
              </button>
              <button @click="startEditing('password')" class="edit-btn">
                <i class="icon-lock"></i> 修改密码
              </button>
              <button @click="handleLogout" class="logout-btn">
                <i class="icon-logout"></i> 退出登录
              </button>
            </template>

            <!-- 用户名编辑状态下显示保存/取消按钮 -->
            <template v-if="editingUsername">
              <button @click="saveUsername" class="save-btn">
                <i class="icon-save"></i> 保存用户名
              </button>
              <button @click="cancelEditing" class="cancel-btn">
                <i class="icon-cancel"></i> 取消
              </button>
            </template>

            <!-- 密码编辑状态下显示保存/取消按钮 -->
            <template v-if="editingPassword">
              <button @click="savePassword" class="save-btn">
                <i class="icon-save"></i> 保存密码
              </button>
              <button @click="cancelEditing" class="cancel-btn">
                <i class="icon-cancel"></i> 取消
              </button>
            </template>
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
      showPasswordFields: false,
      loginRole: 'user',
      editingUsername: false,
      editingPassword: false,
      passwordStrength: '弱',
      strengthClass: 'weak',
      avatarError: null
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
        this.$notify.error({ title: '错误', message: '请输入用户名和密码' });
        return;
      }

      try {
        const params = new URLSearchParams();
        params.append('username', this.loginUsername);
        params.append('password', this.loginPassword);
        params.append('role', this.loginRole); // 添加角色参数

        const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: params
        });

        const data = await response.json();
        if (data.error) {
          this.$notify.error({ title: '错误', message: data.error });
          return;
        }

        this.user = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));

        // 如果是管理员，跳转到管理员界面
        if (this.user.role === 'admin') {
          this.$router.push('/admin');
        }
      } catch (err) {
        this.$notify.error({ title: '错误', message: '登录失败: ' + err.message });
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

    startEditing(type) {
      // 先取消所有编辑状态
      this.cancelEditing();

      // 设置新的编辑状态
      if (type === 'username') {
        this.editingUsername = true;
        this.editUsername = this.user.username;
      } else if (type === 'password') {
        this.editingPassword = true;
      }
    },

    cancelEditing() {
      this.editingUsername = false;
      this.editingPassword = false;
      this.clearForm();
    },

    clearForm() {
      this.editUsername = '';
      this.currentPassword = '';
      this.newPassword = '';
      this.newPasswordConfirm = '';
      this.avatarError = null;
    },

    checkPasswordStrength() {
      if (!this.newPassword) {
        this.passwordStrength = '弱';
        this.strengthClass = 'weak';
        return;
      }

      // 简单密码强度检测
      const hasNumber = /\d/.test(this.newPassword);
      const hasLetter = /[a-zA-Z]/.test(this.newPassword);
      const hasSpecial = /[^a-zA-Z0-9]/.test(this.newPassword);
      const isLong = this.newPassword.length >= 8;

      if (isLong && hasNumber && hasLetter && hasSpecial) {
        this.passwordStrength = '强';
        this.strengthClass = 'strong';
      } else if (isLong && (hasNumber || hasLetter)) {
        this.passwordStrength = '中';
        this.strengthClass = 'medium';
      } else {
        this.passwordStrength = '弱';
        this.strengthClass = 'weak';
      }
    },

    async saveUsername() {
      if (!this.editUsername) {
        this.$notify.error({ title: '错误', message: '用户名不能为空' });
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:5000/user/update', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: this.user.id,
            username: this.editUsername
          })
        });

        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }

        this.user.username = this.editUsername;
        localStorage.setItem('user', JSON.stringify(this.user));
        this.editingUsername = false;

        this.$notify.success({
          title: '成功',
          message: '用户名修改成功'
        });
      } catch (err) {
        this.$notify.error({
          title: '错误',
          message: '更新失败: ' + err.message
        });
      }
    },

    async savePassword() {
      if (!this.currentPassword) {
        this.$notify.error({ title: '错误', message: '请输入当前密码' });
        return;
      }

      if (!this.newPassword) {
        this.$notify.error({ title: '错误', message: '请输入新密码' });
        return;
      }

      if (this.newPassword !== this.newPasswordConfirm) {
        this.$notify.error({ title: '错误', message: '两次输入的新密码不一致' });
        return;
      }

      // 再次检查密码强度
      this.checkPasswordStrength();
      if (this.passwordStrength === '弱') {
        this.$notify.error({ title: '错误', message: '密码强度太弱，请使用更复杂的密码' });
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:5000/user/update', {  // 修改为正确的API端点
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: this.user.id,
            current_password: this.currentPassword,
            new_password: this.newPassword
          })
        });

        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }

        this.editingPassword = false;
        this.clearForm();

        this.$notify.success({
          title: '成功',
          message: '密码修改成功'
        });
      } catch (err) {
        this.$notify.error({
          title: '错误',
          message: '密码修改失败: ' + err.message
        });
      }
    },

    triggerAvatarUpload() {
      document.getElementById('avatar-upload').click();
    },

    async handleAvatarUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      // 验证文件类型
      if (!file.type.match('image.*')) {
        this.avatarError = '请选择有效的图片文件 (JPEG, PNG, GIF)';
        return;
      }

      // 验证文件大小 (限制2MB)
      if (file.size > 2 * 1024 * 1024) {
        this.avatarError = '图片大小不能超过2MB';
        return;
      }

      this.avatarError = null;

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
          throw new Error(data.error);
        }

        // 更新头像并添加时间戳防止缓存
        this.user.avatar = data.avatar_url + '?t=' + Date.now();
        localStorage.setItem('user', JSON.stringify(this.user));

        this.$notify.success({
          title: '成功',
          message: '头像更新成功'
        });
      } catch (err) {
        this.avatarError = '头像上传失败: ' + err.message;
      }
    },

    handleLogout() {
      localStorage.removeItem('user');
      this.user = null;
      this.showLogin = true;
      this.$notify.success({
        title: '成功',
        message: '您已成功退出登录'
      });
    }
  }
}
</script>

<style scoped>
/* 基础页面样式 - 与其他页面统一 */
.profile-page {
  font-family: Arial, sans-serif;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  box-sizing: border-box;
}

.page-title {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
}

/* 卡片样式 - 与History和Crawler统一 */
.profile-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 25px;
  margin-bottom: 20px;
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
  font-size: 14px;
}

/* 表单输入 - 与其他页面统一 */
.form-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-input:focus {
  border-color: #1890ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 密码表单区域 */
.password-form {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.password-strength {
  margin-top: 5px;
  font-size: 12px;
}

.password-strength .weak {
  color: #ff4d4f;
}

.password-strength .medium {
  color: #faad14;
}

.password-strength .strong {
  color: #52c41a;
}

.error-message {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 5px;
  text-align: center;
}

/* 按钮样式 - 与其他页面统一 */
button {
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-weight: 500;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-btn {
  background-color: #1890ff;
  color: white;
}

.upload-btn:hover {
  background-color: #40a9ff;
}

.edit-btn {
  background-color: #1890ff;
  color: white;
}

.edit-btn:hover {
  background-color: #40a9ff;
}

.save-btn {
  background-color: #52c41a;
  color: white;
}

.save-btn:hover {
  background-color: #73d13d;
}

.cancel-btn {
  background-color: #faad14;
  color: white;
}

.cancel-btn:hover {
  background-color: #ffc53d;
}

.logout-btn {
  background-color: #ff4d4f;
  color: white;
}

.logout-btn:hover {
  background-color: #ff7875;
}

/* 操作按钮组 - 与其他页面统一 */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.action-buttons button {
  flex: 1;
  min-width: 120px;
}

/* 图标样式 */
.icon-upload,
.icon-edit,
.icon-save,
.icon-cancel,
.icon-logout {
  margin-right: 5px;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .profile-card {
    padding: 15px;
  }

  .action-buttons button {
    min-width: 100%;
  }
}
</style>
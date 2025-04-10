<template>
  <div class="profile-page">
    <h1>个人信息</h1>
    
    <!-- 未登录状态 -->
    <div v-if="!user" class="auth-forms">
      <div class="login-form">
        <h2>登录</h2>
        <input v-model="loginUsername" placeholder="用户名">
        <input v-model="loginPassword" type="password" placeholder="密码">
        <button @click="handleLogin">登录</button>
      </div>
      
      <div class="register-form">
        <h2>注册</h2>
        <input v-model="registerUsername" placeholder="用户名">
        <input v-model="registerPassword" type="password" placeholder="密码">
        <button @click="handleRegister">注册</button>
      </div>
    </div>
    
    <!-- 已登录状态 -->
    <div v-else class="user-info">
      <img :src="user.avatar || 'default_avatar.png'" class="avatar">
      <h2>{{ user.username }}</h2>
      <button @click="handleLogout">退出登录</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || null,
      loginUsername: '',
      loginPassword: '',
      registerUsername: '',
      registerPassword: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `username=${this.loginUsername}&password=${this.loginPassword}`
        });
        
        const data = await response.json();
        if (data.error) {
          alert(data.error);
          return;
        }
        
        this.user = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));
        alert('登录成功');
      } catch (err) {
        alert('登录失败: ' + err.message);
      }
    },
    
    async handleRegister() {
      try {
        const response = await fetch('http://127.0.0.1:5000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `username=${this.registerUsername}&password=${this.registerPassword}`
        });
        
        const data = await response.json();
        if (data.error) {
          alert(data.error);
          return;
        }
        
        alert('注册成功，请登录');
        this.registerUsername = '';
        this.registerPassword = '';
      } catch (err) {
        alert('注册失败: ' + err.message);
      }
    },
    
    handleLogout() {
      localStorage.removeItem('user');
      this.user = null;
      alert('已退出登录');
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
  gap: 20px;
}

.login-form, .register-form {
  flex: 1;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

input {
  display: block;
  width: 100%;
  padding: 8px;
  margin: 10px 0;
  box-sizing: border-box;
}

button {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.user-info {
  text-align: center;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 20px;
}
</style>
<template>
  <div id="app">
    <!-- 路由视图 -->
    <keep-alive>
      <router-view style="max-width: 600px; width: 100%;"></router-view>
    </keep-alive>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <router-link to="/crawler" class="nav-item">数据爬取</router-link>
      <router-link to="/history" class="nav-item">历史记录</router-link>
      <router-link to="/profile" class="nav-item">个人信息</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "App",
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user'));
    }
  }
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 100%; /* 确保 app 容器宽度不受限制 */
  min-width: 600px; /* 确保最小宽度为 600px */
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 80px; /* 为底部导航栏留出空间 */
  display: flex;
  flex-direction: column;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #f8f9fa;
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
  border-top: 1px solid #ddd;
  max-width: 600px;
  margin: 0 auto;
}

.nav-item {
  text-decoration: none;
  color: #333;
  font-size: 16px;
}

.nav-item.router-link-exact-active {
  color: #007bff;
  font-weight: bold;
}
</style>
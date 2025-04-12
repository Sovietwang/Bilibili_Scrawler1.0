# Bilibili_Scrawler1.0

- # B站视频信息爬虫系统

  ![Python](https://img.shields.io/badge/Python-3.9+-blue)
  ![Flask](https://img.shields.io/badge/Flask-2.0+-green)
  ![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen)
  ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
  ![Docker](https://img.shields.io/badge/Docker-✔-success)

  一个完整的B站视频信息查询系统，包含前后端分离架构、数据持久化和Docker化部署方案。

  ## ✨ 功能特性

  - **视频信息查询**：通过BV号或视频链接获取详细信息
  - **数据持久化**：自动保存查询历史记录
  - **响应式前端**：适配桌面和移动端设备
  - **RESTful API**：标准化接口设计
  - **容器化部署**：支持Docker一键部署

  ## 🛠️ 技术栈

  ### 后端服务
  | 技术     | 用途       | 版本  |
  | -------- | ---------- | ----- |
  | Python   | 核心语言   | 3.9+  |
  | Flask    | Web框架    | 2.0+  |
  | Requests | HTTP请求库 | 2.26+ |
  | PyMySQL  | MySQL连接  | 1.0+  |

  ### 前端界面
  | 技术         | 用途       | 版本  |
  | ------------ | ---------- | ----- |
  | Vue.js       | 前端框架   | 3.x   |
  | Axios        | HTTP客户端 | 0.21+ |
  | Element Plus | UI组件库   | 2.x   |

  ### 数据存储
  | 技术  | 用途         | 版本 |
  | ----- | ------------ | ---- |
  | MySQL | 关系型数据库 | 8.0  |
  | Redis | 缓存(可选)   | 6.x  |

  ### 基础设施
  | 技术           | 用途        |
  | -------------- | ----------- |
  | Docker         | 容器化      |
  | Nginx          | 反向代理    |
  | GitHub Actions | CI/CD(可选) |

  ## 🚀 快速部署

  ### 开发环境
  
  ```bash
  # 克隆项目
  git clone https://github.com/yourname/bilibili-crawler.git
  cd bilibili-crawler
  
  # 后端依赖
  pip install -r backend/requirements.txt
  
  # 前端依赖
  cd frontend
  npm install
  

###      线上预览

​      项目github地址 [Sovietwang/Bilibili_Scrawler1.0](https://github.com/Sovietwang/Bilibili_Scrawler1.0)

​       线上网站预览[B站助手](https://binqqing.fun/crawler)

## ⚖️ 法律合规声明

### 数据来源合法性
1. 所有数据均通过以下合法途径获取：
   - 网页公开可见数据（不绕过反爬措施）
2. 严格遵守：
   - 《网络安全法》第12、27条
   - 《数据安全法》第21-23条
   - 《个人信息保护法》第13条
   - 《中华人民共和国民法典》第1032条

### 使用限制
```diff
+ 允许行为：
  - 个人学习研究
  - 学术论文数据支撑（需注明来源）
  - 技术演示（需隐藏真实数据）

- 禁止行为：
  - 商业性使用（未获授权）
  - 大规模数据采集
  - 用户隐私数据存储
  
```

### 免责条款

使用者需知：

1. 本项目开发者不承担因滥用导致的任何法律责任
2. 禁止将本项目用于：
   - 流量作弊
   - 数据转售
   - 不正当竞争
3. 收到平台通知后将立即停止服务
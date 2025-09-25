# 🚀 专家评分系统 - 部署指南

## 🌟 项目简介

这是一个专业的AI假设专家评分系统，支持：
- **多主题假设比较**：11个不同研究主题
- **成对比较评分**：科学的比较评估方法
- **多维度评分**：创新性、重要性、合理性、可行性、整体胜出
- **中英文切换**：支持中英文内容显示
- **进度跟踪**：实时显示评分进度
- **数据持久化**：评分结果自动保存

## 🎯 部署平台选择

### ✅ Railway（推荐）
- **免费额度**：每月$5免费额度
- **自动部署**：连接GitHub后自动部署
- **性能优秀**：基于AWS基础设施
- **简单易用**：配置简单，一键部署
- **SSL证书**：自动HTTPS支持

### ✅ Render
- **免费计划**：支持静态网站和Web服务
- **自动部署**：GitHub集成
- **性能稳定**：可靠的基础设施

## 🚀 Railway部署步骤

### 1. 准备项目文件

确保项目包含以下文件：
```
hypothesis_expert_rating_system/
├── app.py                    # Flask主应用
├── requirements.txt          # Python依赖
├── Procfile                 # Railway启动配置
├── hypothesis_data.db        # SQLite数据库
├── templates/               # HTML模板
│   ├── index.html
│   ├── rate_topic.html
│   └── thank_you.html
├── static/                  # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── README_DEPLOYMENT.md     # 本文件
```

### 2. 创建GitHub仓库

```bash
# 初始化Git仓库
cd hypothesis_expert_rating_system
git init
git add .
git commit -m "Initial commit: Expert Rating System"
git branch -M main

# 创建GitHub仓库并推送
# 在GitHub上创建新仓库，然后：
git remote add origin https://github.com/YOUR_USERNAME/hypothesis_expert_rating_system.git
git push -u origin main
```

### 3. 部署到Railway

#### 方法1：通过Railway Dashboard

1. 访问 [Railway.app](https://railway.app)
2. 使用GitHub账号登录
3. 点击"New Project"
4. 选择"Deploy from GitHub repo"
5. 选择 `hypothesis_expert_rating_system` 仓库
6. 等待部署完成

#### 方法2：通过Railway CLI

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up
```

### 4. 配置环境变量

在Railway Dashboard中设置：

```
PORT=8080
HOST=0.0.0.0
DEBUG=False
```

### 5. 获取部署URL

部署完成后，Railway会提供一个公网URL，例如：
`https://hypothesis-expert-rating-system-production.up.railway.app`

## 🔧 本地开发

### 启动应用

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

### 访问应用

打开浏览器访问：http://localhost:5001

## 📊 功能演示

### 1. 主页功能
- 11个研究主题展示
- 每个主题的描述和欢迎信息
- 点击进入评分页面

### 2. 评分功能
- 成对假设比较
- 5个维度的评分
- 进度条显示
- 中英文切换

### 3. 数据管理
- 评分结果自动保存
- 会话状态管理
- 数据统计和导出

## 🎨 界面特性

### 响应式设计
- 支持桌面、平板、手机
- 自适应布局
- 现代化UI设计

### 交互体验
- 实时进度跟踪
- 平滑动画效果
- 用户友好的反馈

## 🚨 注意事项

### 数据库
- 确保数据库文件存在
- 检查表结构完整性
- 定期备份数据

### 性能优化
- 使用数据库索引
- 实现会话管理
- 优化静态文件加载

### 安全考虑
- 输入验证
- SQL注入防护
- 会话安全

## 🔍 故障排除

### 常见问题

1. **应用无法启动**
   - 检查依赖是否安装
   - 验证数据库文件
   - 查看Railway日志

2. **数据库连接失败**
   - 检查数据库文件权限
   - 验证表结构
   - 确认SQLite版本

3. **页面显示异常**
   - 检查浏览器控制台
   - 验证静态文件路径
   - 确认JavaScript语法

### 调试技巧

```python
# 启用调试模式
DEBUG=True

# 查看Railway日志
railway logs
```

## 📈 性能监控

### Railway监控
- 访问Railway Dashboard
- 查看应用性能指标
- 监控资源使用情况

### 应用监控
- 响应时间统计
- 错误率监控
- 用户行为分析

## 🔄 更新部署

### 自动部署
- 推送代码到GitHub
- Railway自动检测更新
- 自动重新部署

### 手动部署
```bash
# 重新部署
railway up

# 查看部署状态
railway status

# 查看日志
railway logs
```

## 🌟 扩展功能

### 未来计划
- 用户认证系统
- 批量评分功能
- 高级数据分析
- 移动端优化

### 贡献指南
- Fork项目
- 创建功能分支
- 提交Pull Request
- 代码审查

## 📞 技术支持

### 联系方式
- GitHub Issues
- 项目Wiki
- 开发者社区

### 资源链接
- [Railway官方文档](https://docs.railway.app)
- [Flask官方文档](https://flask.palletsprojects.com)
- [Bootstrap文档](https://getbootstrap.com/docs)

---

**🎉 恭喜！你的专家评分系统已经成功部署到Railway！**

现在你可以：
- 分享链接给专家进行评分
- 在任何设备上访问
- 享受高性能的云服务
- 专注于功能开发和优化

**🚀 开始你的专家评分之旅吧！**

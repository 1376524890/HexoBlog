# 股票交易模拟系统 - Vue 3 前端

## 🎉 项目已成功创建！

这是一个完整的基于 Vue 3 的股票交易模拟系统前端，包含以下功能：

### ✨ 主要功能模块

1. **概览页** - 系统总览、持仓概览、分析摘要、最新交易和资讯
2. **持仓管理** - 完整持仓列表、多维度排序、资产配置可视化
3. **K 线图表** - 实时价格走势、成交量分析、持仓分布、技术指标
4. **投资分析** - 性能指标、AI 投资建议、市场情绪、风险评估
5. **新闻摘要** - 实时财经新闻、情绪分类、多维度筛选
6. **交易记录** - 完整交易流水、费用汇总、统计分析

### 📂 项目结构

```
stock-frontend/
├── src/
│   ├── assets/           # 静态资源
│   ├── components/       # 可复用组件
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态管理
│   │   └── stock.ts     # 股票数据 store
│   ├── views/           # 页面组件
│   │   ├── Overview.vue # 概览页
│   │   ├── Portfolio.vue # 持仓页
│   │   ├── Charts.vue   # 图表页
│   │   ├── Analysis.vue # 分析页
│   │   ├── News.vue     # 新闻页
│   │   └── Transactions.vue # 交易记录页
│   ├── App.vue          # 根组件
│   ├── main.ts          # 入口文件
│   └── style.css        # 全局样式
├── dist/                # 生产构建输出
├── public/              # 静态资源
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

### 🚀 运行方式

```bash
# 安装依赖
cd stock-frontend
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览生产版本
npm run preview
```

### 🛠️ 技术栈

- Vue 3 (Composition API)
- TypeScript
- Vite
- Tailwind CSS
- Pinia
- Vue Router 4
- Chart.js
- Vue-Chart.js

### 📊 数据源

当前使用模拟数据，可以通过以下方式接入真实后端：

1. 修改 `src/stores/stock.ts` 中的 `useStockStore`
2. 使用 axios 调用真实 API
3. 实时更新数据

### 🎨 设计特点

- 深色主题（Dark Mode）
- 响应式布局
- 现代化渐变色卡片
- 流畅动画效果
- 专业交易界面风格

## ✅ 构建完成

生产构建已成功生成在 `dist/` 目录，可以通过 `npm run preview` 预览。

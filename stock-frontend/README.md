# 股票交易模拟系统 - Vue 3 前端

## 📋 项目概述

这是一个基于 Vue 3 的现代股票交易模拟系统前端界面，提供完整的交易数据分析、持仓管理和市场资讯功能。

## ✨ 主要功能

### 1. 概览页 (`/`)
- 总权益、可用资金、总盈亏等核心指标
- 持仓概览（前 5 只股票）
- 系统分析摘要
- 最近交易记录
- 最新资讯推送

### 2. 持仓管理 (`/portfolio`)
- 完整的持仓列表
- 多维度排序（市值、盈亏、涨幅）
- 资产配置可视化
- 个股表现分析

### 3. K 线图表 (`/charts`)
- 实时价格走势图表
- 成交量分析
- 持仓分布饼图
- 技术指标展示

### 4. 投资分析 (`/analysis`)
- 性能指标展示（夏普比率、最大回撤等）
- AI 投资建议
- 市场情绪分析
- 风险评估报告

### 5. 新闻摘要 (`/news`)
- 实时财经新闻
- 情绪分类（利好/中性/利空）
- 多维度筛选和搜索
- 相关股票关联

### 6. 交易记录 (`/transactions`)
- 完整的交易流水
- 买入/卖出统计
- 费用汇总
- CSV 导出功能

## 🛠️ 技术栈

- **Vue 3** - Composition API
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Tailwind CSS** - 现代化样式
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **Chart.js** - 图表可视化
- **@heroicons/vue** - 图标库

## 🚀 快速开始

### 1. 安装依赖
```bash
cd stock-frontend
npm install
```

### 2. 开发模式
```bash
npm run dev
```
项目将在 `http://localhost:3000` 启动

### 3. 构建生产版本
```bash
npm run build
```

### 4. 预览生产版本
```bash
npm run preview
```

## 📁 项目结构

```
stock-frontend/
├── public/                 # 静态资源
├── src/
│   ├── assets/            # 图片、字体等资源
│   ├── components/        # 可复用组件
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # Pinia 状态管理
│   │   └── stock.ts
│   ├── views/            # 页面组件
│   │   ├── Overview.vue
│   │   ├── Portfolio.vue
│   │   ├── Charts.vue
│   │   ├── Analysis.vue
│   │   ├── News.vue
│   │   └── Transactions.vue
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   └── style.css         # 全局样式
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## 🎨 设计特点

- **深色主题**：专业交易界面风格
- **响应式布局**：适配桌面和移动端
- **渐变色卡片**：现代化 UI 设计
- **流畅动画**：平滑过渡效果
- **实时数据**：支持实时更新

## 🔧 自定义配置

### API 端点配置
在 `vite.config.ts` 中修改代理配置：
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

### 主题色配置
在 `tailwind.config.js` 中自定义颜色：
```javascript
colors: {
  primary: { ... },
  success: { ... },
  danger: { ... }
}
```

## 📊 数据模拟

当前使用静态数据模拟，如需接入真实后端：

1. 在 `src/stores/stock.ts` 中替换 mock 数据为 API 调用
2. 使用 axios 获取实时数据
3. 更新组件以支持动态数据

示例：
```typescript
import axios from 'axios'

export const useStockStore = defineStore('stock', () => {
  const holdings = ref<Holding[]>([])
  
  const fetchHoldings = async () => {
    const response = await axios.get('/api/portfolio')
    holdings.value = response.data
  }
  
  onMounted(() => {
    fetchHoldings()
  })
  
  return { holdings }
})
```

## 🔐 环境变量

创建 `.env` 文件：
```env
VITE_API_BASE_URL=http://localhost:8080/api
```

## 📝 开发说明

- 所有新组件应使用 Composition API
- 使用 TypeScript 提供类型安全
- 遵循 Tailwind CSS Utility-first 原则
- 保持组件单一职责
- 添加适当的错误处理

## 🐛 已知限制

- 当前为演示版本，数据为静态
- K 线图使用模拟数据
- 需要接入真实后端 API 才能完全使用

## 📄 许可证

MIT License

---

## 维护说明

此项目已集成到 OpenClaw 系统中，可作为：
1. 股票交易系统的可视化前端
2. 展示 Vue 3 和现代化前端开发技术
3. 交易数据分析的平台

建议定期更新依赖，保持安全性。

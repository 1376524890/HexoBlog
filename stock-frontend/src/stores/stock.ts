import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Stock {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap: string
}

export interface Holding {
  symbol: string
  name: string
  shares: number
  avgPrice: number
  currentPrice: number
  marketValue: number
  costBasis: number
  gainLoss: number
  gainLossPercent: number
}

export interface Transaction {
  id: string
  symbol: string
  type: 'buy' | 'sell'
  shares: number
  price: number
  total: number
  timestamp: Date
  fees: number
}

export interface MarketNews {
  id: string
  title: string
  summary: string
  source: string
  timestamp: Date
  sentiment: 'positive' | 'negative' | 'neutral'
  relatedSymbols: string[]
}

export interface SystemStats {
  totalEquity: number
  cash: number
  invested: number
  dayGain: number
  dayGainPercent: number
  totalGain: number
  totalGainPercent: number
  winRate: number
  totalTrades: number
}

export const useStockStore = defineStore('stock', () => {
  // System Stats
  const stats = ref<SystemStats>({
    totalEquity: 1000000,
    cash: 450000,
    invested: 550000,
    dayGain: 12500,
    dayGainPercent: 1.25,
    totalGain: 85000,
    totalGainPercent: 9.5,
    winRate: 68.5,
    totalTrades: 127
  })

  // Holdings
  const holdings = ref<Holding[]>([
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      shares: 500,
      avgPrice: 175.50,
      currentPrice: 182.30,
      marketValue: 91150,
      costBasis: 87750,
      gainLoss: 3400,
      gainLossPercent: 3.87
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      shares: 300,
      avgPrice: 380.20,
      currentPrice: 395.80,
      marketValue: 118740,
      costBasis: 114060,
      gainLoss: 4680,
      gainLossPercent: 4.10
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      shares: 200,
      avgPrice: 140.30,
      currentPrice: 145.60,
      marketValue: 29120,
      costBasis: 28060,
      gainLoss: 1060,
      gainLossPercent: 3.78
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      shares: 150,
      avgPrice: 245.80,
      currentPrice: 238.50,
      marketValue: 35775,
      costBasis: 36870,
      gainLoss: -1095,
      gainLossPercent: -2.97
    },
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      shares: 100,
      avgPrice: 875.30,
      currentPrice: 920.10,
      marketValue: 92010,
      costBasis: 87530,
      gainLoss: 4480,
      gainLossPercent: 5.12
    }
  ])

  // Transactions
  const transactions = ref<Transaction[]>([
    {
      id: 'TXN001',
      symbol: 'AAPL',
      type: 'buy',
      shares: 200,
      price: 175.50,
      total: 35100,
      timestamp: new Date('2026-03-15T10:30:00'),
      fees: 5
    },
    {
      id: 'TXN002',
      symbol: 'MSFT',
      type: 'buy',
      shares: 150,
      price: 380.20,
      total: 57030,
      timestamp: new Date('2026-03-14T14:20:00'),
      fees: 5
    },
    {
      id: 'TXN003',
      symbol: 'NVDA',
      type: 'buy',
      shares: 100,
      price: 875.30,
      total: 87530,
      timestamp: new Date('2026-03-13T11:15:00'),
      fees: 5
    },
    {
      id: 'TXN004',
      symbol: 'TSLA',
      type: 'buy',
      shares: 150,
      price: 245.80,
      total: 36870,
      timestamp: new Date('2026-03-12T09:45:00'),
      fees: 5
    },
    {
      id: 'TXN005',
      symbol: 'GOOGL',
      type: 'buy',
      shares: 200,
      price: 140.30,
      total: 28060,
      timestamp: new Date('2026-03-11T13:30:00'),
      fees: 5
    }
  ])

  // News
  const news = ref<MarketNews[]>([
    {
      id: 'NEWS001',
      title: '科技股继续走强，AI 概念备受追捧',
      summary: '主要科技股今日继续上涨，人工智能相关概念受到投资者热捧。市场分析师认为，AI 技术应用的持续拓展将为科技行业带来长期增长动力。',
      source: '财经日报',
      timestamp: new Date('2026-03-17T08:30:00'),
      sentiment: 'positive',
      relatedSymbols: ['AAPL', 'MSFT', 'GOOGL', 'NVDA']
    },
    {
      id: 'NEWS002',
      title: '特斯拉发布最新产能数据',
      summary: '特斯拉公布了最新的季度产能数据，虽然超出市场预期，但投资者对自动驾驶技术的进展仍存在疑虑。股价在盘中出现震荡。',
      source: '汽车财经',
      timestamp: new Date('2026-03-17T07:15:00'),
      sentiment: 'neutral',
      relatedSymbols: ['TSLA']
    },
    {
      id: 'NEWS003',
      title: '美联储利率决议即将公布',
      summary: '市场密切关注即将公布的美联储利率决议，投资者担心加息可能影响科技股估值。分析师建议保持谨慎乐观。',
      source: '华尔街见闻',
      timestamp: new Date('2026-03-16T16:00:00'),
      sentiment: 'negative',
      relatedSymbols: ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    },
    {
      id: 'NEWS004',
      title: '英伟达新芯片架构引发关注',
      summary: '英伟达宣布新一代 GPU 架构，性能提升显著，有望进一步巩固其在 AI 芯片市场的领先地位。股价随之上涨。',
      source: '科技日报',
      timestamp: new Date('2026-03-16T10:30:00'),
      sentiment: 'positive',
      relatedSymbols: ['NVDA']
    },
    {
      id: 'NEWS005',
      title: '苹果服务业务收入创新高',
      summary: '苹果公布最新财报，服务业务收入首次突破 200 亿美元大关，显示出公司生态系统的强大粘性和盈利能力。',
      source: '商业周刊',
      timestamp: new Date('2026-03-15T14:20:00'),
      sentiment: 'positive',
      relatedSymbols: ['AAPL']
    }
  ])

  // Computed
  const totalMarketValue = computed(() => 
    holdings.value.reduce((sum, h) => sum + h.marketValue, 0)
  )

  const totalGainLoss = computed(() => 
    holdings.value.reduce((sum, h) => sum + h.gainLoss, 0)
  )

  const totalGainLossPercent = computed(() => {
    const totalCost = holdings.value.reduce((sum, h) => sum + h.costBasis, 0)
    if (totalCost === 0) return 0
    return (totalGainLoss.value / totalCost) * 100
  })

  const topGainer = computed(() => {
    if (holdings.value.length === 0) return null
    return holdings.value.reduce((prev, current) => 
      current.gainLossPercent > prev.gainLossPercent ? current : prev
    )
  })

  const topLoser = computed(() => {
    if (holdings.value.length === 0) return null
    return holdings.value.reduce((prev, current) => 
      current.gainLossPercent < prev.gainLossPercent ? current : prev
    )
  })

  return {
    // State
    stats,
    holdings,
    transactions,
    news,
    
    // Computed
    totalMarketValue,
    totalGainLoss,
    totalGainLossPercent,
    topGainer,
    topLoser
  }
})

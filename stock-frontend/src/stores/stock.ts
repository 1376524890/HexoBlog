import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// API 基础地址
const API_BASE = '/api'

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
  // Loading states
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdate = ref<Date | null>(null)

  // System Stats
  const stats = ref<SystemStats>({
    totalEquity: 0,
    cash: 0,
    invested: 0,
    dayGain: 0,
    dayGainPercent: 0,
    totalGain: 0,
    totalGainPercent: 0,
    winRate: 0,
    totalTrades: 0
  })

  // Holdings
  const holdings = ref<Holding[]>([])

  // Transactions
  const transactions = ref<Transaction[]>([])

  // News
  const news = ref<MarketNews[]>([])

  // 股票名称映射 (A 股代码 -> 名称)
  const stockNames: Record<string, string> = {
    '601398.SS': '工商银行',
    '600519.SS': '贵州茅台',
    '000001.SZ': '平安银行',
    '600036.SS': '招商银行',
    '601318.SS': '中国平安',
    '000858.SZ': '五粮液',
    '600000.SS': '浦发银行',
    '601166.SS': '兴业银行',
    '600276.SS': '恒瑞医药',
    '000333.SZ': '美的集团'
  }

  // 获取股票名称
  const getStockName = (symbol: string): string => {
    return stockNames[symbol] || symbol
  }

  // Fetch portfolio summary
  const fetchSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE}/portfolio/summary`)
      const data = response.data

      stats.value = {
        totalEquity: data.total_equity || 0,
        cash: data.current_cash || 0,
        invested: data.total_market_value || 0,
        dayGain: 0, // 后端暂无此数据
        dayGainPercent: 0,
        totalGain: data.total_pnl || 0,
        totalGainPercent: data.total_pnl_pct || 0,
        winRate: data.win_rate || 0,
        totalTrades: data.total_trades || 0
      }
    } catch (e) {
      console.error('Failed to fetch summary:', e)
      throw e
    }
  }

  // Fetch holdings
  const fetchHoldings = async () => {
    try {
      const response = await axios.get(`${API_BASE}/portfolio/positions`)
      const data = response.data

      if (data.status === 'empty' || !data.positions) {
        holdings.value = []
        return
      }

      holdings.value = data.positions.map((pos: any) => ({
        symbol: pos.symbol,
        name: getStockName(pos.symbol),
        shares: pos.shares,
        avgPrice: pos.avg_price,
        currentPrice: pos.current_price,
        marketValue: pos.market_value,
        costBasis: pos.shares * pos.avg_price,
        gainLoss: pos.pnl,
        gainLossPercent: pos.pnl_pct
      }))
    } catch (e) {
      console.error('Failed to fetch holdings:', e)
      throw e
    }
  }

  // Fetch trade history
  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/trade/history`)
      const data = response.data

      if (!data.trades) {
        transactions.value = []
        return
      }

      transactions.value = data.trades.map((trade: any, index: number) => ({
        id: `TXN${String(index + 1).padStart(3, '0')}`,
        symbol: trade.symbol,
        type: trade.type as 'buy' | 'sell',
        shares: trade.shares,
        price: trade.price,
        total: trade.shares * trade.price,
        timestamp: new Date(trade.time),
        fees: 5 // 默认手续费
      }))
    } catch (e) {
      console.error('Failed to fetch transactions:', e)
      throw e
    }
  }

  // Fetch news
  const fetchNews = async () => {
    try {
      const response = await axios.get(`${API_BASE}/news?limit=10`)
      const data = response.data

      // 如果后端有错误或没有数据，使用默认新闻
      if (data.error || data.total === 0) {
        news.value = getDefaultNews()
        return
      }

      const allNews: MarketNews[] = []

      // 合并所有分类的新闻
      for (const sentiment of ['positive', 'neutral', 'negative'] as const) {
        const items = data.categorized?.[sentiment] || []
        for (const item of items) {
          allNews.push({
            id: item.id || `NEWS${Date.now()}`,
            title: item.title || '',
            summary: item.summary || item.content || '',
            source: item.source || '财经资讯',
            timestamp: new Date(item.publish_time || item.timestamp || Date.now()),
            sentiment: sentiment,
            relatedSymbols: item.related_symbols || item.symbols || []
          })
        }
      }

      news.value = allNews.length > 0 ? allNews : getDefaultNews()
    } catch (e) {
      console.error('Failed to fetch news:', e)
      news.value = getDefaultNews()
    }
  }

  // 默认新闻 (当后端无法获取时使用)
  const getDefaultNews = (): MarketNews[] => [
    {
      id: 'NEWS001',
      title: 'A 股市场早报：关注金融板块走势',
      summary: '今日 A 股市场开盘，银行板块表现活跃，投资者关注金融股走势。',
      source: '财经日报',
      timestamp: new Date(),
      sentiment: 'neutral',
      relatedSymbols: ['601398.SS', '600036.SS']
    },
    {
      id: 'NEWS002',
      title: '央行发布最新货币政策报告',
      summary: '央行发布季度货币政策执行报告，强调保持流动性合理充裕。',
      source: '央行官网',
      timestamp: new Date(Date.now() - 3600000),
      sentiment: 'positive',
      relatedSymbols: []
    }
  ]

  // Fetch all data
  const fetchAllData = async () => {
    loading.value = true
    error.value = null

    try {
      await Promise.all([
        fetchSummary(),
        fetchHoldings(),
        fetchTransactions(),
        fetchNews()
      ])
      lastUpdate.value = new Date()
    } catch (e: any) {
      error.value = e.message || '获取数据失败'
      console.error('Failed to fetch data:', e)
    } finally {
      loading.value = false
    }
  }

  // Execute buy order
  const buyStock = async (symbol: string, shares: number) => {
    try {
      const response = await axios.post(`${API_BASE}/trade/buy`, {
        symbol,
        shares
      })
      if (response.data.success) {
        await fetchAllData()
      }
      return response.data
    } catch (e) {
      console.error('Buy failed:', e)
      throw e
    }
  }

  // Execute sell order
  const sellStock = async (symbol: string, shares: number) => {
    try {
      const response = await axios.post(`${API_BASE}/trade/sell`, {
        symbol,
        shares
      })
      if (response.data.success) {
        await fetchAllData()
      }
      return response.data
    } catch (e) {
      console.error('Sell failed:', e)
      throw e
    }
  }

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
    loading,
    error,
    lastUpdate,

    // Actions
    fetchAllData,
    fetchSummary,
    fetchHoldings,
    fetchTransactions,
    fetchNews,
    buyStock,
    sellStock,

    // Computed
    totalMarketValue,
    totalGainLoss,
    totalGainLossPercent,
    topGainer,
    topLoser
  }
})
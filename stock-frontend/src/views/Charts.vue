<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStockStore } from '@/stores/stock'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement, Filler } from 'chart.js'
import { Pie, Line, Bar } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
)

const store = useStockStore()
const selectedStock = ref<string>('AAPL')

// Mock K-line data
const klineData = computed(() => {
  const stock = store.holdings.find(h => h.symbol === selectedStock.value)
  if (!stock) return { prices: [], dates: [] }
  
  const prices: number[] = []
  const dates: string[] = []
  const basePrice = stock.currentPrice
  
  for (let i = 0; i < 60; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (59 - i))
    dates.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
    
    const volatility = basePrice * 0.05
    const change = (Math.random() - 0.48) * volatility
    prices.push(basePrice + change)
  }
  
  return { prices, dates }
})

const volumeData = computed(() => {
  return klineData.value.prices.map((price) => ({
    price,
    volume: Math.floor(Math.random() * 1000000) + 500000
  }))
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: {
        color: '#9ca3af',
        font: { size: 12 }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(31, 41, 55, 0.9)',
      titleColor: '#f9fafb',
      bodyColor: '#f9fafb',
      borderColor: '#374151',
      borderWidth: 1,
      padding: 12,
      displayColors: true
    }
  },
  scales: {
    x: {
      ticks: { color: '#9ca3af' },
      grid: { color: '#374151' }
    },
    y: {
      ticks: { color: '#9ca3af' },
      grid: { color: '#374151' }
    }
  }
}

const lineChartData = computed(() => ({
  labels: klineData.value.dates,
  datasets: [{
    label: '价格',
    data: klineData.value.prices,
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    fill: true,
    tension: 0.4,
    pointRadius: 3,
    pointHoverRadius: 5
  }]
}))

const volumeChartData = computed(() => ({
  labels: klineData.value.dates.slice(-30),
  datasets: [{
    label: '成交量',
    data: volumeData.value.slice(-30).map((v) => v.volume),
    backgroundColor: 'rgba(34, 197, 94, 0.6)',
    borderColor: 'rgb(34, 197, 94)',
  }]
}))

const pieChartData = {
  labels: store.holdings.map(h => h.symbol),
  datasets: [{
    data: store.holdings.map(h => h.marketValue),
    backgroundColor: [
      'rgba(59, 130, 246, 0.8)',
      'rgba(147, 51, 234, 0.8)',
      'rgba(236, 72, 153, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(34, 197, 94, 0.8)'
    ],
    borderColor: '#1f2937',
    borderWidth: 2
  }]
}

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const,
      labels: {
        color: '#9ca3af',
        font: { size: 12 },
        padding: 15
      }
    }
  }
}

const formattedNumber = (num: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(num)
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">K 线图表</h1>
      <p class="text-gray-400">查看持仓股票的详细走势分析</p>
    </div>

    <!-- Stock Selector -->
    <div class="card mb-6">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 class="text-xl font-semibold text-white mb-2">选择股票</h2>
          <p class="text-sm text-gray-400">点击下方卡片选择要查看的股票</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="stock in store.holdings"
            :key="stock.symbol"
            @click="selectedStock = stock.symbol"
            :class="selectedStock === stock.symbol ? 'ring-2 ring-primary-500' : ''"
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all duration-200 min-w-[100px]"
          >
            <div class="font-bold text-white">{{ stock.symbol }}</div>
            <div class="text-xs text-gray-400">{{ stock.name }}</div>
          </button>
        </div>
      </div>
    </div>

    <!-- Selected Stock Info -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div v-for="stock in [store.holdings.find(h => h.symbol === selectedStock)]" :key="stock?.symbol" class="col-span-1 md:col-span-5">
        <div class="stat-card" v-if="stock">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-3xl font-bold text-white mb-1">{{ stock.symbol }}</div>
              <div class="text-gray-400">{{ stock.name }}</div>
            </div>
            <div class="text-right">
              <div class="text-3xl font-bold text-green-400">
                {{ stock.currentPrice >= stock.avgPrice ? '+' : '' }}{{ stock.currentPrice - stock.avgPrice >= 0 ? '+' : '' }}{{ (stock.currentPrice - stock.avgPrice).toFixed(2) }}
              </div>
              <div :class="stock.gainLossPercent >= 0 ? 'text-green-400' : 'text-red-400'" class="text-lg font-medium">
                {{ stock.gainLossPercent >= 0 ? '+' : '' }}{{ stock.gainLossPercent.toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Price Chart -->
      <div class="card lg:col-span-2">
        <div class="card-header">
          <h2 class="card-title">价格走势</h2>
        </div>
        <div class="h-96">
          <Line :data="lineChartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Volume Chart -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">成交量</h2>
        </div>
        <div class="h-96">
          <Bar :data="volumeChartData" :options="{ ...chartOptions, plugins: { legend: { display: false } } }" />
        </div>
      </div>
    </div>

    <!-- Allocation & Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Portfolio Allocation -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">持仓分布</h2>
        </div>
        <div class="h-80">
          <Pie :data="pieChartData" :options="pieOptions" />
        </div>
      </div>

      <!-- Performance Metrics -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">技术指标</h2>
        </div>
        <div class="space-y-4">
          <div v-for="stock in store.holdings" :key="stock.symbol" class="p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors">
            <div class="flex items-center justify-between mb-3">
              <div class="font-medium text-white">{{ stock.symbol }}</div>
              <span :class="stock.gainLossPercent >= 0 ? 'text-green-400' : 'text-red-400'" class="text-sm font-medium">
                {{ stock.gainLossPercent >= 0 ? '+' : '' }}{{ stock.gainLossPercent.toFixed(2) }}%
              </span>
            </div>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div class="text-gray-400">持股数量</div>
                <div class="font-medium text-white">{{ stock.shares.toLocaleString() }}</div>
              </div>
              <div>
                <div class="text-gray-400">当前价格</div>
                <div class="font-medium text-white">{{ formattedNumber(stock.currentPrice) }}</div>
              </div>
              <div>
                <div class="text-gray-400">平均成本</div>
                <div class="font-medium text-white">{{ formattedNumber(stock.avgPrice) }}</div>
              </div>
              <div>
                <div class="text-gray-400">盈亏</div>
                <div :class="stock.gainLoss >= 0 ? 'text-green-400' : 'text-red-400'" class="font-medium">
                  {{ stock.gainLoss >= 0 ? '+' : '' }}{{ formattedNumber(stock.gainLoss) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

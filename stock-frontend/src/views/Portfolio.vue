<script setup lang="ts">
import { computed } from 'vue'
import { useStockStore } from '@/stores/stock'

const store = useStockStore()

const formattedNumber = (num: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(num)
}

const portfolioStats = computed(() => {
  const totalCost = store.holdings.reduce((sum, h) => sum + h.costBasis, 0)
  const totalMarket = store.holdings.reduce((sum, h) => sum + h.marketValue, 0)
  const totalGain = totalMarket - totalCost
  const gainPercent = totalCost > 0 ? (totalGain / totalCost) * 100 : 0
  
  return {
    totalCost,
    totalMarket,
    totalGain,
    gainPercent
  }
})

const sortKey = computed(() => 'marketValue' as const)
const sortOrder = computed(() => 'desc' as const)

const sortedHoldings = computed(() => {
  return [...store.holdings].sort((a, b) => {
    const aVal = a[sortKey.value]
    const bVal = b[sortKey.value]
    return sortOrder.value === 'desc' ? (bVal > aVal ? 1 : -1) : (aVal > bVal ? 1 : -1)
  })
})

const stockPerformance = [
  { symbol: 'AAPL', name: 'Apple Inc.', allocation: 28.5, change: 3.87 },
  { symbol: 'MSFT', name: 'Microsoft Corporation', allocation: 32.3, change: 4.10 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', allocation: 6.3, change: 3.78 },
  { symbol: 'TSLA', name: 'Tesla Inc.', allocation: 8.9, change: -2.97 },
  { symbol: 'NVDA', name: 'NVIDIA Corporation', allocation: 24.0, change: 5.12 },
]
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">持仓管理</h1>
      <p class="text-gray-400">查看和管理您的投资组合</p>
    </div>

    <!-- Portfolio Summary -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="stat-card">
        <p class="stat-label">总市值</p>
        <p class="stat-value text-white">{{ formattedNumber(portfolioStats.totalMarket) }}</p>
        <p class="text-sm text-gray-400 mt-1">占总权益的 {{ ((portfolioStats.totalMarket / store.stats.totalEquity) * 100).toFixed(1) }}%</p>
      </div>
      
      <div class="stat-card">
        <p class="stat-label">总成本</p>
        <p class="stat-value text-blue-400">{{ formattedNumber(portfolioStats.totalCost) }}</p>
        <p class="text-sm text-gray-400 mt-1">持仓成本总额</p>
      </div>
      
      <div class="stat-card">
        <p class="stat-label">总盈亏</p>
        <p class="stat-value" :class="portfolioStats.totalGain >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ portfolioStats.totalGain >= 0 ? '+' : '' }}{{ formattedNumber(portfolioStats.totalGain) }}
        </p>
        <p class="text-sm" :class="portfolioStats.gainPercent >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ portfolioStats.gainPercent >= 0 ? '+' : '' }}{{ portfolioStats.gainPercent.toFixed(2) }}%
        </p>
      </div>
      
      <div class="stat-card">
        <p class="stat-label">持仓数量</p>
        <p class="stat-value text-purple-400">{{ store.holdings.length }}</p>
        <p class="text-sm text-gray-400 mt-1">只股票</p>
      </div>
    </div>

    <!-- Holdings Table -->
    <div class="card mb-8">
      <div class="card-header">
        <h2 class="card-title">持仓明细</h2>
        <div class="flex items-center space-x-4">
          <select v-model="sortKey" class="input w-auto text-sm">
            <option value="marketValue">市值从高到低</option>
            <option value="gainLoss">盈亏从高到低</option>
            <option value="gainLossPercent">涨幅从高到低</option>
          </select>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="text-left text-gray-400 text-sm border-b border-gray-700">
              <th class="pb-3 font-medium">股票信息</th>
              <th class="pb-3 font-medium text-right">持股数量</th>
              <th class="pb-3 font-medium text-right">平均成本</th>
              <th class="pb-3 font-medium text-right">当前价格</th>
              <th class="pb-3 font-medium text-right">市值</th>
              <th class="pb-3 font-medium text-right">盈亏金额</th>
              <th class="pb-3 font-medium text-right">盈亏比例</th>
              <th class="pb-3 font-medium text-right">占比</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="holding in sortedHoldings" 
              :key="holding.symbol"
              class="border-b border-gray-700 last:border-0 hover:bg-gray-700/50 transition-colors"
            >
              <td class="py-4">
                <div>
                  <div class="font-medium text-white text-lg">{{ holding.symbol }}</div>
                  <div class="text-sm text-gray-400">{{ holding.name }}</div>
                </div>
              </td>
              <td class="py-4 text-right">{{ holding.shares.toLocaleString() }}</td>
              <td class="py-4 text-right">{{ formattedNumber(holding.avgPrice) }}</td>
              <td class="py-4 text-right">{{ formattedNumber(holding.currentPrice) }}</td>
              <td class="py-4 text-right">{{ formattedNumber(holding.marketValue) }}</td>
              <td class="py-4 text-right">
                <span :class="holding.gainLoss >= 0 ? 'text-green-400' : 'text-red-400'" class="font-medium">
                  {{ holding.gainLoss >= 0 ? '+' : '' }}{{ formattedNumber(holding.gainLoss) }}
                </span>
              </td>
              <td class="py-4 text-right">
                <span :class="holding.gainLossPercent >= 0 ? 'text-green-400' : 'text-red-400'" class="font-medium">
                  {{ holding.gainLossPercent >= 0 ? '+' : '' }}{{ holding.gainLossPercent.toFixed(2) }}%
                </span>
              </td>
              <td class="py-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                  <div class="w-16 bg-gray-700 rounded-full h-1.5">
                    <div 
                      class="h-1.5 rounded-full" 
                      :class="holding.gainLossPercent >= 0 ? 'bg-green-500' : 'bg-red-500'"
                      :style="{ width: `${Math.min(Math.abs(holding.gainLossPercent), 100)}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-400">{{ ((holding.marketValue / portfolioStats.totalMarket) * 100).toFixed(1) }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Performance Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Stock Performance -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">个股表现</h2>
        </div>
        <div class="space-y-4">
          <div 
            v-for="stock in stockPerformance" 
            :key="stock.symbol"
            class="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-gradient-to-br from-gray-600 to-gray-700 rounded-lg flex items-center justify-center font-bold text-white">
                {{ stock.symbol[0] }}
              </div>
              <div>
                <div class="font-medium text-white">{{ stock.symbol }}</div>
                <div class="text-sm text-gray-400">{{ stock.name }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="font-medium text-white">{{ stock.allocation }}%</div>
              <div :class="stock.change >= 0 ? 'text-green-400' : 'text-red-400'" class="text-sm">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Allocation Chart (Visual) -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">资产配置</h2>
        </div>
        <div class="space-y-6">
          <!-- Circular Chart -->
          <div class="flex justify-center">
            <div class="relative w-48 h-48">
              <svg viewBox="0 0 100 100" class="w-full h-full">
                <circle 
                  v-for="(stock, index) in stockPerformance" 
                  :key="stock.symbol"
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="currentColor"
                  :stroke-width="15"
                  :stroke-dasharray="`${stock.allocation * 2.51} 251`"
                  :stroke-offset="-62.8"
                  :class="index === 0 ? 'text-blue-500' : index === 1 ? 'text-purple-500' : index === 2 ? 'text-pink-500' : index === 3 ? 'text-red-500' : 'text-green-500'"
                  transform="rotate(-90 50 50)"
                />
                <circle 
                  cx="50"
                  cy="50"
                  r="30"
                  fill="#1f2937"
                />
              </svg>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center">
                  <div class="text-xs text-gray-400">总市值</div>
                  <div class="text-sm font-bold text-white">{{ formattedNumber(portfolioStats.totalMarket) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Legend -->
          <div class="space-y-2">
            <div v-for="stock in stockPerformance" :key="stock.symbol" class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 rounded-full" :class="
                  stock.symbol === 'AAPL' ? 'bg-blue-500' : 
                  stock.symbol === 'MSFT' ? 'bg-purple-500' : 
                  stock.symbol === 'GOOGL' ? 'bg-pink-500' : 
                  stock.symbol === 'TSLA' ? 'bg-red-500' : 'bg-green-500'
                "></div>
                <span class="text-sm text-gray-300">{{ stock.symbol }}</span>
              </div>
              <span class="text-sm font-medium text-white">{{ stock.allocation }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

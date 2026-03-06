<template>
  <div class="app">
    <!-- 顶部 Header -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo-wrap">
          <span class="logo-icon">🍜</span>
          <div>
            <h1 class="app-title">智能点餐</h1>
            <p class="app-tagline">AI 助力，好味道随心选</p>
          </div>
        </div>
        <div class="header-badge">
          <span class="badge-dot"></span>
          营业中
        </div>
      </div>

      <!-- 波浪装饰 -->
      <svg class="header-wave" viewBox="0 0 375 24" preserveAspectRatio="none">
        <path d="M0 0 C100 24 275 24 375 0 L375 24 L0 24 Z" fill="#FFF8F5"/>
      </svg>
    </header>

    <!-- 主内容 -->
    <main class="app-main">
      <!-- 配送查询 -->
      <DeliveryCheck />

      <!-- 分割线 -->
      <div class="divider">
        <span class="divider-line"></span>
        <span class="divider-text">今日菜单</span>
        <span class="divider-line"></span>
      </div>

      <!-- 菜单网格 -->
      <MenuGrid
        :menus="menus"
        :loading="menuLoading"
        :error="menuError"
        :highlight-ids="highlightIds"
        @retry="loadMenus"
      />
    </main>

    <!-- 智能点餐助手 -->
    <ChatAssistant
      @highlight="onHighlight"
      @clear-highlight="onClearHighlight"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MenuGrid from './components/MenuGrid.vue'
import DeliveryCheck from './components/DeliveryCheck.vue'
import ChatAssistant from './components/ChatAssistant.vue'
import { fetchMenus } from './api/index.js'

const menus = ref([])
const menuLoading = ref(false)
const menuError = ref('')
const highlightIds = ref([])

async function loadMenus() {
  menuLoading.value = true
  menuError.value = ''
  try {
    const res = await fetchMenus()
    menus.value = res.menus || []
  } catch (e) {
    menuError.value = e.message || '菜单加载失败，请重试'
  } finally {
    menuLoading.value = false
  }
}

function onHighlight(ids) {
  highlightIds.value = ids
  // 滚动到第一个推荐菜品
  setTimeout(() => {
    const el = document.querySelector('.menu-card.recommended')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 300)
}

function onClearHighlight() {
  highlightIds.value = []
}

onMounted(() => {
  loadMenus()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: var(--bg);
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  background: linear-gradient(145deg, var(--primary) 0%, #E8501A 50%, var(--secondary) 100%);
  padding: 44px 20px 28px;
  position: relative;
  color: white;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 36px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.app-title {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 1px;
  text-shadow: 0 1px 4px rgba(0,0,0,0.2);
}

.app-tagline {
  font-size: 12px;
  opacity: 0.85;
  margin-top: 2px;
}

.header-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.badge-dot {
  width: 7px;
  height: 7px;
  background: #2ECC71;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.header-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 24px;
  display: block;
}

/* 主内容 */
.app-main {
  flex: 1;
  padding-top: 16px;
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

.divider-text {
  font-size: 13px;
  color: var(--text-light);
  white-space: nowrap;
  font-weight: 500;
}
</style>
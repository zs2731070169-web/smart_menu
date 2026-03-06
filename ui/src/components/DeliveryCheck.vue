<template>
  <section class="delivery-section">
    <div class="delivery-card">
      <div class="delivery-header">
        <span class="delivery-icon">📍</span>
        <div>
          <h3 class="delivery-title">配送范围查询</h3>
          <p class="delivery-subtitle">输入地址，确认是否可以配送到您</p>
        </div>
      </div>

      <div class="input-row">
        <div class="input-wrap" :class="{ focused: isFocused }">
          <input
            ref="inputRef"
            v-model="address"
            type="text"
            placeholder="请输入您的收货地址..."
            class="address-input"
            @focus="isFocused = true"
            @blur="isFocused = false"
            @keyup.enter="handleCheck"
            :disabled="loading"
          />
          <button
            v-if="address"
            class="clear-btn"
            @click="clearInput"
          >×</button>
        </div>
        <button
          class="check-btn"
          :class="{ loading }"
          @click="handleCheck"
          :disabled="loading || !address.trim()"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>查询</span>
        </button>
      </div>

      <!-- 查询结果 -->
      <transition name="slide-fade">
        <div v-if="result" class="result-card" :class="resultClass">
          <div class="result-status">
            <span class="status-icon">{{ result.in_range ? '✅' : '❌' }}</span>
            <span class="status-text">{{ result.in_range ? '可以配送' : '超出配送范围' }}</span>
          </div>

          <div v-if="result.formatted_address" class="result-address">
            <span class="result-label">地址</span>
            <span class="result-value">{{ result.formatted_address }}</span>
          </div>

          <div v-if="result.in_range" class="result-details">
            <div class="result-item">
              <span class="result-label">距离</span>
              <span class="result-value highlight">{{ result.distance }} km</span>
            </div>
            <div class="result-item">
              <span class="result-label">预计</span>
              <span class="result-value highlight">{{ result.duration }}</span>
            </div>
          </div>

          <p v-if="result.message && !result.status" class="error-msg">{{ result.message }}</p>
        </div>
      </transition>

      <!-- 错误提示 -->
      <transition name="slide-fade">
        <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>
      </transition>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { checkDelivery } from '../api/index.js'

const address = ref('')
const loading = ref(false)
const result = ref(null)
const errorMsg = ref('')
const isFocused = ref(false)
const inputRef = ref(null)

const resultClass = computed(() => {
  if (!result.value) return ''
  if (!result.value.status) return 'result-error'
  return result.value.in_range ? 'result-success' : 'result-warning'
})

function clearInput() {
  address.value = ''
  result.value = null
  errorMsg.value = ''
  inputRef.value?.focus()
}

async function handleCheck() {
  if (!address.value.trim() || loading.value) return

  loading.value = true
  result.value = null
  errorMsg.value = ''

  try {
    result.value = await checkDelivery(address.value.trim())
  } catch (e) {
    errorMsg.value = e.message || '查询失败，请稍后重试'
    setTimeout(() => { errorMsg.value = '' }, 3000)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.delivery-section {
  padding: 0 16px 16px;
}

.delivery-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 18px 16px;
  box-shadow: 0 4px 20px rgba(255, 107, 53, 0.1);
  border: 1px solid var(--border);
}

.delivery-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.delivery-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.delivery-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.delivery-subtitle {
  font-size: 12px;
  color: var(--text-light);
}

.input-row {
  display: grid;
}

.input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  padding: 0 10px;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 42px;
}

.input-wrap.focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.address-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  min-width: 0;
}

.address-input::placeholder {
  color: var(--text-light);
}

.clear-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: var(--text-light);
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
}

.check-btn {
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: none;
  border-radius: 10px;
  margin-top: 6px;
  height: 42px;
  font-size: 14px;
  font-weight: 600;
  transition: opacity 0.2s, transform 0.1s;
}

.check-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.check-btn:not(:disabled):active {
  transform: scale(0.96);
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 结果卡片 */
.result-card {
  margin-top: 14px;
  padding: 14px;
  border-radius: var(--radius);
  border: 1.5px solid;
  animation: fadeIn 0.3s ease;
}

.result-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.status-icon {
  font-size: 18px;
}

.status-text {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.result-address {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 10px;
}

.result-details {
  display: flex;
  gap: 20px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-label {
  font-size: 11px;
  color: var(--text-light);
}

.result-value {
  font-size: 13px;
  color: var(--text-primary);
}

.result-value.highlight {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary);
}

.error-msg {
  font-size: 13px;
  color: var(--error);
  margin-top: 6px;
}

.error-toast {
  margin-top: 10px;
  background: #FFF0F0;
  color: var(--error);
  padding: 10px 12px;
  border-radius: var(--radius);
  font-size: 13px;
  border: 1px solid #FFBBBB;
}

/* gap fallback for older Android WebView */
@supports not (gap: 1rem) {
  .delivery-header > * + * {
    margin-left: 10px;
  }

  .input-row > * + * {
    margin-left: 8px;
  }

  .result-details > * + * {
    margin-left: 20px;
  }
}

@media (max-width: 390px) {
  .delivery-section {
    padding: 0 14px 14px;
  }

  .delivery-card {
    padding: 14px 12px;
  }

  .delivery-header {
    align-items: flex-start;
  }

  .input-row {
    flex-wrap: wrap;
    gap: 10px;
  }

  .input-wrap {
    min-width: 0;
  }

  .check-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

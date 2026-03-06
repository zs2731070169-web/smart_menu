<template>
  <!-- 浮动聊天按钮 -->
  <div class="chat-fab-wrapper">
    <transition name="bounce">
      <button
          v-if="!isOpen"
          class="chat-fab"
          @click="openChat"
          aria-label="打开点餐助手"
      >
        <span class="fab-icon">🤖</span>
        <span class="fab-label">点餐助手</span>
        <span v-if="hasUnread" class="unread-dot"></span>
      </button>
    </transition>

    <!-- 聊天面板 -->
    <transition name="slide-up">
      <div v-if="isOpen" class="chat-panel">
        <!-- 头部 -->
        <div class="chat-header">
          <div class="chat-header-info">
            <div class="avatar">
              <span>🤖</span>
            </div>
            <div>
              <h4 class="chat-name">智能点餐助手</h4>
              <span class="chat-status">
                <span class="online-dot"></span>
                在线服务中
              </span>
            </div>
          </div>
          <div class="header-actions">
            <button class="new-chat-btn" @click="startNewChat" :disabled="thinking" aria-label="开启新对话" title="新对话">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
              <span>新对话</span>
            </button>
            <button class="close-btn" @click="closeChat" aria-label="关闭">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 消息区域 -->
        <div class="chat-messages" ref="messagesRef">
          <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="message-row"
              :class="msg.role"
          >
            <div v-if="msg.role === 'assistant'" class="msg-avatar">🤖</div>
            <div class="message-bubble" :class="msg.role">
              <p class="message-text">{{ msg.text }}</p>
              <span class="message-time">{{ msg.time }}</span>
            </div>
          </div>

          <!-- 加载中气泡 -->
          <div v-if="thinking" class="message-row assistant">
            <div class="msg-avatar">🤖</div>
            <div class="message-bubble assistant thinking">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>

        <!-- 快捷提示（每次展示） -->
        <div v-if="showHints" class="quick-hints">
          <p class="hints-label">你可以问我：</p>
          <div class="hints-list">
            <button
                v-for="hint in hints"
                :key="hint"
                class="hint-chip"
                @click="sendHint(hint)"
            >{{ hint }}
            </button>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="input-wrap" :class="{ focused: inputFocused }">
            <input
                v-model="inputText"
                type="text"
                placeholder="想吃什么？问问我吧..."
                class="chat-input"
                @focus="inputFocused = true"
                @blur="inputFocused = false"
                @keyup.enter="handleSend"
                :disabled="thinking"
                ref="chatInputRef"
            />
            <button
                class="send-btn"
                @click="handleSend"
                :disabled="!inputText.trim() || thinking"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z"
                      stroke="currentColor" stroke-width="2"
                      stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 遮罩层（移动端点击外部关闭） -->
    <transition name="fade">
      <div v-if="isOpen" class="chat-overlay" @click="closeChat"></div>
    </transition>
  </div>
</template>

<script setup>
import {nextTick, ref, watch} from 'vue'
import {newChat, sendChat} from '../api/index.js'

const emit = defineEmits(['highlight', 'clearHighlight'])

const isOpen = ref(false)
const hasUnread = ref(false)
const thinking = ref(false)
const inputText = ref('')
const inputFocused = ref(false)
const messagesRef = ref(null)
const chatInputRef = ref(null)
const showHints = ref(true)

const hints = ['推荐几道好吃的菜', '订餐联系']

const messages = ref([
  {role: 'assistant', text: '您好！我是智能点餐助手，可以根据您的口味偏好为您推荐菜品。有什么我可以帮您的吗？', time: formatTime(new Date())},
])

function formatTime(date) {
  return date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'})
}

function openChat() {
  isOpen.value = true
  hasUnread.value = false
  nextTick(() => {
    scrollToBottom()
    chatInputRef.value?.focus()
  })
}

function closeChat() {
  isOpen.value = false
}

const WELCOME_MSG = {
  role: 'assistant',
  text: '您好！我是智能点餐助手，可以根据您的口味偏好为您推荐菜品。有什么我可以帮您的吗？',
}

async function startNewChat() {
  try {
    await newChat()
  } catch {
    // 接口失败不影响前端重置
  }
  emit('clearHighlight')
  messages.value = [{...WELCOME_MSG, time: formatTime(new Date())}]
  inputText.value = ''
  showHints.value = true
  nextTick(() => {
    scrollToBottom()
    chatInputRef.value?.focus()
  })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function sendHint(hint) {
  inputText.value = hint
  handleSend()
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return

  // 正则校验，如果text只有特殊字符，则直接返回，避免发送无意义的消息
  const meaningfulText = text.replace(/[\s\p{P}\p{S}]+/gu, '')
  if (!meaningfulText) {
    inputText.value = ''
    messages.value.push({
      role: 'assistant',
      text: '抱歉，没有收到有效问题，请重新描述一下吧！',
      time: formatTime(new Date()),
    })
    return
  }

  // 新一次查询前清除框选
  emit('clearHighlight')
  showHints.value = false

  // 添加用户消息
  messages.value.push({
    role: 'user',
    text,
    time: formatTime(new Date()),
  })
  inputText.value = ''
  thinking.value = true
  scrollToBottom()

  try {
    const res = await sendChat(text)
    const msg = res.message || {}

    // 助手回复文本
    const replyText = msg.recommend_menus || msg.message || '抱歉，我暂时无法理解您的问题，请换个方式描述。'
    messages.value.push({
      role: 'assistant',
      text: replyText,
      time: formatTime(new Date()),
    })

    // 如果有推荐菜品 ID，触发框选
    if (Array.isArray(msg.ids) && msg.ids.length > 0) {
      emit('highlight', msg.ids)
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      text: '网络出了点小问题，请稍后再试。',
      time: formatTime(new Date()),
    })
  } finally {
    thinking.value = false
    //恢复提示展示
    showHints.value = true
    scrollToBottom()
    if (!isOpen.value) hasUnread.value = true
  }
}

watch(messages, () => {
  scrollToBottom()
}, {deep: true})
</script>

<style scoped>
.chat-fab-wrapper {
  position: fixed;
  bottom: 24px;
  right: 20px;
  z-index: 1000;
}

/* 浮动按钮 */
.chat-fab {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  border: none;
  border-radius: 28px;
  padding: 12px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 6px 24px rgba(255, 107, 53, 0.45);
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
}

.chat-fab:active {
  transform: scale(0.94);
  box-shadow: 0 3px 12px rgba(255, 107, 53, 0.35);
}

.fab-icon {
  font-size: 20px;
}

.unread-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  background: #FF3B30;
  border-radius: 50%;
  border: 2px solid white;
}

/* 聊天面板 */
.chat-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-width: 480px;
  margin: 0 auto;
  height: 90vh;
  background: var(--bg-card);
  border-radius: 24px 24px 0 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  overflow: hidden;
}

/* 遮罩 */
.chat-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1000;
  backdrop-filter: blur(2px);
}

/* 头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, #fff8f5, #fff);
}

.chat-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.chat-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--success);
}

.online-dot {
  width: 6px;
  height: 6px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 16px;
  padding: 5px 10px;
  font-size: 12px;
  color: var(--primary);
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:not(:disabled):active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.new-chat-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.close-btn {
  background: var(--bg);
  border: none;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background 0.2s;
}

.close-btn:active {
  background: var(--border);
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  /* Adaptive vertical spacing between bubbles across phone sizes */
  --message-row-gap: clamp(14px, 2.8vw, 20px);
  gap: var(--message-row-gap);
  scroll-behavior: smooth;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 18px;
  position: relative;
  animation: fadeIn 0.2s ease;
}

.message-bubble.assistant {
  background: var(--bg);
  border: 1px solid var(--border);
  border-bottom-left-radius: 6px;
}

.message-bubble.user {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border-bottom-right-radius: 6px;
}

.message-text {
  font-size: 14px;
  line-height: 1;
  word-break: break-word;
}

.message-time {
  display: block;
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.6;
}

/* 思考中动画 */
.thinking {
  padding: 14px 18px;
  display: flex;
  gap: 5px;
  align-items: center;
}

.dot {
  width: 7px;
  height: 7px;
  background: var(--primary);
  border-radius: 50%;
  animation: bounce-dot 1.2s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce-dot {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

/* 快捷提示 */
.quick-hints {
  padding: 0 14px 12px;
  border-top: 1px solid var(--border);
}

.hints-label {
  font-size: 11px;
  color: var(--text-light);
  margin-bottom: 8px;
  padding-top: 10px;
}

.hints-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.hint-chip {
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--primary);
  font-size: 10px;
  padding: 5px 12px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.hint-chip:active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

/* 输入区域 */
.chat-input-area {
  padding: 12px 14px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  border-top: 1px solid var(--border);
  background: var(--bg-card);
}

.input-wrap {
  display: flex;
  align-items: center;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 24px;
  padding: 0 6px 0 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 44px;
}

.input-wrap.focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  padding: 10px 0;
}

.chat-input::placeholder {
  color: var(--text-light);
}

.send-btn {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-btn:not(:disabled):active {
  transform: scale(0.9);
}

/* 动画 */
.bounce-enter-active {
  animation: bounce-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.bounce-leave-active {
  animation: bounce-in 0.2s ease reverse;
}

@keyframes bounce-in {
  from {
    transform: scale(0.5);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* gap fallback for older Android WebView */
@supports not (gap: 1rem) {
  .chat-header-info > * + * {
    margin-left: 10px;
  }

  .header-actions > * + * {
    margin-left: 8px;
  }

  .message-row > * + * {
    margin-left: 8px;
  }

  .message-row + .message-row {
    margin-top: var(--message-row-gap, 16px);
  }

  .thinking > * + * {
    margin-left: 5px;
  }

  .hints-list > * {
    margin: 0 6px 6px 0;
  }
}

@media (max-width: 390px) {
  .chat-header {
    padding: 14px 12px;
  }

  .chat-header-info {
    min-width: 0;
  }

  .chat-name {
    font-size: 14px;
  }

  .new-chat-btn {
    padding: 4px 8px;
    font-size: 11px;
  }

  .close-btn {
    width: 30px;
    height: 30px;
  }

  .chat-messages {
    padding: 14px 12px;
    --message-row-gap: clamp(16px, 4vw, 22px);
  }

  .message-bubble {
    max-width: 80%;
    padding: 10px 12px;
  }
}

@media (min-width: 480px) {
  .chat-messages {
    --message-row-gap: clamp(16px, 2vw, 24px);
  }
}
</style>

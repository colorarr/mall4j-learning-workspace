<template>
  <view class="ai-agent">
    <button
      class="ai-agent__entry"
      aria-label="打开商城智能助手"
      @tap="openChat"
    >
      <image
        class="ai-agent__entry-image"
        src="/static/images/icon/ai-assistant.png"
        mode="aspectFit"
      />
    </button>

    <view
      v-if="visible"
      class="ai-agent__mask"
      @tap="closeChat"
    >
      <view
        class="ai-agent__panel"
        @tap.stop
      >
        <view class="ai-agent__drag-bar" />

        <view class="ai-agent__header">
          <image
            class="ai-agent__avatar"
            src="/static/images/icon/ai-assistant.png"
            mode="aspectFit"
          />
          <view class="ai-agent__header-content">
            <text class="ai-agent__title">
              商城智能助手
            </text>
            <view class="ai-agent__status">
              <view class="ai-agent__status-dot" />
              <text>在线为你服务</text>
            </view>
          </view>
          <button
            class="ai-agent__close"
            aria-label="关闭智能助手"
            @tap="closeChat"
          >
            ×
          </button>
        </view>

        <scroll-view
          class="ai-agent__messages"
          scroll-y
          :scroll-into-view="scrollIntoView"
          :show-scrollbar="false"
        >
          <view class="ai-agent__welcome">
            <text class="ai-agent__welcome-title">
              你好，我是商城智能助手
            </text>
            <text class="ai-agent__welcome-text">
              我可以帮你推荐商品、解答选购问题和查询订单信息。
            </text>
          </view>

          <view class="ai-agent__quick-list">
            <view
              v-for="item in quickQuestions"
              :key="item"
              class="ai-agent__quick-item"
              @tap="sendQuickQuestion(item)"
            >
              {{ item }}
            </view>
          </view>

          <view
            v-for="message in messages"
            :id="`ai-message-${message.id}`"
            :key="message.id"
            class="ai-agent__message-row"
            :class="`ai-agent__message-row--${message.role}`"
          >
            <image
              v-if="message.role === 'assistant'"
              class="ai-agent__message-avatar"
              src="/static/images/icon/ai-assistant.png"
              mode="aspectFit"
            />
            <view class="ai-agent__message-bubble">
              {{ message.content }}
            </view>
          </view>

          <view
            v-if="isReplying"
            id="ai-message-loading"
            class="ai-agent__message-row ai-agent__message-row--assistant"
          >
            <image
              class="ai-agent__message-avatar"
              src="/static/images/icon/ai-assistant.png"
              mode="aspectFit"
            />
            <view class="ai-agent__typing">
              <view />
              <view />
              <view />
            </view>
          </view>
        </scroll-view>

        <view class="ai-agent__composer">
          <view class="ai-agent__input-wrap">
            <input
              v-model="inputValue"
              class="ai-agent__input"
              confirm-type="send"
              maxlength="300"
              placeholder="请输入你想咨询的问题"
              placeholder-class="ai-agent__input-placeholder"
              @confirm="sendMessage"
            >
          </view>
          <button
            class="ai-agent__send"
            :class="{ 'ai-agent__send--active': canSend }"
            :disabled="!canSend"
            @tap="sendMessage"
          >
            发送
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'

const quickQuestions = [
  '推荐热销商品',
  '帮我查询订单',
  '商品应该怎么选'
]

const visible = ref(false)
const inputValue = ref('')
const messages = ref([])
const isReplying = ref(false)
const scrollIntoView = ref('')
let messageId = 0
let replyTimer = null

const canSend = computed(() => {
  return inputValue.value.trim().length > 0 && !isReplying.value
})

const getCurrentRoute = () => {
  const pages = getCurrentPages()
  return pages[pages.length - 1]?.route || ''
}

const isTabPage = () => {
  return [
    'pages/index/index',
    'pages/category/category',
    'pages/basket/basket',
    'pages/user/user'
  ].includes(getCurrentRoute())
}

const updateScrollPosition = (targetId) => {
  nextTick(() => {
    scrollIntoView.value = ''
    nextTick(() => {
      scrollIntoView.value = targetId
    })
  })
}

const openChat = () => {
  visible.value = true
  if (isTabPage()) {
    uni.hideTabBar({ animation: true })
  }
}

const closeChat = () => {
  visible.value = false
  if (isTabPage()) {
    uni.showTabBar({ animation: true })
  }
}

const createAssistantReply = (question) => {
  if (question.includes('订单')) {
    return '请告诉我订单号，或者进入“我的-订单列表”选择需要查询的订单。'
  }
  if (question.includes('推荐') || question.includes('热销')) {
    return '可以告诉我想购买的商品类型和预算，我会为你整理更合适的商品。'
  }
  if (question.includes('怎么选') || question.includes('选购')) {
    return '请告诉我商品类型、使用场景和预算，我会从价格、规格和评价等方面帮你比较。'
  }
  return '已经收到你的问题。智能体接口接入后，我会结合商城商品和订单数据为你解答。'
}

const sendMessage = () => {
  const content = inputValue.value.trim()
  if (!content || isReplying.value) return

  messageId += 1
  messages.value.push({
    id: messageId,
    role: 'user',
    content
  })
  inputValue.value = ''
  isReplying.value = true
  updateScrollPosition('ai-message-loading')

  replyTimer = setTimeout(() => {
    messageId += 1
    messages.value.push({
      id: messageId,
      role: 'assistant',
      content: createAssistantReply(content)
    })
    isReplying.value = false
    updateScrollPosition(`ai-message-${messageId}`)
  }, 650)
}

const sendQuickQuestion = (question) => {
  inputValue.value = question
  sendMessage()
}

onUnmounted(() => {
  if (replyTimer) {
    clearTimeout(replyTimer)
  }
  if (visible.value && isTabPage()) {
    uni.showTabBar({ animation: false })
  }
})
</script>

<style scoped lang="scss">
@use './ai-agent.scss';
</style>

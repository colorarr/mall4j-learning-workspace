<template>
  <view class="ai-agent">
    <button
      class="ai-agent__entry"
      :class="{ 'ai-agent__entry--dragging': isDragging }"
      :style="entryStyle"
      aria-label="打开商城智能助手"
      @mousedown.prevent="handleMouseStart"
      @tap="handleEntryTap"
      @touchcancel.stop="handleTouchEnd"
      @touchend.stop="handleTouchEnd"
      @touchmove.stop.prevent="handleTouchMove"
      @touchstart.stop="handleTouchStart"
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
              <view
                class="ai-agent__status-dot"
                :class="`ai-agent__status-dot--${agentStatus}`"
              />
              <text>{{ agentStatusText }}</text>
            </view>
          </view>
          <view class="ai-agent__header-actions">
            <button
              class="ai-agent__new-chat"
              aria-label="开始新对话"
              @tap="startNewConversation"
            >
              新对话
            </button>
            <button
              class="ai-agent__close"
              aria-label="关闭智能助手"
              @tap="closeChat"
            >
              ×
            </button>
          </view>
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
              <MarkdownRender
                v-if="message.role === 'assistant'"
                class="ai-agent__markdown"
                :content="message.content"
                :final="message.final !== false"
                html-policy="escape"
                mode="chat"
                render-code-blocks-as-pre
              />
              <text
                v-else
                class="ai-agent__plain-text"
              >
                {{ message.content }}
              </text>
            </view>
          </view>

          <view
            v-if="pendingApproval"
            id="ai-approval"
            class="ai-agent__message-row ai-agent__message-row--assistant"
          >
            <image
              class="ai-agent__message-avatar"
              src="/static/images/icon/ai-assistant.png"
              mode="aspectFit"
            />
            <view class="ai-agent__approval-card">
              <view class="ai-agent__approval-header">
                <view class="ai-agent__approval-icon">
                  !
                </view>
                <view class="ai-agent__approval-heading">
                  <text class="ai-agent__approval-title">
                    需要你的确认
                  </text>
                  <text class="ai-agent__approval-tip">
                    确认后将立即执行
                  </text>
                </view>
              </view>

              <view
                v-for="(action, index) in pendingApproval.actions"
                :key="`${action.name}-${index}`"
                class="ai-agent__approval-action"
              >
                <text class="ai-agent__approval-action-name">
                  {{ action.displayName }}
                </text>
                <text class="ai-agent__approval-description">
                  {{ action.description }}
                </text>
              </view>

              <view class="ai-agent__approval-buttons">
                <button
                  class="ai-agent__approval-button ai-agent__approval-button--reject"
                  :disabled="isApprovalSubmitting"
                  @tap.stop="submitApproval('reject')"
                >
                  取消
                </button>
                <button
                  class="ai-agent__approval-button ai-agent__approval-button--approve"
                  :disabled="isApprovalSubmitting"
                  @tap.stop="submitApproval('approve')"
                >
                  确认执行
                </button>
              </view>
            </view>
          </view>

          <view
            v-if="isReplying || isHistoryLoading"
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
              <text v-if="isHistoryLoading || replyStatus">
                {{ isHistoryLoading ? '正在加载聊天记录' : replyStatus }}
              </text>
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
            :disabled="isReplying || isHistoryLoading || Boolean(pendingApproval)"
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
import MarkdownRender from 'markstream-vue'
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  getAgentHistory,
  resumeAgentReply,
  streamAgentReply
} from '@/api/ai-agent.js'
import './markstream.css'

const ENTRY_SIZE_RPX = 94
const ENTRY_MARGIN_RPX = 24
const ENTRY_TOP_MARGIN_RPX = 24
const DRAG_THRESHOLD_PX = 6
const POSITION_STORAGE_KEY = 'mall4j-ai-agent-position'
const CONVERSATION_STORAGE_KEY = 'mall4j-ai-agent-conversation-id'

const APPROVAL_TOOL_NAMES = {
  cart_remove_items: '删除购物车商品',
  cart_clear: '清空购物车',
  cart_clean_expired_items: '清理失效购物项',
  order_cancel: '取消订单',
  order_confirm_receipt: '确认收货',
  order_delete_history: '删除历史订单',
  address_delete: '删除收货地址'
}

const APPROVAL_TOOL_DESCRIPTIONS = {
  cart_remove_items: '将删除你选中的购物车商品。',
  cart_clear: '将清空购物车中的全部商品。',
  cart_clean_expired_items: '将删除购物车中的全部失效商品。',
  order_cancel: '将取消你选中的订单。',
  order_confirm_receipt: '将把你选中的订单更新为已收货。',
  order_delete_history: '将删除你选中的历史订单记录。',
  address_delete: '将删除你选中的收货地址。'
}

const quickQuestions = [
  '推荐热销商品',
  '帮我查询订单',
  '商品应该怎么选'
]

const visible = ref(false)
const isDragging = ref(false)
const inputValue = ref('')
const messages = ref([])
const isReplying = ref(false)
const isHistoryLoading = ref(false)
const isApprovalSubmitting = ref(false)
const pendingApproval = ref(null)
const replyStatus = ref('')
const scrollIntoView = ref('')
const agentStatus = ref('checking')
const conversationId = ref(uni.getStorageSync(CONVERSATION_STORAGE_KEY) || '')
const agentApi = (import.meta.env.VITE_APP_AGENT_API || '/agent-api').replace(/\/$/, '')
let messageId = 0
let requestController = null
let historyController = null
let scrollTimer = null
let lastDragEndAt = 0

const entryPosition = ref({
  left: null,
  top: null
})

const dragState = {
  active: false,
  moved: false,
  startX: 0,
  startY: 0,
  originLeft: 0,
  originTop: 0
}

const canSend = computed(() => {
  return inputValue.value.trim().length > 0 &&
    !isReplying.value &&
    !isHistoryLoading.value &&
    !pendingApproval.value
})
const agentStatusText = computed(() => {
  if (agentStatus.value === 'online') return '在线为你服务'
  if (agentStatus.value === 'offline') return '服务暂时离线'
  return '正在连接服务'
})

const entryStyle = computed(() => {
  if (entryPosition.value.left === null || entryPosition.value.top === null) {
    return {}
  }

  return {
    left: `${entryPosition.value.left}px`,
    top: `${entryPosition.value.top}px`,
    right: 'auto',
    bottom: 'auto'
  }
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

const getBottomReserveRpx = () => {
  const route = getCurrentRoute()

  if (route === 'pages/basket/basket') {
    return 252
  }

  if ([
    'pages/prod/prod',
    'pages/submit-order/submit-order',
    'pages/delivery-address/delivery-address',
    'pages/editAddress/editAddress'
  ].includes(route)) {
    return 156
  }

  return isTabPage() ? 142 : 32
}

const getEntryBounds = () => {
  const systemInfo = uni.getSystemInfoSync()
  const width = systemInfo.windowWidth || 375
  const height = systemInfo.windowHeight || 667
  const toPx = (rpx) => typeof uni.upx2px === 'function' ? uni.upx2px(rpx) : rpx * Math.min(width, 750) / 750
  const entrySize = toPx(ENTRY_SIZE_RPX)
  const sideMargin = toPx(ENTRY_MARGIN_RPX)
  const topMargin = toPx(ENTRY_TOP_MARGIN_RPX)
  const safeBottom = systemInfo.safeArea ? Math.max(0, height - systemInfo.safeArea.bottom) : 0
  const bottomReserve = toPx(getBottomReserveRpx()) + safeBottom

  return {
    minX: sideMargin,
    maxX: Math.max(sideMargin, width - entrySize - sideMargin),
    minY: topMargin,
    maxY: Math.max(topMargin, height - entrySize - bottomReserve)
  }
}

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

const applyStoredEntryPosition = () => {
  const bounds = getEntryBounds()
  const storedPosition = uni.getStorageSync(POSITION_STORAGE_KEY)
  const xRatio = Number(storedPosition?.xRatio)
  const yRatio = Number(storedPosition?.yRatio)

  entryPosition.value = {
    left: Number.isFinite(xRatio) && xRatio <= 0.5 ? bounds.minX : bounds.maxX,
    top: Number.isFinite(yRatio) ? bounds.minY + clamp(yRatio, 0, 1) * (bounds.maxY - bounds.minY) : bounds.maxY
  }
}

const saveEntryPosition = () => {
  const bounds = getEntryBounds()
  const xRange = bounds.maxX - bounds.minX
  const yRange = bounds.maxY - bounds.minY

  uni.setStorageSync(POSITION_STORAGE_KEY, {
    xRatio: xRange > 0 ? (entryPosition.value.left - bounds.minX) / xRange : 1,
    yRatio: yRange > 0 ? (entryPosition.value.top - bounds.minY) / yRange : 1
  })
}

const updateEntryPosition = (clientX, clientY) => {
  if (!dragState.active) return

  const offsetX = clientX - dragState.startX
  const offsetY = clientY - dragState.startY
  if (Math.hypot(offsetX, offsetY) >= DRAG_THRESHOLD_PX) {
    dragState.moved = true
    isDragging.value = true
  }

  if (!dragState.moved) return

  const bounds = getEntryBounds()
  entryPosition.value = {
    left: clamp(dragState.originLeft + offsetX, bounds.minX, bounds.maxX),
    top: clamp(dragState.originTop + offsetY, bounds.minY, bounds.maxY)
  }
}

const startDrag = (clientX, clientY) => {
  if (entryPosition.value.left === null || entryPosition.value.top === null) {
    applyStoredEntryPosition()
  }

  dragState.active = true
  dragState.moved = false
  dragState.startX = clientX
  dragState.startY = clientY
  dragState.originLeft = entryPosition.value.left
  dragState.originTop = entryPosition.value.top
}

const finishDrag = () => {
  if (!dragState.active) return

  if (dragState.moved) {
    const bounds = getEntryBounds()
    const horizontalMiddle = (bounds.minX + bounds.maxX) / 2
    entryPosition.value = {
      left: entryPosition.value.left <= horizontalMiddle ? bounds.minX : bounds.maxX,
      top: clamp(entryPosition.value.top, bounds.minY, bounds.maxY)
    }
    saveEntryPosition()
    lastDragEndAt = Date.now()
  }

  dragState.active = false
  dragState.moved = false
  isDragging.value = false

  // #ifdef H5
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseEnd)
  // #endif
}

const handleTouchStart = (event) => {
  const touch = event.touches?.[0]
  if (!touch) return
  startDrag(touch.clientX, touch.clientY)
}

const handleTouchMove = (event) => {
  const touch = event.touches?.[0]
  if (!touch) return
  updateEntryPosition(touch.clientX, touch.clientY)
}

const handleTouchEnd = () => {
  finishDrag()
}

const handleMouseMove = (event) => {
  updateEntryPosition(event.clientX, event.clientY)
}

const handleMouseEnd = () => {
  finishDrag()
}

const handleMouseStart = (event) => {
  startDrag(event.clientX, event.clientY)

  // #ifdef H5
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseEnd)
  // #endif
}

const handleEntryTap = () => {
  if (isDragging.value || Date.now() - lastDragEndAt < 300) return
  openChat()
}

const updateScrollPosition = (targetId) => {
  nextTick(() => {
    scrollIntoView.value = ''
    nextTick(() => {
      scrollIntoView.value = targetId
    })
  })
}

const scheduleScrollPosition = (targetId) => {
  if (scrollTimer) return
  scrollTimer = setTimeout(() => {
    scrollTimer = null
    updateScrollPosition(targetId)
  }, 50)
}

const openChat = () => {
  visible.value = true
  checkAgentHealth()
  loadConversationHistory()
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

const resetConversation = () => {
  const controller = requestController
  requestController = null
  controller?.abort()

  const activeHistoryController = historyController
  historyController = null
  activeHistoryController?.abort()

  conversationId.value = ''
  uni.removeStorageSync(CONVERSATION_STORAGE_KEY)

  messages.value = []
  inputValue.value = ''
  isReplying.value = false
  isHistoryLoading.value = false
  isApprovalSubmitting.value = false
  pendingApproval.value = null
  replyStatus.value = ''
  scrollIntoView.value = ''
  messageId = 0

  if (scrollTimer) {
    clearTimeout(scrollTimer)
    scrollTimer = null
  }
}

const startNewConversation = () => {
  if (pendingApproval.value) {
    uni.showToast({
      title: '请先处理待确认的操作',
      icon: 'none'
    })
    return
  }

  if (messages.value.length === 0 && !isReplying.value) {
    resetConversation()
    uni.showToast({
      title: '已开始新对话',
      icon: 'none'
    })
    return
  }

  uni.showModal({
    title: '开始新对话',
    content: '当前聊天窗口将被清空，历史会话仍会保留。',
    confirmText: '开始',
    cancelText: '取消',
    success: (result) => {
      if (!result.confirm) return

      resetConversation()
      uni.showToast({
        title: '已开始新对话',
        icon: 'none'
      })
    }
  })
}

const getUserToken = () => {
  const token = uni.getStorageSync('Token')
  if (token) return token
  return uni.getStorageSync('loginResult')?.accessToken || ''
}

const checkAgentHealth = async () => {
  try {
    const response = await fetch(`${agentApi}/health`, {
      headers: { Accept: 'application/json' }
    })
    agentStatus.value = response.ok ? 'online' : 'offline'
  } catch (error) {
    agentStatus.value = 'offline'
  }
}

const promptLogin = (message = '登录后即可使用智能助手咨询商品和订单。') => {
  uni.showModal({
    title: '请先登录',
    content: message,
    cancelText: '稍后',
    confirmText: '去登录',
    success: (result) => {
      if (result.confirm) {
        uni.navigateTo({ url: '/pages/accountLogin/accountLogin' })
      }
    }
  })
}

const createRequestId = () => {
  return `mall-agent-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const getConversationId = () => {
  const storedConversationId = uni.getStorageSync(CONVERSATION_STORAGE_KEY) || ''
  if (storedConversationId !== conversationId.value) {
    conversationId.value = storedConversationId
  }
  return conversationId.value
}

const saveConversationId = (nextConversationId) => {
  if (!nextConversationId || nextConversationId === conversationId.value) return
  conversationId.value = nextConversationId
  uni.setStorageSync(CONVERSATION_STORAGE_KEY, nextConversationId)
}

const createPendingApproval = (data, assistantMessage = null) => {
  if (
    !data?.conversation_id ||
    !data?.interrupt_id ||
    !Array.isArray(data?.actions) ||
    data.actions.length === 0
  ) {
    throw new Error('智能助手返回的审批信息格式异常')
  }

  saveConversationId(data.conversation_id)

  return {
    conversationId: data.conversation_id,
    interruptId: data.interrupt_id,
    reviewConfigs: Array.isArray(data.review_configs) ? data.review_configs : [],
    assistantMessage,
    actions: data.actions.map((action) => ({
      name: action?.name || 'unknown',
      displayName: APPROVAL_TOOL_NAMES[action?.name] || '商城数据变更',
      description: APPROVAL_TOOL_DESCRIPTIONS[action?.name] ||
        action?.description ||
        '该操作将修改商城数据。'
    }))
  }
}

const clearExpiredLogin = () => {
  uni.removeStorageSync('expiresTimeStamp')
  uni.removeStorageSync('isRefreshingToken')
  uni.removeStorageSync('loginResult')
  uni.removeStorageSync('Token')
}

const applyHistoryMessages = (history) => {
  messages.value = history.messages.map((message, index) => ({
    id: index + 1,
    role: message.role,
    content: message.content,
    final: true
  }))
  messageId = messages.value.length

  if (messageId > 0) {
    updateScrollPosition(`ai-message-${messageId}`)
  }
}

const finishHistoryLoading = (controller) => {
  if (historyController !== controller) return
  historyController = null
  isHistoryLoading.value = false
}

const loadConversationHistory = async () => {
  const currentConversationId = getConversationId()
  if (
    !currentConversationId ||
    messages.value.length > 0 ||
    isReplying.value ||
    isHistoryLoading.value
  ) return

  const token = getUserToken()
  if (!token) return

  const controller = new AbortController()
  historyController = controller
  isHistoryLoading.value = true

  try {
    const history = await getAgentHistory({
      baseUrl: agentApi,
      token,
      conversationId: currentConversationId,
      signal: controller.signal
    })

    if (
      historyController !== controller ||
      getConversationId() !== currentConversationId
    ) return

    if (!history.exists) {
      conversationId.value = ''
      uni.removeStorageSync(CONVERSATION_STORAGE_KEY)
      return
    }

    applyHistoryMessages(history)
  } catch (error) {
    if (error.name === 'AbortError') return

    if (error.status === 401) {
      clearExpiredLogin()
      promptLogin('登录状态已过期，请重新登录后继续使用智能助手。')
    } else {
      uni.showToast({
        title: error.message || '聊天记录加载失败',
        icon: 'none'
      })
    }
  } finally {
    finishHistoryLoading(controller)
  }
}

const sendMessage = () => {
  if (
    isReplying.value ||
    isHistoryLoading.value ||
    pendingApproval.value
  ) return

  const token = getUserToken()
  if (!token) {
    promptLogin()
    return
  }

  const content = inputValue.value.trim()
  if (!content) {
    uni.showToast({
      title: '请输入你想咨询的问题',
      icon: 'none'
    })
    return
  }

  messageId += 1
  messages.value.push({
    id: messageId,
    role: 'user',
    content
  })
  inputValue.value = ''
  isReplying.value = true
  replyStatus.value = '正在连接智能助手'
  updateScrollPosition('ai-message-loading')

  const assistantMessage = {
    id: messageId + 1,
    role: 'assistant',
    content: '',
    final: false
  }
  let assistantMessageAdded = false

  const ensureAssistantMessage = () => {
    if (assistantMessageAdded) return
    messageId = assistantMessage.id
    messages.value.push(assistantMessage)
    assistantMessageAdded = true
  }

  const controller = new AbortController()
  requestController = controller

  streamAgentReply({
    baseUrl: agentApi,
    token,
    message: content,
    conversationId: getConversationId(),
    requestId: createRequestId(),
    signal: controller.signal,
    onEvent: ({ type, data }) => {
      if (type === 'start') {
        saveConversationId(data.conversation_id)
      } else if (type === 'status') {
        replyStatus.value = data.message || '正在处理'
      } else if (type === 'agent_start') {
        replyStatus.value = '正在查询商城信息'
      } else if (type === 'tool_start') {
        replyStatus.value = '正在获取数据'
      } else if (type === 'message_start') {
        replyStatus.value = '正在生成回复'
      } else if (type === 'token') {
        ensureAssistantMessage()
        assistantMessage.content += data.content || ''
        replyStatus.value = ''
        scheduleScrollPosition(`ai-message-${assistantMessage.id}`)
      } else if (type === 'message_end') {
        ensureAssistantMessage()
        if (typeof data.content === 'string') {
          assistantMessage.content = data.content
        }
        assistantMessage.final = true
      } else if (type === 'approval_required') {
        pendingApproval.value = createPendingApproval(
          data,
          assistantMessageAdded ? assistantMessage : null
        )
        replyStatus.value = ''
        nextTick(() => updateScrollPosition('ai-approval'))
      } else if (type === 'done') {
        saveConversationId(data.conversation_id)
        assistantMessage.final = true
      }
    }
  })
    .then(({ terminalEvent }) => {
      if (terminalEvent === 'approval_required') return

      if (!assistantMessageAdded) {
        ensureAssistantMessage()
        assistantMessage.content = '请求已完成，但没有生成回复内容'
        assistantMessage.final = true
      }
    })
    .catch((error) => {
      if (error.name === 'AbortError') return
      ensureAssistantMessage()
      if (error.status === 401) {
        clearExpiredLogin()
        assistantMessage.content = '登录状态已过期，请重新登录后再试。'
        promptLogin('登录状态已过期，请重新登录后继续使用智能助手。')
      } else if (error.status === 404 || error.status >= 500 || error.name === 'TypeError') {
        agentStatus.value = 'offline'
        assistantMessage.content = '智能助手服务暂时不可用，请稍后重试。'
      } else {
        assistantMessage.content = error.message || '智能助手暂时无法响应，请稍后重试'
      }
      assistantMessage.final = true
    })
    .finally(() => {
      if (requestController !== controller) return

      requestController = null
      isReplying.value = false
      replyStatus.value = ''
      if (pendingApproval.value) {
        updateScrollPosition('ai-approval')
      } else if (assistantMessageAdded) {
        assistantMessage.final = true
        updateScrollPosition(`ai-message-${assistantMessage.id}`)
      }
    })
}

const submitApproval = (decisionType) => {
  if (
    !pendingApproval.value ||
    isApprovalSubmitting.value ||
    isReplying.value
  ) return

  const token = getUserToken()
  if (!token) {
    promptLogin()
    return
  }

  const approval = pendingApproval.value
  pendingApproval.value = null
  const existingAssistantMessage = approval.assistantMessage
  const assistantMessage = existingAssistantMessage || {
    id: messageId + 1,
    role: 'assistant',
    content: '',
    final: false
  }
  let assistantMessageAdded = Boolean(existingAssistantMessage)

  if (assistantMessageAdded) {
    assistantMessage.final = false
  }

  const ensureAssistantMessage = () => {
    if (assistantMessageAdded) return
    messageId = assistantMessage.id
    messages.value.push(assistantMessage)
    assistantMessageAdded = true
  }

  const decisions = approval.actions.map(() => {
    if (decisionType === 'approve') {
      return { type: 'approve' }
    }

    return {
      type: 'reject',
      message: '用户在确认窗口中拒绝执行该操作'
    }
  })

  isApprovalSubmitting.value = true
  isReplying.value = true
  replyStatus.value = '正在取消操作'
  if (decisionType === 'approve') {
    replyStatus.value = '正在执行已确认的操作'
  }
  updateScrollPosition('ai-message-loading')

  const controller = new AbortController()
  requestController = controller

  resumeAgentReply({
    baseUrl: agentApi,
    token,
    conversationId: approval.conversationId,
    interruptId: approval.interruptId,
    decisions,
    requestId: createRequestId(),
    signal: controller.signal,
    onEvent: ({ type, data }) => {
      if (type === 'start') {
        saveConversationId(data.conversation_id)
      } else if (type === 'status') {
        replyStatus.value = data.message || '正在处理审批结果'
      } else if (type === 'agent_start') {
        replyStatus.value = '正在继续处理请求'
      } else if (type === 'tool_start') {
        replyStatus.value = '正在执行已确认的操作'
      } else if (type === 'message_start') {
        replyStatus.value = '正在生成回复'
      } else if (type === 'token') {
        ensureAssistantMessage()
        assistantMessage.content += data.content || ''
        replyStatus.value = ''
        scheduleScrollPosition(`ai-message-${assistantMessage.id}`)
      } else if (type === 'message_end') {
        ensureAssistantMessage()
        if (typeof data.content === 'string') {
          assistantMessage.content = data.content
        }
        assistantMessage.final = true
      } else if (type === 'approval_required') {
        pendingApproval.value = createPendingApproval(
          data,
          assistantMessageAdded ? assistantMessage : null
        )
        replyStatus.value = ''
        nextTick(() => updateScrollPosition('ai-approval'))
      } else if (type === 'done') {
        saveConversationId(data.conversation_id)
        pendingApproval.value = null
        assistantMessage.final = true
      }
    }
  })
    .then(({ terminalEvent }) => {
      if (terminalEvent === 'approval_required') return

      pendingApproval.value = null
      if (!assistantMessageAdded) {
        ensureAssistantMessage()
        assistantMessage.content = '已取消本次操作'
        if (decisionType === 'approve') {
          assistantMessage.content = '操作已执行完成'
        }
        assistantMessage.final = true
      }
    })
    .catch((error) => {
      if (error.name === 'AbortError') return

      ensureAssistantMessage()
      if (error.status === 401) {
        clearExpiredLogin()
        pendingApproval.value = null
        assistantMessage.content = '登录状态已过期，请重新登录后再试。'
        promptLogin('登录状态已过期，请重新登录后继续使用智能助手。')
      } else if (error.status === 409) {
        pendingApproval.value = null
        assistantMessage.content = error.message || '该审批请求已经失效，请重新发起操作。'
      } else if (
        error.status === 404 ||
        error.status >= 500 ||
        error.name === 'TypeError'
      ) {
        pendingApproval.value = approval
        agentStatus.value = 'offline'
        assistantMessage.content = '审批请求处理失败，请稍后重试。'
      } else {
        pendingApproval.value = approval
        assistantMessage.content = error.message || '审批请求处理失败，请稍后重试。'
      }
      assistantMessage.final = true
    })
    .finally(() => {
      if (requestController !== controller) return

      requestController = null
      isReplying.value = false
      isApprovalSubmitting.value = false
      replyStatus.value = ''
      if (pendingApproval.value) {
        updateScrollPosition('ai-approval')
      } else if (assistantMessageAdded) {
        assistantMessage.final = true
        updateScrollPosition(`ai-message-${assistantMessage.id}`)
      }
    })
}

const sendQuickQuestion = (question) => {
  inputValue.value = question
  sendMessage()
}

onMounted(() => {
  nextTick(() => {
    applyStoredEntryPosition()
  })
  uni.$on('mall4j:open-ai-agent', openChat)
  checkAgentHealth()
})

onUnmounted(() => {
  uni.$off('mall4j:open-ai-agent', openChat)
  finishDrag()
  if (scrollTimer) {
    clearTimeout(scrollTimer)
  }
  if (requestController) {
    requestController.abort()
  }
  if (historyController) {
    historyController.abort()
  }
  if (visible.value && isTabPage()) {
    uni.showTabBar({ animation: false })
  }
})
</script>

<style scoped lang="scss">
@use './ai-agent.scss';
</style>

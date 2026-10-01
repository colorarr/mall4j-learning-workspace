const parseSseFrame = (frame) => {
  let type = 'message'
  const dataLines = []

  frame.split(/\r?\n/).forEach((line) => {
    if (!line || line.startsWith(':')) return

    if (line.startsWith('event:')) {
      type = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  })

  if (!dataLines.length) return null

  return {
    type,
    data: JSON.parse(dataLines.join('\n'))
  }
}

const getResponseError = async (response) => {
  let fallbackMessage = '智能助手服务请求失败'
  if (response.status === 401) {
    fallbackMessage = '登录状态已过期，请重新登录'
  } else if (response.status === 404) {
    fallbackMessage = '智能助手服务未连接，请稍后重试'
  } else if (response.status >= 500) {
    fallbackMessage = '智能助手服务暂时不可用，请稍后重试'
  }

  try {
    const data = await response.json()
    if (typeof data?.detail === 'string') return data.detail
    if (typeof data?.message === 'string') return data.message
    if (Array.isArray(data?.detail)) {
      return data.detail.map((item) => item?.msg).filter(Boolean).join('；') || fallbackMessage
    }
  } catch (error) {
    return fallbackMessage
  }

  return fallbackMessage
}

const consumeSseResponse = async ({ response, onEvent }) => {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('text/event-stream') || !response.body) {
    throw new Error('智能助手返回了错误的响应格式')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  let terminalEvent = ''

  const processBuffer = async (flush = false) => {
    while (buffer) {
      const separator = buffer.match(/\r?\n\r?\n/)
      if (!separator || separator.index === undefined) {
        if (!flush) return
      }

      const frameEnd = separator?.index ?? buffer.length
      const frame = buffer.slice(0, frameEnd)
      buffer = separator ? buffer.slice(frameEnd + separator[0].length) : ''

      const event = parseSseFrame(frame)
      if (!event) continue

      if (event.type === 'error') {
        throw new Error(event.data.message || '智能助手执行失败')
      }

      await onEvent(event)
      if (event.type === 'done' || event.type === 'approval_required') {
        terminalEvent = event.type
      }
    }
  }

  try {
    while (true) {
      const { value, done } = await reader.read()
      buffer += decoder.decode(value, { stream: !done })
      await processBuffer(done)
      if (done) break
    }
  } finally {
    reader.releaseLock()
  }

  if (!terminalEvent) {
    throw new Error('智能助手连接提前结束')
  }

  return { terminalEvent }
}

export const getAgentHistory = async ({
  baseUrl,
  token,
  conversationId,
  signal
}) => {
  const encodedConversationId = encodeURIComponent(conversationId)
  const response = await fetch(`${baseUrl}/chat/history/${encodedConversationId}`, {
    headers: {
      Authorization: token,
      Accept: 'application/json'
    },
    signal
  })

  if (!response.ok) {
    const error = new Error(await getResponseError(response))
    error.status = response.status
    throw error
  }

  return response.json()
}

export const streamAgentReply = async ({
  baseUrl,
  token,
  message,
  conversationId,
  requestId,
  signal,
  onEvent
}) => {
  const response = await fetch(`${baseUrl}/chat/stream`, {
    method: 'POST',
    headers: {
      Authorization: token,
      'X-Request-Id': requestId,
      'Content-Type': 'application/json',
      Accept: 'text/event-stream'
    },
    body: JSON.stringify({
      messages: message,
      conversation_id: conversationId || null
    }),
    signal
  })

  if (!response.ok) {
    const error = new Error(await getResponseError(response))
    error.status = response.status
    throw error
  }

  return consumeSseResponse({ response, onEvent })
}

export const resumeAgentReply = async ({
  baseUrl,
  token,
  conversationId,
  interruptId,
  decisions,
  requestId,
  signal,
  onEvent
}) => {
  const response = await fetch(`${baseUrl}/chat/resume`, {
    method: 'POST',
    headers: {
      Authorization: token,
      'X-Request-Id': requestId,
      'Content-Type': 'application/json',
      Accept: 'text/event-stream'
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      interrupt_id: interruptId,
      decisions
    }),
    signal
  })

  if (!response.ok) {
    const error = new Error(await getResponseError(response))
    error.status = response.status
    throw error
  }

  return consumeSseResponse({ response, onEvent })
}

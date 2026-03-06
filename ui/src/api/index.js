const BASE = '/smart/menu'

/**
 * 获取所有菜单项
 */
export async function fetchMenus() {
  const res = await fetch(`${BASE}/query/menus`, {
    credentials: 'include',
  })
  if (!res.ok) throw new Error('菜单加载失败')
  return res.json()
}

/**
 * 配送地址校验
 * @param {string} address
 */
export async function checkDelivery(address) {
  const res = await fetch(`${BASE}/query/delivery`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address }),
  })
  if (!res.ok) throw new Error('地址查询失败')
  return res.json()
}

/**
 * 开启新对话
 */
export async function newChat() {
  const res = await fetch(`${BASE}/new/chat`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) throw new Error('新对话请求失败')
  return res.json()
}

/**
 * 聊天接口
 * @param {string} query
 */
export async function sendChat(query) {
  const params = new URLSearchParams({ query })
  const res = await fetch(`${BASE}/chat?${params}`, {
    credentials: 'include',
  })
  if (!res.ok) throw new Error('对话请求失败')
  return res.json()
}
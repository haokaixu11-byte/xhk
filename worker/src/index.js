/**
 * ProtoFlow API Worker
 * 提供原型分享数据的存储和读取服务
 *
 * POST /api/share        - 保存原型数据，返回 shareId
 * GET  /api/share/:id    - 读取原型数据
 */

const ALLOWED_ORIGINS = [
  'https://protoflow-editor.pages.dev',
  'http://localhost:3000',
  'http://localhost:5173',
]

// KV 中每条记录最多保留 180 天（秒）
const TTL_SECONDS = 180 * 24 * 60 * 60

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || ''
  // Allow protoflow-editor.pages.dev and any preview deploy subdomains
  const isAllowed = ALLOWED_ORIGINS.includes(origin) ||
    /^https:\/\/[a-z0-9-]+\.protoflow-editor\.pages\.dev$/.test(origin)
  const allowedOrigin = isAllowed ? origin : ALLOWED_ORIGINS[0]
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  }
}

function jsonResponse(data, status = 200, request) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
      ...corsHeaders(request),
    },
  })
}

function generateId() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  let id = ''
  // 使用 crypto.getRandomValues 生成安全随机 ID
  const arr = new Uint8Array(12)
  crypto.getRandomValues(arr)
  for (const byte of arr) {
    id += chars[byte % chars.length]
  }
  return id
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    const method = request.method

    // 处理 CORS 预检请求
    if (method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request) })
    }

    // 健康检查 (must be before other routes)
    if (url.pathname === '/api/health') {
      return jsonResponse({ status: 'ok', service: 'ProtoFlow API' }, 200, request)
    }

    // POST /api/share — 保存原型数据
    if (method === 'POST' && url.pathname === '/api/share') {
      try {
        const body = await request.json()
        if (!body || !body.pages) {
          return jsonResponse({ error: '无效的原型数据，缺少 pages 字段' }, 400, request)
        }

        // 如果客户端传来了已有的 shareId（更新场景），复用它；否则生成新的
        const shareId = (body.shareId && /^[a-z0-9]{8,16}$/.test(body.shareId))
          ? body.shareId
          : generateId()

        const record = {
          id: shareId,
          title: body.title || '未命名原型',
          pages: body.pages,
          createdAt: body.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }

        await env.PROTO_SHARES.put(shareId, JSON.stringify(record), {
          expirationTtl: TTL_SECONDS,
        })

        return jsonResponse({ success: true, shareId }, 200, request)
      } catch (err) {
        return jsonResponse({ error: '保存失败：' + err.message }, 500, request)
      }
    }

    // GET /api/share/:id — 读取原型数据
    const matchGet = url.pathname.match(/^\/api\/share\/([a-z0-9]{8,16})$/)
    if (method === 'GET' && matchGet) {
      const shareId = matchGet[1]
      try {
        const raw = await env.PROTO_SHARES.get(shareId)
        if (!raw) {
          return jsonResponse({ error: '找不到该分享，可能已过期（保存180天）' }, 404, request)
        }
        const record = JSON.parse(raw)
        return jsonResponse({ success: true, data: record }, 200, request)
      } catch (err) {
        return jsonResponse({ error: '读取失败：' + err.message }, 500, request)
      }
    }

    return jsonResponse({ error: '接口不存在' }, 404, request)
  },
}

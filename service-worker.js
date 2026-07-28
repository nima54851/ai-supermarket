// AI超市 Service Worker v5 - HTML永不走缓存，确保商品实时更新
const CACHE_NAME = 'ai-supermarket-v5';

// 核心资源（只缓存静态资源，不缓存HTML）
const PRECACHE = [
  '/ai-supermarket/manifest.json',
];

// Install: 预缓存 + 跳过等待
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(c => c.addAll(PRECACHE).catch(() => {}))
      .then(() => self.skipWaiting())
  );
});

// Activate: 清理旧缓存 + 声明控制权
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch: HTML 文件永远从网络拿（保证最新内容），其他资源缓存
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = e.request.url;
  // HTML 永远走网络，不缓存
  if (url.endsWith('.html') || url.endsWith('/') || url.includes('index.html')) {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    return;
  }
  // 静态资源：网络优先，失败用缓存
  e.respondWith(
    fetch(e.request)
      .then(res => {
        if (res && res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone)).catch(() => {});
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});

// ── Web Push 通知（需要 VAPID 公钥配置）───────────────
self.addEventListener('push', e => {
  if (!e.data) return;
  let data;
  try { data = e.data.json(); } catch { data = { title: '🛒 AI超市', body: e.data.text() }; }

  const opts = {
    body: data.body || '有新品上架，快来看看！',
    icon: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"%3E%3Crect width="192" height="192" rx="36" fill="%236366f1"/%3E%3Ctext x="96" y="128" font-size="110" text-anchor="middle"%3E%F0%9F%9B%92%3C/text%3E%3C/svg%3E',
    badge: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"%3E%3Crect width="96" height="96" rx="18" fill="%236366f1"/%3E%3Ctext x="48" y="68" font-size="55" text-anchor="middle"%3E%F0%9F%9B%92%3C/text%3E%3C/svg%3E',
    vibrate: [300, 100, 300],
    tag: 'ai-market-v4',
    renotify: true,
    requireInteraction: false,
    data: { url: data.url || '/ai-supermarket/#products' },
    actions: [
      { action: 'view', title: '🔍 立即查看' },
      { action: 'dismiss', title: '⏰ 稍后' }
    ]
  };

  e.waitUntil(self.registration.showNotification(data.title || '🛒 AI超市 · 新品上架！', opts));
});

// 通知点击
self.addEventListener('notificationclick', e => {
  e.notification.close();
  if (e.action === 'dismiss') return;
  e.waitUntil(clients.openWindow(e.notification.data.url || '/ai-supermarket/'));
});

// 定期新品检测（Background Sync）
self.addEventListener('periodicsync', e => {
  if (e.tag === 'check-new-products') e.waitUntil(checkNewProducts());
});

async function checkNewProducts() {
  try {
    const r = await fetch('https://api.github.com/repos/nima54851/ai-supermarket/releases/latest', {
      headers: { 'Authorization': 'token ', 'Accept': 'application/vnd.github+json' }
    });
    if (!r.ok) return;
    const d = await r.json();
    const last = localStorage ? localStorage.getItem('ai_market_last_release') : null;
    if (d.published_at && d.published_at !== last) {
      if (typeof localStorage !== 'undefined') localStorage.setItem('ai_market_last_release', d.published_at);
      await self.registration.showNotification('🛒 AI超市 · 新品发布！', {
        body: d.tag_name ? `v${d.tag_name} 上线，快来抢购！` : '有新的AI技能包发布了！',
        icon: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"%3E%3Crect width="192" height="192" rx="36" fill="%236366f1"/%3E%3Ctext x="96" y="128" font-size="110" text-anchor="middle"%3E%F0%9F%9B%92%3C/text%3E%3C/svg%3E',
        badge: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"%3E%3Crect width="96" height="96" rx="18" fill="%236366f1"/%3E%3Ctext x="48" y="68" font-size="55" text-anchor="middle"%3E%F0%9F%9B%92%3C/text%3E%3C/svg%3E',
        tag: 'new-product-v4',
        data: { url: '/ai-supermarket/#products' }
      });
    }
  } catch(_) {}
}

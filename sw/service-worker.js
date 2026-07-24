// AI超市 Service Worker v3 - 全面离线 + 新品推送通知
const CACHE_NAME = 'ai-supermarket-v3';

// 核心资源（预缓存）
const PRECACHE = [
  '/ai-supermarket/',
  '/ai-supermarket/index.html',
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

// Fetch: 网络优先，失败用缓存兜底
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
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
    tag: 'ai-market-v3',
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
        tag: 'new-product-v3',
        data: { url: '/ai-supermarket/#products' }
      });
    }
  } catch(_) {}
}

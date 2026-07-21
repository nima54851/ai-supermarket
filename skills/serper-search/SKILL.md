# Serper.dev Search API — Skill

> Google Search API via Serper.dev，支持 search / images / videos / news / shopping 五种类型。

## 凭证

- **API Key:** `a1e27f773565e1f150d753e3f8b2b889012434a3`
- **Base URL:** `https://google.serper.dev`

## API 端点

| 类型 | 端点 | 说明 |
|------|------|------|
| search | `POST /search` | 网页搜索 |
| images | `POST /images` | 图片搜索 |
| videos | `POST /videos` | 视频搜索 |
| news | `POST /news` | 新闻搜索 |
| shopping | `POST /shopping` | 购物搜索 |

## 请求格式

```bash
curl -s -X POST "https://google.serper.dev/{endpoint}" \
  -H "X-API-Key: a1e27f773565e1f150d753e3f8b2b889012434a3" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "搜索关键词",
    "num": 10,
    "page": 1,
    "gl": "cn",
    "hl": "zh-cn"
  }'
```

### 常用参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `q` | string | 必填 | 搜索关键词 |
| `num` | int | 10 | 结果数量（1-100） |
| `page` | int | 1 | 页码 |
| `gl` | string | "us" | 国家（gl=cn 中国） |
| `hl` | string | "en-US" | 语言（hl=zh-cn 中文） |
| `engine` | string | "google" | 搜索引擎（仅支持 google） |

## 返回字段速查

### search 返回字段

```json
{
  "searchParameters": { "q": "...", "type": "search", "num": 10 },
  "organic": [
    {
      "title": "标题",
      "link": "https://...",
      "snippet": "摘要",
      "position": 1
    }
  ],
  "relatedSearches": [{ "query": "相关搜索词" }],
  "peopleAlsoAsk": [
    {
      "question": "问题",
      "answer": "答案",
      "link": "链接",
      "snippet": "来源"
    }
  ]
}
```

### images 返回字段

```json
{
  "searchParameters": { "type": "images" },
  "images": [
    {
      "title": "标题",
      "imageUrl": "https://...",
      "source": "来源",
      "link": "页面链接",
      "thumbnailUrl": "缩略图"
    }
  ]
}
```

### videos 返回字段

```json
{
  "videos": [
    {
      "title": "标题",
      "link": "https://...",
      "thumbnail": "缩略图URL",
      "duration": "时长",
      "source": "来源平台"
    }
  ]
}
```

## Python 使用示例

```python
import requests

API_KEY = "a1e27f773565e1f150d753e3f8b2b889012434a3"
BASE = "https://google.serper.dev"

def search(query, num=10, gl="cn", hl="zh-cn"):
    resp = requests.post(
        f"{BASE}/search",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": num, "gl": gl, "hl": hl}
    )
    resp.raise_for_status()
    return resp.json()

def search_images(query, num=10):
    resp = requests.post(
        f"{BASE}/images",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": num}
    )
    resp.raise_for_status()
    return resp.json()

def search_news(query, num=10):
    resp = requests.post(
        f"{BASE}/news",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": num}
    )
    resp.raise_for_status()
    return resp.json()
```

## Node.js 使用示例

```javascript
const axios = require('axios');

const API_KEY = 'a1e27f773565e1f150d753e3f8b2b889012434a3';
const BASE = 'https://google.serper.dev';

async function search(query, num = 10) {
  const resp = await axios.post(`${BASE}/search`, {
    q: query,
    num,
    gl: 'cn',
    hl: 'zh-cn'
  }, {
    headers: { 'X-API-Key': API_KEY, 'Content-Type': 'application/json' }
  });
  return resp.data;
}
```

## n8n HTTP Request 节点配置

```
Method: POST
URL: https://google.serper.dev/search
Headers:
  X-API-Key: a1e27f773565e1f150d753e3f8b2b889012434a3
  Content-Type: application/json
Body (JSON):
{
  "q": "{{ $json.query }}",
  "num": 10,
  "gl": "cn",
  "hl": "zh-cn"
}
```

## 配额说明

- 免费额度：每月 2,500 次搜索
- 按量付费：超出后 $0.001/次（搜索）/ $0.005/次（图片/视频）
- Dashboard: https://serper.dev/dashboard

## 注意事项

- 搜索请求是 POST，不是 GET
- Header 用 `X-API-Key`，不是 `Authorization: Bearer`
- `gl=cn` + `hl=zh-cn` 可获取中文结果
- `num` 最大 100，分页用 `page` 参数

---

*创建于: 2026-07-08*

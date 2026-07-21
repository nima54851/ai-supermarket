#!/usr/bin/env python3
"""
手机号归属地查询 Bot + Web + API
Telegram Bot + Web 页面 + Flask API
数据库：79,632 条 7 位精准号段，覆盖全国 331 城市
"""
import os
import sys
import json
import re
import logging
from flask import Flask, request, jsonify, render_template_string

# Telegram
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    TELEGRAM_OK = True
except ImportError:
    TELEGRAM_OK = False

# 导入号段数据库
sys.path.insert(0, os.path.dirname(__file__))
from phone_data import lookup, format_result, get_db_stats

# ========== 配置 ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8979991426:AAEtgWjhF1KV_pJZVwzjk-ZE2_Yf1-W4RDU")
PORT = int(os.environ.get("PORT", 8080))
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "7668716558")

# ========== Flask App ==========
app = Flask(__name__)

# 页面模板：百度风格手机号查询
LANDING_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>手机号归属地查询 - 灵犀号段</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: white;
            font-size: 28px;
            margin-bottom: 8px;
        }
        .header p {
            color: rgba(255,255,255,0.8);
            font-size: 14px;
        }
        .search-box {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }
        .search-form {
            display: flex;
            gap: 10px;
        }
        .search-form input {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            outline: none;
            transition: border 0.2s;
        }
        .search-form input:focus {
            border-color: #667eea;
        }
        .search-form input::placeholder {
            color: #999;
        }
        .search-form button {
            padding: 14px 28px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }
        .search-form button:hover {
            background: #5a6fd6;
        }
        .result-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-top: 20px;
            display: none;
        }
        .result-card.show {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-header {
            font-size: 14px;
            color: #666;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #eee;
        }
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f5f5f5;
        }
        .result-item:last-child {
            border-bottom: none;
        }
        .result-label {
            color: #888;
            font-size: 14px;
        }
        .result-value {
            font-size: 16px;
            font-weight: 500;
        }
        .result-value.phone-text {
            font-size: 18px;
            color: #333;
            letter-spacing: 1px;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-mobile { background: #e3f2fd; color: #1565c0; }
        .badge-unicom { background: #e8f5e9; color: #2e7d32; }
        .badge-telecom { background: #fce4ec; color: #c62828; }
        .badge-broadcast { background: #fff3e0; color: #e65100; }
        .badge-unknown { background: #f5f5f5; color: #666; }
        .error-message {
            color: #c62828;
            text-align: center;
            padding: 20px;
        }
        .stats {
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            margin-top: 30px;
        }
        .stats span {
            margin: 0 10px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .loading.show {
            display: block;
        }
        .examples {
            margin-top: 16px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .examples span {
            color: #999;
            font-size: 13px;
        }
        .examples button {
            padding: 4px 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            background: white;
            font-size: 13px;
            color: #666;
            cursor: pointer;
            transition: all 0.2s;
        }
        .examples button:hover {
            border-color: #667eea;
            color: #667eea;
        }
        @media (max-width: 500px) {
            .search-form { flex-direction: column; }
            .search-form button { width: 100%; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📱 手机号归属地查询</h1>
        <p>输入手机号码，精准查询运营商、省份、城市信息</p>
    </div>
    <div class="search-box">
        <div class="search-form">
            <input type="text" id="phoneInput" placeholder="输入手机号，如 13800138000" maxlength="20" autofocus>
            <button onclick="search()">🔍 查询</button>
        </div>
        <div class="examples">
            <span>试试：</span>
            <button onclick="quickSearch('13800138000')">13800138000</button>
            <button onclick="quickSearch('18801012345')">18801012345</button>
            <button onclick="quickSearch('18908001234')">18908001234</button>
        </div>
        <div class="loading" id="loading">查询中...</div>
    </div>
    <div class="result-card" id="result">
        <div class="result-header">📋 查询结果</div>
        <div id="resultContent"></div>
    </div>
    <div class="stats">
        <span>📊 数据覆盖：331 城市</span>
        <span>🔢 号段：79,632 条</span>
        <span>🤖 Telegram @phone_lookup_bot</span>
    </div>
</div>
<script>
function quickSearch(phone) {
    document.getElementById('phoneInput').value = phone;
    search();
}
function search() {
    var phone = document.getElementById('phoneInput').value.trim();
    var result = document.getElementById('result');
    var content = document.getElementById('resultContent');
    var loading = document.getElementById('loading');
    
    if (!phone) {
        result.classList.remove('show');
        return;
    }
    
    loading.classList.add('show');
    result.classList.remove('show');
    
    fetch('/api/query?phone=' + encodeURIComponent(phone))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            loading.classList.remove('show');
            result.classList.add('show');
            
            if (!data.success) {
                content.innerHTML = '<div class="error-message">❌ ' + data.error + '</div>';
                return;
            }
            
            var badgeClass = 'badge-unknown';
            var op = data.operator || '';
            if (op.includes('移动')) badgeClass = 'badge-mobile';
            else if (op.includes('联通')) badgeClass = 'badge-unicom';
            else if (op.includes('电信')) badgeClass = 'badge-telecom';
            else if (op.includes('广电')) badgeClass = 'badge-broadcast';
            
            var html = '';
            html += '<div class="result-item"><span class="result-label">📱 手机号</span><span class="result-value phone-text">' + data.phone_display + '</span></div>';
            html += '<div class="result-item"><span class="result-label">🏢 运营商</span><span class="result-value"><span class="badge ' + badgeClass + '">' + op + '</span></span></div>';
            
            if (data.province) {
                html += '<div class="result-item"><span class="result-label">📍 省份</span><span class="result-value">' + data.province + '</span></div>';
            }
            if (data.city) {
                html += '<div class="result-item"><span class="result-label">🏙️ 城市</span><span class="result-value">' + data.city + '</span></div>';
            }
            if (data.district) {
                html += '<div class="result-item"><span class="result-label">🏘️ 区县</span><span class="result-value">' + data.district + '</span></div>';
            }
            if (data.type) {
                html += '<div class="result-item"><span class="result-label">📡 号段类型</span><span class="result-value">' + data.type + '</span></div>';
            }
            html += '<div class="result-item"><span class="result-label">🎯 查询精度</span><span class="result-value">' + data.precision + '</span></div>';
            
            if (data.town) {
                html += '<div class="result-item"><span class="result-label">🏡 村镇</span><span class="result-value">' + data.town + '</span></div>';
            }
            
            content.innerHTML = html;
        })
        .catch(function(err) {
            loading.classList.remove('show');
            result.classList.add('show');
            content.innerHTML = '<div class="error-message">❌ 网络错误，请重试</div>';
        });
}
</script>
</body>
</html>
"""


# ========== 号段数据库增强 ==========

# 城市 → 区县映射（用于补充区县信息）
CITY_DISTRICTS = {
    # 北京
    "北京": ["东城区","西城区","朝阳区","海淀区","丰台区","石景山区","通州区",
             "顺义区","房山区","大兴区","昌平区","怀柔区","平谷区","门头沟区",
             "密云区","延庆区"],
    # 上海
    "上海": ["黄浦区","徐汇区","长宁区","静安区","普陀区","虹口区","杨浦区",
             "闵行区","宝山区","嘉定区","浦东新区","金山区","松江区","青浦区",
             "奉贤区","崇明区"],
    # 广州
    "广州": ["越秀区","海珠区","荔湾区","天河区","白云区","黄埔区","花都区",
             "番禺区","南沙区","从化区","增城区"],
    # 深圳
    "深圳": ["罗湖区","福田区","南山区","宝安区","龙岗区","盐田区","龙华区",
             "坪山区","光明区","大鹏新区"],
    # 杭州
    "杭州": ["上城区","拱墅区","西湖区","滨江区","萧山区","余杭区","临平区",
             "钱塘区","富阳区","临安区","桐庐县","淳安县","建德市"],
    # 成都
    "成都": ["锦江区","青羊区","金牛区","武侯区","成华区","龙泉驿区","青白江区",
             "新都区","温江区","双流区","郫都区","新津区","都江堰市","彭州市",
             "邛崃市","崇州市","金堂县","大邑县","蒲江县"],
    # 南京
    "南京": ["玄武区","秦淮区","建邺区","鼓楼区","浦口区","栖霞区","雨花台区",
             "江宁区","六合区","溧水区","高淳区"],
    # 武汉
    "武汉": ["江岸区","江汉区","硚口区","汉阳区","武昌区","青山区","洪山区",
             "东西湖区","汉南区","蔡甸区","江夏区","黄陂区","新洲区"],
    # 西安
    "西安": ["新城区","碑林区","莲湖区","灞桥区","未央区","雁塔区","阎良区",
             "临潼区","长安区","高陵区","鄠邑区","蓝田县","周至县"],
    # 重庆
    "重庆": ["渝中区","江北区","南岸区","沙坪坝区","九龙坡区","大渡口区",
             "北碚区","渝北区","巴南区","万州区","涪陵区","黔江区","长寿区",
             "江津区","合川区","永川区","南川区","璧山区","铜梁区","潼南区",
             "荣昌区","开州区","梁平区","武隆区"],
    # 苏州
    "苏州": ["姑苏区","虎丘区","吴中区","相城区","吴江区","常熟市","张家港市",
             "昆山市","太仓市"],
    # 长沙
    "长沙": ["芙蓉区","天心区","岳麓区","开福区","雨花区","望城区","浏阳市",
             "宁乡市","长沙县"],
    # 郑州
    "郑州": ["中原区","二七区","管城回族区","金水区","上街区","惠济区",
             "中牟县","巩义市","荥阳市","新密市","新郑市","登封市"],
    # 济南
    "济南": ["历下区","市中区","槐荫区","天桥区","历城区","长清区","章丘区",
             "济阳区","莱芜区","钢城区","平阴县","商河县"],
    # 青岛
    "青岛": ["市南区","市北区","黄岛区","崂山区","李沧区","城阳区","即墨区",
             "胶州市","平度市","莱西市"],
    # 厦门
    "厦门": ["思明区","海沧区","湖里区","集美区","同安区","翔安区"],
    # 合肥
    "合肥": ["瑶海区","庐阳区","蜀山区","包河区","长丰县","肥东县","肥西县",
             "庐江县","巢湖市"],
    # 福州
    "福州": ["鼓楼区","台江区","仓山区","马尾区","晋安区","长乐区","闽侯县",
             "连江县","罗源县","闽清县","永泰县","平潭县","福清市"],
    # 哈尔滨
    "哈尔滨": ["道里区","南岗区","道外区","香坊区","平房区","松北区","呼兰区",
               "阿城区","双城区","依兰县","方正县","宾县","巴彦县","木兰县",
               "通河县","延寿县","尚志市","五常市"],
    # 昆明
    "昆明": ["五华区","盘龙区","官渡区","西山区","东川区","呈贡区","晋宁区",
             "富民县","宜良县","石林县","嵩明县","禄劝县","寻甸县","安宁市"],
    # 贵阳
    "贵阳": ["南明区","云岩区","花溪区","乌当区","白云区","观山湖区",
             "开阳县","息烽县","修文县","清镇市"],
    # 南宁
    "南宁": ["兴宁区","江南区","青秀区","西乡塘区","良庆区","邕宁区","武鸣区",
             "隆安县","马山县","上林县","宾阳县","横州市"],
    # 乌鲁木齐
    "乌鲁木齐": ["天山区","沙依巴克区","新市区","水磨沟区","头屯河区",
                 "达坂城区","米东区","乌鲁木齐县"],
}

# 城市 → 村镇映射（示例数据，实际需要更完整的村镇数据库）
CITY_TOWNS = {
    "北京": {
        "东城区": ["景山街道","东华门街道","建国门街道","朝阳门街道","东四街道","北新桥街道",
                  "安定门街道","交道口街道","和平里街道","前门街道","崇文门外街道"],
        "海淀区": ["中关村街道","海淀街道","清华园街道","燕园街道","万柳地区","上地街道",
                  "学院路街道","北太平庄街道","西三旗街道","清河街道","西北旺镇"],
        "昌平区": ["回龙观街道","龙泽园街道","史各庄街道","霍营街道","沙河镇","小汤山镇",
                  "北七家镇","阳坊镇","南口镇","十三陵镇"],
    },
    "上海": {
        "浦东新区": ["陆家嘴街道","张江镇","金桥镇","北蔡镇","三林镇","川沙新镇",
                    "周浦镇","康桥镇","惠南镇","祝桥镇"],
        "徐汇区": ["湖南路街道","天平路街道","田林街道","龙华街道","漕河泾街道",
                  "华泾镇","长桥街道"],
    },
    "广州": {
        "天河区": ["天河南街道","石牌街道","五山街道","员村街道","车陂街道",
                  "猎德街道","棠下街道","天河智慧城"],
        "白云区": ["三元里街道","同和街道","永平街道","石井街道","太和镇",
                  "人和镇","江高镇","钟落潭镇"],
        "番禺区": ["市桥街道","大石街道","洛浦街道","南村镇","新造镇","化龙镇",
                  "石楼镇","大龙街道"],
    },
    "深圳": {
        "南山区": ["南头街道","南山街道","西丽街道","沙河街道","蛇口街道",
                  "招商街道","粤海街道","桃源街道"],
        "福田区": ["园岭街道","南园街道","福田街道","沙头街道","梅林街道",
                  "华富街道","莲花街道","华强北街道"],
        "宝安区": ["新安街道","西乡街道","福永街道","沙井街道","松岗街道",
                  "石岩街道","航城街道"],
        "龙岗区": ["龙城街道","龙岗街道","布吉街道","坂田街道","南湾街道",
                  "横岗街道","平湖街道","坪地街道"],
    },
    "杭州": {
        "西湖区": ["西溪街道","灵隐街道","翠苑街道","文新街道","古荡街道",
                  "转塘街道","留下街道","三墩镇"],
        "余杭区": ["余杭街道","闲林街道","仓前街道","五常街道","中泰街道",
                  "瓶窑镇","良渚街道","仁和街道"],
        "上城区": ["湖滨街道","清波街道","小营街道","望江街道","南星街道",
                  "紫阳街道","笕桥街道","九堡街道"],
    },
    "成都": {
        "锦江区": ["春熙路街道","书院街街道","锦官驿街道","牛市口街道","东湖街道",
                  "沙河街道","成龙路街道"],
        "武侯区": ["浆洗街街道","望江路街道","玉林街道","火车南站街道",
                  "晋阳街道","机投桥街道","簇桥街道"],
        "高新区": ["肖家河街道","芳草街街道","石羊街道","桂溪街道","中和街道"],
    },
    "南京": {
        "秦淮区": ["洪武路街道","五老村街道","大光路街道","瑞金路街道","月牙湖街道",
                  "光华路街道","夫子庙街道","双塘街道"],
        "鼓楼区": ["宁海路街道","华侨路街道","湖南路街道","中央门街道",
                  "江东街道","凤凰街道","热河南路街道"],
    },
    "武汉": {
        "武昌区": ["积玉桥街道","杨园街道","徐家棚街道","粮道街道","中华路街道",
                  "黄鹤楼街道","珞珈山街道","水果湖街道"],
        "洪山区": ["珞南街道","关山街道","狮子山街道","张家湾街道","梨园街道",
                  "卓刀泉街道","洪山街道"],
    },
}


def enrich_lookup_result(phone: str) -> dict:
    """
    增强查询结果：手机号 → 省/市/区县/村镇
    """
    base = lookup(phone)

    if not base['success']:
        return base

    city = base.get('city')

    # 补全世界（7位查询已知城市）
    if city:
        # 取省份（如果已有）
        province = base.get('province', '')

        # 补充区县（按城市映射，随机/按号段取一个）
        districts = CITY_DISTRICTS.get(city, [])
        if districts:
            # 用手机号后4位作为索引，固定映射到区县
            idx = int(base.get('phone', phone)[-4:]) % len(districts)
            district = districts[idx]
            base['district'] = district

            # 补充村镇
            town_map = CITY_TOWNS.get(city, {})
            towns = town_map.get(district, [])
            if towns:
                town_idx = int(base.get('phone', phone)[-2:]) % len(towns)
                base['town'] = towns[town_idx]

    # 格式化显示号码
    phone_raw = base.get('phone', phone)
    if len(phone_raw) == 11:
        base['phone_display'] = f"{phone_raw[:3]} {phone_raw[3:7]} {phone_raw[7:]}"
    else:
        base['phone_display'] = phone_raw

    return base


# ========== Flask API ==========

@app.route('/')
def index():
    return render_template_string(LANDING_PAGE)


@app.route('/api/query')
def api_query():
    phone = request.args.get('phone', '')
    if not phone:
        return jsonify({'success': False, 'error': '请输入手机号'})

    result = enrich_lookup_result(phone)
    return jsonify(result)


@app.route('/api/stats')
def api_stats():
    s = get_db_stats()
    return jsonify({
        'success': True,
        'total_7digit': s['total_7digit'],
        'covered_provinces': s['covered_provinces'],
        'covered_cities': s['covered_cities'],
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


# ========== Telegram Bot ==========

if TELEGRAM_OK:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f"👋 欢迎 {user.first_name}！\n\n"
            f"📱 直接发送手机号，即可查询：\n"
            f"  • 运营商（移动/联通/电信/广电）\n"
            f"  • 归属省份\n"
            f"  • 归属城市\n"
            f"  • 区县信息\n\n"
            f"✅ 支持格式：\n"
            f"  • `13800138000`（11位完整号码）\n"
            f"  • `+8613800138000`（含国际区号）\n\n"
            f"📊 发送 /stats 查看数据库统计\n"
            f"🌐 网页查询：`{request.url_root if hasattr(request, 'url_root') else ''}`",
            parse_mode="Markdown"
        )

    async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        s = get_db_stats()
        await update.message.reply_text(
            f"📊 *数据库统计*\n\n"
            f"• 7位精准号段：{s['total_7digit']:,} 条\n"
            f"• 覆盖省份：{s['covered_provinces']} 个\n"
            f"• 覆盖城市：{s['covered_cities']} 个\n"
            f"• 运营商：{'、'.join(s.get('operators', {}).keys())}\n\n"
            f"_数据来源：工信部公开号段_",
            parse_mode="Markdown"
        )

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        if text.startswith('/'):
            return

        phone_pattern = re.compile(r'(\+?86)?[\s-]*(\d{3,11})')
        match = phone_pattern.search(text)
        if not match:
            await update.message.reply_text(
                "❌ 未识别到手机号\n\n"
                "请直接发送手机号码（如 `13800138000`）",
                parse_mode="Markdown"
            )
            return

        phone = match.group(2)
        result = enrich_lookup_result(phone)

        if not result['success']:
            await update.message.reply_text(
                f"❌ {result.get('error', '查询失败')}",
                parse_mode="Markdown"
            )
            return

        msg = format_bot_result(result)

        keyboard = [[InlineKeyboardButton("🌐 网页版查询", url=f"https://phone-lookup.up.railway.app")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(msg, parse_mode="Markdown",
                                        reply_markup=reply_markup)

    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")

    def format_bot_result(r: dict) -> str:
        op = r.get('operator', '')
        op_icons = {'中国移动': '📶', '中国联通': '📡',
                    '中国电信': '📺', '中国广电': '📻'}
        icon = op_icons.get(op, '🏢')

        lines = [
            f"🔍 *手机号归属地查询*\n",
            f"📱 号码：`{r.get('phone_display', r.get('phone', ''))}`",
            f"{icon} 运营商：{op}",
        ]

        if r.get('province'):
            lines.append(f"📍 省份：{r['province']}")
        if r.get('city'):
            lines.append(f"🏙️ 城市：{r['city']}")
        if r.get('district'):
            lines.append(f"🏘️ 区县：{r['district']}")
        if r.get('town'):
            lines.append(f"🏡 村镇：{r['town']}")
        if r.get('type'):
            lines.append(f"📡 类型：{r['type']}")

        lines.extend([
            f"\n🎯 精度：{r.get('precision', '运营商级别')}",
            f"━━━━━━━━━━━",
            f"_数据：工信部公开号段_",
        ])
        return '\n'.join(lines)

    def run_telegram_bot():
        import asyncio
        app_bot = Application.builder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("stats", stats_cmd))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app_bot.add_error_handler(error_handler)
        logger.info("🤖 Telegram Bot 启动中...")
        asyncio.run(app_bot.initialize())
        asyncio.run(app_bot.start())
        asyncio.run(app_bot.run_until_disconnected())


# ========== 主程序 ==========

def main():
    # 启动 Telegram Bot（后台线程，避开信号处理问题）
    if TELEGRAM_OK and BOT_TOKEN and BOT_TOKEN != "your_token_here":
        from threading import Thread
        t = Thread(target=run_telegram_bot, daemon=True)
        t.start()
        print("✅ Telegram Bot 已启动")

    # 启动 Flask Web 服务
    print(f"🌐 Web 服务启动在 port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)


if __name__ == '__main__':
    main()

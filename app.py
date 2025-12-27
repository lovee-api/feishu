from flask import Flask, jsonify, render_template
from database import db
from services import AnalyticsService
from feishu_service import FeishuSheetService
import os

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Renamed from hubway.db to ecommerce.db to match new scope
DB_PATH = os.path.join(BASE_DIR, 'ecommerce.db')

# Feishu Configuration
FEISHU_APP_ID = "cli_a9c019d701b8dbc9"
FEISHU_APP_SECRET = "oilqGaONOXLulFiWGpXFmhEO7YNKCQLo"
FEISHU_SPREADSHEET_TOKEN = "HgC9sb5EPhNPFbterr9cr64onyh"
FEISHU_SHEET_ID = "80e00b"  # 商品销售数据
FEISHU_LIVE_SHEET_ID = "lCypKc"  # 直播间数据

app = Flask(__name__)
# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Auto-Import Logic
with app.app_context():
    db.create_all() # Ensure tables exist
    
    # Try importing Excel
    from services import IngestionService
    excel_path = os.path.join(BASE_DIR, '新建 Microsoft Excel 工作表 (2).xlsx')
    IngestionService.import_excel_if_empty(excel_path)

# --- Routes ---

@app.route('/')
def index():
    # Redirect to Sales by default as it is the main view now
    return render_template('dashboard_sales.html', active_page='sales')

@app.route('/dashboard/sales')
def dashboard_sales():
    return render_template('dashboard_sales.html', active_page='sales')

@app.route('/dashboard/service')
def dashboard_service():
    return render_template('dashboard_service.html', active_page='service')

@app.route('/dashboard/feishu-test')
def dashboard_feishu_test():
    return render_template('dashboard_feishu.html', active_page='feishu')

@app.route('/dashboard/live')
def dashboard_live():
    return render_template('dashboard_live.html', active_page='live')

# --- Sales Analysis Routes ---

@app.route('/api/sales/overview')
def get_sales_overview():
    try:
        data = AnalyticsService.get_sales_overview()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales/trend')
def get_sales_trend():
    try:
        data = AnalyticsService.get_sales_trend()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales/funnel')
def get_sales_funnel():
    try:
        data = AnalyticsService.get_sales_funnel()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/service/metrics')
def get_service_metrics():
    try:
        data = AnalyticsService.get_service_metrics()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feishu/data')
def get_feishu_data():
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        return jsonify(parsed_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feishu/overview')
def get_feishu_overview():
    """飞书数据 - KPI 概览"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        # Calculate KPIs
        total_sales = sum(float(str(row.get('支付金额', 0)).replace(',', '')) for row in parsed_data if row.get('支付金额'))
        total_visitors = sum(int(float(str(row.get('访客数', 0)).replace(',', ''))) for row in parsed_data if row.get('访客数'))
        total_orders = sum(int(float(str(row.get('支付子订单数', 0)).replace(',', ''))) for row in parsed_data if row.get('支付子订单数'))
        
        return jsonify({
            "total_sales": round(total_sales, 2),
            "total_visitors": total_visitors,
            "total_orders": total_orders
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feishu/trend')
def get_feishu_trend():
    """飞书数据 - 趋势图"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        # Group by date
        from collections import defaultdict
        daily = defaultdict(lambda: {"sales": 0, "visitors": 0})
        
        for row in parsed_data:
            date = str(row.get('日期', ''))
            if date:
                sales = float(str(row.get('支付金额', 0)).replace(',', '')) if row.get('支付金额') else 0
                visitors = int(float(str(row.get('访客数', 0)).replace(',', ''))) if row.get('访客数') else 0
                daily[date]["sales"] += sales
                daily[date]["visitors"] += visitors
        
        # Sort by date
        result = [{"date": k, "sales": v["sales"], "visitors": v["visitors"]} for k, v in sorted(daily.items())]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feishu/funnel')
def get_feishu_funnel():
    """飞书数据 - 转化漏斗"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        total_visitors = sum(int(float(str(row.get('访客数', 0)).replace(',', ''))) for row in parsed_data if row.get('访客数'))
        total_cart = sum(int(float(str(row.get('加购人数', 0)).replace(',', ''))) for row in parsed_data if row.get('加购人数'))
        total_orders = sum(int(float(str(row.get('支付子订单数', 0)).replace(',', ''))) for row in parsed_data if row.get('支付子订单数'))
        
        return jsonify({
            "visitors": total_visitors,
            "cart": total_cart,
            "orders": total_orders
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feishu/service')
def get_feishu_service():
    """飞书数据 - 服务指标"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        # Calculate averages
        logistics_times = [float(str(row.get('物流到货时长(小时)', 0)).replace(',', '')) for row in parsed_data if row.get('物流到货时长(小时)')]
        chat_times = [float(str(row.get('旺旺人工响应时长(秒)', 0)).replace(',', '')) for row in parsed_data if row.get('旺旺人工响应时长(秒)')]
        refund_times = [float(str(row.get('退款处理时长(天)', 0)).replace(',', '')) for row in parsed_data if row.get('退款处理时长(天)')]
        
        return jsonify({
            "logistics_hours": round(sum(logistics_times) / len(logistics_times), 1) if logistics_times else 0,
            "chat_seconds": round(sum(chat_times) / len(chat_times), 1) if chat_times else 0,
            "refund_days": round(sum(refund_times) / len(refund_times), 1) if refund_times else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# 直播间数据 API (Live Stream Dashboard)
# =============================================

@app.route('/api/live/data')
def get_live_data():
    """直播间原始数据"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_LIVE_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        return jsonify(parsed_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/live/overview')
def get_live_overview():
    """直播间 KPI 概览"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_LIVE_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        def safe_float(val):
            try:
                return float(str(val).replace(',', '').replace('#DIV/0!', '0').replace('######', '0'))
            except:
                return 0
        
        def safe_int(val):
            return int(safe_float(val))
        
        # 累计指标
        total_gmv = sum(safe_float(row.get('直播间GMV', 0)) for row in parsed_data)
        total_uv = sum(safe_int(row.get('直播间访问人数（uv）', 0)) for row in parsed_data)
        total_sessions = sum(safe_int(row.get('开播场次', 0)) for row in parsed_data)
        total_fans = sum(safe_int(row.get('直播间新增粉丝数', 0)) for row in parsed_data)
        
        return jsonify({
            "total_gmv": round(total_gmv, 2),
            "total_uv": total_uv,
            "total_sessions": total_sessions,
            "total_fans": total_fans
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/live/trend')
def get_live_trend():
    """直播间趋势数据"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_LIVE_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        def safe_float(val):
            try:
                return float(str(val).replace(',', '').replace('#DIV/0!', '0').replace('######', '0'))
            except:
                return 0
        
        result = []
        for row in parsed_data:
            date = str(row.get('统计日期', ''))
            if date and date != '统计日期':
                result.append({
                    "date": date,
                    "gmv": safe_float(row.get('直播间GMV', 0)),
                    "uv": safe_float(row.get('直播间访问人数（uv）', 0)),
                    "revenue": safe_float(row.get('直播间营收', 0))
                })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/live/metrics')
def get_live_metrics():
    """直播间效率指标"""
    try:
        feishu = FeishuSheetService(FEISHU_APP_ID, FEISHU_APP_SECRET)
        raw_data = feishu.get_sheet_data(FEISHU_SPREADSHEET_TOKEN, FEISHU_LIVE_SHEET_ID)
        parsed_data = feishu.parse_to_daily_sales(raw_data)
        
        def safe_float(val):
            try:
                v = str(val).replace(',', '').replace('#DIV/0!', '0').replace('######', '0').replace('%', '')
                return float(v)
            except:
                return 0
        
        # 计算平均值
        gpm_list = [safe_float(row.get('GPM（千次展现成交）', 0)) for row in parsed_data if row.get('GPM（千次展现成交）')]
        uv_value_list = [safe_float(row.get('UV价值', 0)) for row in parsed_data if row.get('UV价值')]
        conversion_list = [safe_float(row.get('uv转化率', 0)) for row in parsed_data if row.get('uv转化率')]
        
        return jsonify({
            "avg_gpm": round(sum(gpm_list) / len(gpm_list), 2) if gpm_list else 0,
            "avg_uv_value": round(sum(uv_value_list) / len(uv_value_list), 2) if uv_value_list else 0,
            "avg_conversion": round(sum(conversion_list) / len(conversion_list) * 100, 2) if conversion_list else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

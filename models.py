from database import db

# Mapping 'Sales' from Excel
class DailySales(db.Model):
    __tablename__ = 'daily_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)          # 日期
    category = db.Column(db.String)      # 类别
    payment_amount = db.Column(db.Float) # 支付金额
    visitors = db.Column(db.Integer)     # 访客数
    pay_conversion_rate = db.Column(db.String) # 支付转化率

    # --- Finance & Sales Depth ---
    item_count = db.Column(db.Integer)     # 支付件数
    order_count = db.Column(db.Integer)    # 支付子订单数
    avg_order_value = db.Column(db.Float)  # 客单价
    success_refund_amount = db.Column(db.Float) # 成功退款金额
    item_view_count = db.Column(db.Integer)     # 浏览量

    # --- Conversion Funnel ---
    add_to_cart_users = db.Column(db.Integer)   # 加购人数
    add_to_cart_count = db.Column(db.Integer)   # 加购件数
    consult_rate = db.Column(db.String)         # 咨询率

    # --- Retention (Old Customers) ---
    old_buyer_pay_amount = db.Column(db.Float)  # 老客复购金额
    old_buyer_pay_count = db.Column(db.Integer) # 老客复购人数
    old_buyer_rate = db.Column(db.String)       # 老客复购率
    
    # --- Service & Logistics ---
    chat_response_time = db.Column(db.Float)    # 旺旺人工响应时长(秒)
    logistics_time = db.Column(db.Float)        # 物流到货时长(小时)
    refund_duration = db.Column(db.Float)       # 退款处理时长(天)
    dispute_rate = db.Column(db.String)         # 纠纷投诉商责率
    chat_satisfaction = db.Column(db.String)    # 旺旺满意度

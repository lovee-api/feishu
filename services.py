from sqlalchemy import func, desc
import pandas as pd
import os
from models import DailySales
from database import db

class IngestionService:
    @staticmethod
    def import_excel_if_empty(file_path):
        """
        Check if DailySales is empty. If so, load from Excel.
        """
        if db.session.query(DailySales).first() is not None:
            print("DailySales table already has data. Skipping import.")
            return

        if not os.path.exists(file_path):
            print(f"Excel file not found: {file_path}")
            return

        try:
            print(f"Importing data from {file_path}...")
            df = pd.read_excel(file_path)
            
            # Map columns: Excel -> Model
            for _, row in df.iterrows():
                # Helper to clean numbers (remove , and %)
                def clean_float(val):
                    try:
                        return float(str(val).replace(',', '').replace('%', ''))
                    except:
                        return 0.0
                
                def clean_int(val):
                    try:
                        return int(clean_float(val))
                    except:
                        return 0

                record = DailySales(
                    date = str(row.get('日期', '')),
                    category = str(row.get('类别', '')),
                    payment_amount = clean_float(row.get('支付金额', 0)),
                    visitors = clean_int(row.get('访客数', 0)),
                    pay_conversion_rate = str(row.get('支付转化率', '0%')),
                    
                    # Finance
                    item_count = clean_int(row.get('支付件数', 0)),
                    order_count = clean_int(row.get('支付子订单数', 0)),
                    avg_order_value = clean_float(row.get('客单价', 0)),
                    success_refund_amount = clean_float(row.get('成功退款金额', 0)),
                    item_view_count = clean_int(row.get('浏览量', 0)),

                    # Funnel
                    add_to_cart_users = clean_int(row.get('加购人数', 0)),
                    add_to_cart_count = clean_int(row.get('加购件数', 0)),
                    consult_rate = str(row.get('咨询率', '0%')),

                    # Retention
                    old_buyer_pay_amount = clean_float(row.get('老客复购金额', 0)),
                    old_buyer_pay_count = clean_int(row.get('老客复购人数', 0)),
                    old_buyer_rate = str(row.get('老客复购率', '0%')),

                    # Service
                    chat_response_time = clean_float(row.get('旺旺人工响应时长(秒)', 0)),
                    logistics_time = clean_float(row.get('物流到货时长(小时)', 0)),
                    refund_duration = clean_float(row.get('退款处理时长(天)', 0)),
                    dispute_rate = str(row.get('纠纷投诉商责率', '0%')),
                    chat_satisfaction = str(row.get('旺旺满意度', '0%'))
                )
                db.session.add(record)
            
            db.session.commit()
            print("Import completed successfully.")
            
        except Exception as e:
            print(f"Error during import: {e}")
            db.session.rollback()

class AnalyticsService:
    @staticmethod
    def get_sales_overview():
        """
        Get total sales summary for the Sales Dashboard.
        """
        # Sum of payment amount
        total_sales = db.session.query(func.sum(DailySales.payment_amount)).scalar()
        total_visitors = db.session.query(func.sum(DailySales.visitors)).scalar()
        total_orders = db.session.query(func.sum(DailySales.order_count)).scalar()
        
        return {
            "total_sales": total_sales if total_sales else 0,
            "total_visitors": total_visitors if total_visitors else 0,
            "total_orders": total_orders if total_orders else 0
        }

    @staticmethod
    def get_sales_trend():
        """ Daily Sales trend """
        results = db.session.query(
            DailySales.date,
            func.sum(DailySales.payment_amount).label('sales'),
            func.sum(DailySales.visitors).label('visitors')
        ).group_by(DailySales.date).order_by(DailySales.date).all()
        return [{"date": row[0], "sales": row[1], "visitors": row[2]} for row in results]

    @staticmethod
    def get_sales_funnel():
        """ Aggregate Funnel: Visitors -> AddCart -> PayUsers """
        res = db.session.query(
            func.sum(DailySales.visitors).label('visitors'),
            func.sum(DailySales.add_to_cart_users).label('cart'),
            func.sum(DailySales.order_count).label('orders') # Approximation
        ).one()
        
        return {
            "visitors": res.visitors or 0,
            "cart": res.cart or 0,
            "orders": res.orders or 0
        }
    
    @staticmethod
    def get_service_metrics():
        """ Service & Logistics KPIs (Avg) """
        res = db.session.query(
            func.avg(DailySales.logistics_time).label('logistics'),
            func.avg(DailySales.chat_response_time).label('chat'),
            func.avg(DailySales.refund_duration).label('refund')
        ).one()
        
        return {
            "logistics_hours": round(res.logistics or 0, 1),
            "chat_seconds": round(res.chat or 0, 1),
            "refund_days": round(res.refund or 0, 1)
        }

# E-commerce BI Dashboard

电商数据中台 - 基于 Flask + ECharts 构建的企业级 BI 看板系统。

## 功能特性

- 📊 **销售分析看板**: 销售额、访客数、转化漏斗
- 😊 **服务监控看板**: 物流时效、客服响应、退款效率
- 📈 **飞书数据看板**: 实时读取飞书在线表格数据

## 本地运行

```bash
pip install -r requirements.txt
python app.py
```

访问: http://127.0.0.1:5000

## 技术栈

- **Backend**: Flask, SQLAlchemy
- **Frontend**: ECharts, Jinja2
- **数据源**: SQLite (本地Excel) + 飞书 API (在线表格)

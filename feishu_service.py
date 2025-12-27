"""
Feishu Sheet Service - 飞书在线表格数据读取 (使用 HTTP API)
"""
import requests
import json

class FeishuSheetService:
    def __init__(self, app_id, app_secret):
        """
        Initialize Feishu client
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
    
    def _get_tenant_access_token(self):
        """
        获取 tenant_access_token
        """
        if self.access_token:
            return self.access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get("code") == 0:
            self.access_token = data.get("tenant_access_token")
            print(f"✅ Got access token: {self.access_token[:20]}...")
            return self.access_token
        else:
            print(f"❌ Failed to get token: {data}")
            return None
    
    def get_sheet_data(self, spreadsheet_token, sheet_id, range_notation="A1:Z1000"):
        """
        Read data from Feishu Sheet
        """
        token = self._get_tenant_access_token()
        if not token:
            return []
        
        # API: 读取单个范围
        range_str = f"{sheet_id}!{range_notation}"
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "valueRenderOption": "ToString"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get("code") == 0:
                values = data.get("data", {}).get("valueRange", {}).get("values", [])
                print(f"✅ Successfully read {len(values)} rows from Feishu")
                return values
            else:
                print(f"❌ API Error: code={data.get('code')}, msg={data.get('msg')}")
                return []
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []
    
    def parse_to_daily_sales(self, raw_data):
        """
        Convert raw Feishu data to DailySales format
        """
        records = []
        
        if not raw_data or len(raw_data) < 2:
            print(f"⚠️ Insufficient data: {len(raw_data) if raw_data else 0} rows")
            return records
        
        headers = raw_data[0]
        print(f"📋 Headers: {headers}")
        
        for row in raw_data[1:]:
            record = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    record[str(header)] = row[i]
                else:
                    record[str(header)] = None
            records.append(record)
        
        print(f"✅ Parsed {len(records)} records")
        return records

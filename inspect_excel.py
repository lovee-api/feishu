import pandas as pd
import os

excel_path = r'c:\Users\Administrator\Desktop\电商bi看板搭建\新建 Microsoft Excel 工作表 (2).xlsx'

try:
    # Read the first few rows to understand structure
    df = pd.read_excel(excel_path, nrows=5)
    print("Columns:", df.columns.tolist())
    print("\nFirst row sample:")
    print(df.iloc[0])
    
    # Check data types
    print("\nData Types:")
    print(df.dtypes)
except Exception as e:
    print(f"Error reading Excel: {e}")

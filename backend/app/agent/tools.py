# 工具 = Agent 可调用的普通函数。本文件只写纯数据逻辑，不碰 LLM
import pandas as pd
from langchain_core.tools import tool as _tool

def load_df(file_path: str)->pd.DataFrame:
    """读 CSV 为 DataFrame。所有工具共用，避免重复读文件"""
    return pd.read_csv(file_path)

def query_data(file_path: str,group_col: str,value_col:str,agg: str = "sum")->dict:
    """按维度聚合统计。如 query_data('sales.csv', '月份', '销售额')
    返回 {组名: 统计值} 的字典
    agg 支持: sum / mean / max / min / count
    """
    df = load_df(file_path)
    # groupby: 按 group_col 分组，取 value_col 列，做 agg 聚合
    result = df.groupby(group_col)[value_col].agg(agg)
    return result.to_dict() # 转成 {"2024-01": 3000, ...} 字典

def detect_anomaly(file_path: str,value_col: str,threshold: float = 2.0)->dict:
    """用 3σ 思想找异常：偏离均值超过 threshold 个标准差的行"""
    df = load_df(file_path)
    mean = df[value_col].mean() # 均值
    std = df[value_col].std()   # 标准差
    # 布尔索引：筛选出 |x - mean| > threshold * std 的行
    mask = (df[value_col] - mean).abs() > threshold * std
    anomalies = df[mask].to_dict("records") #把异常行转成字典列表
    return {
        "mean": round(float(mean), 2),   # float() 转原生类型，保证可 JSON 序列化
        "std": round(float(std), 2),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }

def summarize_column(file_path: str,column: str)->dict:
    """单列描述统计"""
    df = load_df(file_path)
    series = df[column]
    return {
        "count": int(series.count()),          #非空数量
        "mean": round(float(series.mean()), 2),  #均值
        "max": float(series.max()),           #最大值
        "min": float(series.min()),           #最小值
        "unique": int(series.nunique()),      #不同取值个数
    }


# ---- 把纯函数包装成 LangChain 工具，供 LLM 通过 bind_tools 调用 ----
# _tool(func) 会读取函数的 类型注解 + docstring，自动生成 LLM 能读懂的"参数 JSON schema"
query_data_tool = _tool(query_data)
detect_anomaly_tool = _tool(detect_anomaly)
summarize_column_tool = _tool(summarize_column)

ALL_TOOLS = [query_data_tool, detect_anomaly_tool, summarize_column_tool]
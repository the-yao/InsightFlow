# 终端交互入口：先选模型 -> 再输入问题 -> 打印分析结果
from app.agent.graph import run_agent
from app.core.llm import choose_provider

if __name__ == "__main__":
    provider = choose_provider()
    question = input("请输入你的分析问题：") or "请分析 sales.csv：按月份汇总销售额，并检查销售额有没有异常"
    print("\n正在分析...\n")
    print(run_agent(question, provider=provider))
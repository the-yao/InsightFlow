# 2.4：用 LangGraph 状态机重构，支持多轮工具调用 + 系统提示词约束
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.graph import StateGraph,MessagesState,START,END
from langgraph.prebuilt import ToolNode

from app.core.llm import get_llm
from app.agent.tools import ALL_TOOLS

# 系统提示词：解决之前模型「偏离指令」的三大问题 
SYSTEM_PROMPT = """你是 InsightFlow 的数据分析助手。分析时必须遵守：
1. 始终用中文回答
2. 严格按用户指定的维度分析（用户说按月份就按月份，不要自作主张换维度）
3. 主动完成任务，不要反问用户
4. 只基于工具返回的真实数据下结论，不要编造
"""

def build_graph(provider: str | None = None):
  #在build_graph里创建llm，通过闭包把provider/tools固定给节点
  llm = get_llm(provider=provider).bind_tools(ALL_TOOLS)

  #--节点1: 调用模型--
  def call_model(state):
    response = llm.invoke(state["messages"])
    return {"messages":[response]}    #返回模型回复,MessageState会【追加】而非覆盖

  #--节点2： 执行工具（langgraph 内置，自动遍历tool_calls 并回填结果）--
  tool_node = ToolNode(ALL_TOOLS)

  # --条件边： 模型还想调工具?--
  def should_continue(state) -> str:
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

  #--组装状态机--
  graph = StateGraph(MessagesState)
  graph.add_node("agent",call_model)    # 模型节点
  graph.add_node("tools",tool_node)    # 工具节点
  graph.add_edge(START,"agent")        # 入口 -> 模型
  graph.add_conditional_edges(         #模型 -> 工具 / 结束 (由should_continue决定)
    "agent",
    should_continue,
    {"tools": "tools",END: END},
  )
  graph.add_edge("tools","agent")       # 工具跑完 -> 模型（循环）

  return graph.compile() 

def run_agent(question: str,provider: str | None = None) -> str:
  app = build_graph(provider)
  #初始 State： 系统提示词 + 用户问题
  initial_state = {"messages":[SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content=question)]}
  result = app.invoke(initial_state)
  return result["messages"][-1].content

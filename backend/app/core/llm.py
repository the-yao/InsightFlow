# DeepSeek 和 Ollama 都走 OpenAI 兼容协议，只需切换 base_url 和 model
from langchain_openai import ChatOpenAI
from .config import settings

def get_llm ( temperature: float = 0 , provider: str | None = None ):
    provider = provider or settings.llm_provider
    if provider == "ollama":
        return ChatOpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama",
            model=settings.ollama_model,
            temperature=temperature,
        )
    return ChatOpenAI(
        base_url=settings.deepseek_base_url,
        api_key=settings.deepseek_api_key,
        model=settings.deepseek_model,
        temperature=temperature,
    )

def choose_provider() -> str:
    """终端交互式选择 LLM，返回 'deepseek' 或 'ollama'"""
    print("请选择使用的模型：")
    print("1. DeepSeek")
    print(f"2. Ollama（{settings.ollama_model}）")
    while True:
        choice = input("请输入数字 (1/2): ").strip()
        if choice == "1":
            return "deepseek"
        if choice == "2":
            return "ollama"
        print("输入无效，请输入 1 或 2")
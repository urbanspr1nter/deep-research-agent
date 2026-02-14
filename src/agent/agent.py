from smolagents import CodeAgent, OpenAIModel
from tools.kagi_search_tool import KagiSearchTool
from tools.text_summarizer_tool import TextSummarizerTool


model = OpenAIModel(
    model_id="ministral-3-3b-reasoning-2512",
    api_base="http://127.0.0.1:8000/v1",
    api_key="none",
    temperature=0.6
)

agent = CodeAgent(
    tools=[
        KagiSearchTool(),
        TextSummarizerTool()
    ],
    model=model,
    additional_authorized_imports=[
        "requests",
        "bs4", 
        "os"
    ],
)

result = agent.run("tell me about the Qwen3-VL model architecture in detail. cite your sources.")
print(result)

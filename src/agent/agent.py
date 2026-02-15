import os
from smolagents import CodeAgent, OpenAIModel, VisitWebpageTool, WikipediaSearchTool
from tools.kagi_search_tool import KagiSearchTool
from tools.pdf_to_markdown import PdfToMarkdownTool
from tools.search_resarch_papers_on_arxiv_tool import SearchResearchPapersOnArxivTool
from tools.text_summarizer_tool import TextSummarizerTool
from tools.file_system_tool import FileSystemTool
from callbacks.token_usage import on_step as on_step_monitor_token_usage

config = {
    "model_id": "gpt-oss-120b",
    "api_base": "http://192.168.1.21:8000/v1",
    "api_key": "none",
    "temperature": 0.6
}

model = OpenAIModel(**config)

search_agent = CodeAgent(
    max_steps=100,
    tools=[
        KagiSearchTool(),
        VisitWebpageTool(),
        FileSystemTool(),
        WikipediaSearchTool(
            user_agent="Roger's Deep Researcher (urbanspr1nter@gmail.com)"
        ),
        SearchResearchPapersOnArxivTool()
    ],
    model=model,
    additional_authorized_imports=[
        "requests",
        "bs4",
        "json",
        "matplotlib",
        "pandas",
        "numpy"
    ],
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    name="search_agent",
    description="Search agent. Utilize for searching the web, visiting web pages and collect findings. Give it clear research questions."
)

reader_agent = CodeAgent(
    max_steps=100,
    tools=[
        TextSummarizerTool(
            model=config["model_id"],
            llm_host_base_url=config["api_base"],
            llm_host_api_key=config["api_key"]
        ),
        PdfToMarkdownTool(),
        FileSystemTool()
    ],
    model=model,
    additional_authorized_imports=[
        "requests",
        "bs4", 
        "json",
        "matplotlib",
        "pandas",
        "numpy"
    ],
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    name="reader_agent",
    description="Extract content from PDFs, summarize large amounts of content and collect findings."
)



agent = CodeAgent(
    max_steps=100,
    managed_agents=[search_agent, reader_agent],
    tools=[],
    model=model,
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    instructions="You are a deep research manager. Break research questions into sub-tasks, delegate each to the appropriate agent, and synthesize their results into a comprehensive answer. Always delegate — never try to answer from memory alone.",
    step_callbacks=[on_step_monitor_token_usage]
)

# print("Ask away...")
# while True:
#     print()
#     query = input("> ")

#     if query.strip() == "/exit":
#         break

#     result = agent.run(query)

#     print(result)

result = agent.run("""Research what the general consensus is with regards to which of the 3 starter Pokemon of the original 150 is the strongest.

For your final answer, generate a full report (in markdown) of your findings and cite sources.

Save the report as "Final Report.md" in the sandbox.
""")
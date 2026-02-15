import os
from smolagents import CodeAgent, OpenAIModel, VisitWebpageTool, WikipediaSearchTool
from tools.kagi_search_tool import KagiSearchTool
from tools.pdf_to_markdown import PdfToMarkdownTool
from tools.search_resarch_papers_on_arxiv_tool import SearchResearchPapersOnArxivTool
from tools.text_summarizer_tool import TextSummarizerTool
from tools.file_system_tool import FileSystemTool
from callbacks.token_usage import on_step as on_step_monitor_token_usage
from prompts.manager import get_manager_instructions
from prompts.search_agent import get_search_agent_instructions
from prompts.reader_agent import get_reader_agent_instructions
from prompts.fact_checker_agent import get_fact_checker_agent_instructions

config = {
    "model_id": "gpt-oss-120b",
    "api_base": "http://192.168.1.21:8000/v1",
    "api_key": os.getenv("OPENAI_API_KEY", "none"),
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
        "numpy",
        "textwrap"
    ],
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    name="search_agent",
    description="Search agent. Utilize for searching the web, visiting web pages and collect findings. Give it clear research questions.",
    instructions=get_search_agent_instructions()
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
        "numpy",
        "textwrap"
    ],
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    name="reader_agent",
    description="Extract content from PDFs, summarize large amounts of content and collect findings.",
    instructions=get_reader_agent_instructions()
)

fact_checker_agent = CodeAgent(
    max_steps=100,
    tools=[
        KagiSearchTool(),
        VisitWebpageTool(),
        FileSystemTool()
    ],
    model=model,
    additional_authorized_imports=[
        "requests",
        "bs4",
        "json"
    ],
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    name="fact_checker_agent",
    description="Fact-checker agent. Verifies the accuracy of a research report by checking citations and claims against their sources. Give it the path to a report in the sandbox.",
    instructions=get_fact_checker_agent_instructions()
)

agent = CodeAgent(
    max_steps=100,
    managed_agents=[search_agent, reader_agent, fact_checker_agent],
    tools=[
        FileSystemTool()
    ],
    model=model,
    planning_interval=3,
    executor_kwargs={"timeout_seconds": 3600},
    instructions=get_manager_instructions(),
    additional_authorized_imports=[
        "requests",
        "bs4", 
        "json",
        "matplotlib",
        "pandas",
        "numpy",
        "textwrap"
    ],
    step_callbacks=[on_step_monitor_token_usage]
)


result = agent.run("""Research the difference between Thunderbolt 4/5 compared to OcuLink.

We need to understand:
- Background information about each of the technologies, and their historical context
- Technical comparisons between the 2 technologies
- Applications used in each
- Why Thunderbolt is seemingly more prominent than OcuLink in the consumer market.
- Use-cases in enterprise environment.
- Reliability and long-term ROI and cost in devices using either of the technologies
- Limitations and operating systems support.

You may also gather any other additional information not noted above which you may think will be helpful for the reader to know.

Create a comprehensive report about your findings. Cite all sources.

CRITICAL: Output final report as a markdown file.
""")
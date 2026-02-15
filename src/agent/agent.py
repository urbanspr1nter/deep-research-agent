import os
from smolagents import CodeAgent, OpenAIModel, WikipediaSearchTool
from tools.safe_visit_webpage_tool import SafeVisitWebpageTool
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

DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_API_BASE_URL = "https://api.openai.com/v1"
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY", "none")

model_configs = {
    "manager": {
        "model_id": DEFAULT_MODEL,
        "api_base": DEFAULT_API_BASE_URL,
        "api_key": DEFAULT_API_KEY,
        "temperature": 1.0
    },
    "search_agent": {
        "model_id": DEFAULT_MODEL,
        "api_base": DEFAULT_API_BASE_URL,
        "api_key": DEFAULT_API_KEY,
        "temperature": 1.0
    },
    "reader_agent": {
        "model_id": DEFAULT_MODEL,
        "api_base": DEFAULT_API_BASE_URL,
        "api_key": DEFAULT_API_KEY,
        "temperature": 1.0
    },
    "fact_checker_agent": {
        "model_id": DEFAULT_MODEL,
        "api_base": DEFAULT_API_BASE_URL,
        "api_key": DEFAULT_API_KEY,
        "temperature": 0.1 
    }
}

config = {
    "max_steps": 25,
    "additional_authorized_imports": [
        "requests",
        "bs4",
        "json",
        "matplotlib",
        "pandas",
        "numpy",
        "textwrap"
    ],
    "execution_timeout_seconds": 900,
    "planning_interval": 3
}

search_agent = CodeAgent(
    max_steps=config["max_steps"],
    tools=[
        KagiSearchTool(),
        SafeVisitWebpageTool(),
        FileSystemTool(),
        WikipediaSearchTool(
            user_agent="Roger's Deep Researcher (urbanspr1nter@gmail.com)"
        ),
        SearchResearchPapersOnArxivTool()
    ],
    model=OpenAIModel(**model_configs["search_agent"]),
    additional_authorized_imports=config["additional_authorized_imports"],
    planning_interval=config["planning_interval"],
    executor_kwargs={"timeout_seconds": config["execution_timeout_seconds"]},
    name="search_agent",
    description="Search agent. Utilize for searching the web, visiting web pages and collect findings. Give it clear research questions.",
    instructions=get_search_agent_instructions()
)

reader_agent = CodeAgent(
    max_steps=config["max_steps"],
    tools=[
        TextSummarizerTool(
            model=model_configs["reader_agent"]["model_id"],
            llm_host_base_url=model_configs["reader_agent"]["api_base"],
            llm_host_api_key=model_configs["reader_agent"]["api_key"]
        ),
        PdfToMarkdownTool(),
        FileSystemTool()
    ],
    model=OpenAIModel(**model_configs["reader_agent"]),
    additional_authorized_imports=config["additional_authorized_imports"],
    planning_interval=config["planning_interval"],
    executor_kwargs={"timeout_seconds": config["execution_timeout_seconds"]},
    name="reader_agent",
    description="Extract content from PDFs, summarize large amounts of content and collect findings.",
    instructions=get_reader_agent_instructions()
)

fact_checker_agent = CodeAgent(
    max_steps=config["max_steps"],
    tools=[
        KagiSearchTool(),
        SafeVisitWebpageTool(),
        FileSystemTool()
    ],
    model=OpenAIModel(**model_configs["fact_checker_agent"]),
    additional_authorized_imports=config["additional_authorized_imports"],
    planning_interval=config["planning_interval"],
    executor_kwargs={"timeout_seconds": config["execution_timeout_seconds"]},
    name="fact_checker_agent",
    description="Fact-checker agent. Verifies the accuracy of a research report by checking citations and claims against their sources. Give it the path to a report in the sandbox.",
    instructions=get_fact_checker_agent_instructions()
)

agent = CodeAgent(
    max_steps=config["max_steps"],
    managed_agents=[search_agent, reader_agent, fact_checker_agent],
    tools=[
        FileSystemTool()
    ],
    model=OpenAIModel(**model_configs["manager"]),
    planning_interval=config["planning_interval"],
    executor_kwargs={"timeout_seconds": config["execution_timeout_seconds"]},
    instructions=get_manager_instructions(),
    additional_authorized_imports=config["additional_authorized_imports"],
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
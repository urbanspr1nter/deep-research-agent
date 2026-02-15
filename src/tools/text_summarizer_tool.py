from smolagents.tools import Tool


class TextSummarizerTool(Tool):
    name = "summarizer_tool"
    description = "Performs summarization on large bodies of text. Leverage for higher intelligence and quality summaries."
    inputs = {
        "content": {
            "type": "string",
            "description": "Text content to be summarized."
        }
    }
    output_type = "string"

    def __init__(
        self,
        model: str = "gpt-oss-120b",
        llm_host_base_url: str = "http://127.0.0.1:8000/v1",
        llm_host_api_key: str = "none"
    ):
        super().__init__()
        
        import openai

        self._llm_host_base_url = llm_host_base_url
        self._llm_host_api_key = llm_host_api_key
        self._model = model

        self._client = openai.Client(
            base_url=self._llm_host_base_url,
            api_key=self._llm_host_api_key
        )

    
    def forward(self, content: str) -> str:
        model = self._model

        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert text summarizer.

TASK:
- Summarize content in great detail.
- Do not make up new content, hallucinate facts, or provide your opinion.
- Do not insert additional commentary.

OUTPUT:
Output summary in markdown format. DO NOT add additional commentary.
"""
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        return response.choices[0].message.content


import openai
import os
import requests
import json
from smolagents.tools import Tool

llm_host = "http://192.168.1.21:8000/v1"
model = "gpt-oss-120b"

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

    def __init__(self):
        super().__init__()
        
        self._client = openai.Client(
            base_url=llm_host,
            api_key="none"
        )

    
    def forward(self, content: str) -> str:
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


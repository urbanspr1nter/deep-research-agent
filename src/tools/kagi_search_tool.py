from smolagents.tools import Tool

class KagiSearchTool(Tool):
    name = "kagi_search"
    description = """Performs a web search using the Kagi search engine based on your query. It is superior to Google search. This tool return a list of search results.

Output will be a formatted markdown summary of the search results followed by a list of suggested additional search queries that may be relevant to the original query.

IMPORTANT: Must have the KAGI_API_KEY environment variable set to use this tool. By default, the tool will reference it from your environment."""
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to perform."
        },
        "limit": {
            "type": "integer",
            "nullable": True,
            "description": "Search results limit. Default is 25 and can be no less than that."
        }
    }
    output_type = "string"

    def __init__(self, api_key: str = ""):
        super().__init__()

        import os
        self.api_key = api_key or os.getenv("KAGI_API_KEY")

        if not self.api_key or len(self.api_key) == 0:
            raise ValueError("Need a Kagi API key!")

    def forward(self, query: str, limit: int = 25) -> str:
        import requests

        params = {
            "q": query,
            "limit": limit
        }

        headers= {
            "Authorization": f"Bot {self.api_key}"
        }

        response = requests.get(
            "https://kagi.com/api/v0/search",
            headers=headers,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        if "data" in data:
            data = data["data"]

        suggested_search_results = [s for s in data if s["t"] == 1]

        results = {}

        results["suggested_additional_search_queries"] = "## Suggested Additional Search Queries"
        if len(suggested_search_results) > 0:
            suggested_list = suggested_search_results[0].get("list", [])
            for suggested_query in suggested_list:
                results["suggested_additional_search_queries"] = f"""{results['suggested_additional_search_queries']}
- {suggested_query}"""

        results["search_results"] = f"""## Search Results
Here are your results for the following search query: {query}.

Use the information below to summarize or fetch additional information given the URL.

"""
        for search_result in data:
            if search_result["t"] != 0:
                continue

            results["search_results"] = f"""{results["search_results"]}
### {search_result["title"]}
**URL** - {search_result["url"]}
**Preview** - {search_result["snippet"]}

"""
        final = f"""{results["search_results"]}
{results["suggested_additional_search_queries"]}
"""

        return final

    def _to_markdown():
        pass

if __name__ == "__main__":
    search_tool = KagiSearchTool()

    print(search_tool("why is the sky blue?"))
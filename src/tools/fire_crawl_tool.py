from smolagents.tools import Tool


class FireCrawlWebpageScraperTool(Tool):
  name = "visit_webpage"
  description = (
      "Visits a webpage at the given url and reads its content as a markdown string. Use this to browse webpages."
  )
  inputs = {
      "url": {
          "type": "string",
          "description": "The url of the webpage to visit.",
      }
  }
  output_type = "string"

  def __init__(self, api_key: str):
    super().__init__()

    self._base_url = "https://api.firecrawl.dev/v2/scrape"
    self._api_key = api_key

  
  def forward(self, url: str) -> str:
    import requests

    headers = {
      "Authorization": f"Bearer {self._api_key}",
      "Content-Type": "application/json"
    }

    payload = {
      "url": url,
      "formats": [
        "markdown"
      ],
      "excludeTags": [
        "header",
        "footer",
        "nav",
        "aside",
        "iframe"
      ],
      "waitFor": 100,
      "removeBase64Images": True,
      "storeInCache": False,
      "timeout": 60000
    }

    result = requests.post(self._base_url, headers=headers, json=payload).json()

    if "data" in result and "markdown" in result["data"]:
      return result["data"]["markdown"]
    else:
      return "[ERROR] WEBPAGE UNAVAILABLE"
    

if __name__ == "__main__":
  import os
  crawl = FireCrawlWebpageScraperTool(os.getenv("FIRE_CRAWL_API_KEY"))

  print(crawl.forward("https://qwen.ai/blog?id=qwen3.5"))
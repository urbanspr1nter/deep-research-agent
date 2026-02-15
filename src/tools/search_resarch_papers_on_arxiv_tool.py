from smolagents.tools import Tool


class SearchResearchPapersOnArxivTool(Tool):
    name = "arxiv_search"
    description = """Searches arXiv for academic research papers matching a query. Returns a list of papers with their title, authors, abstract, and PDF download URL.

Use standard search terms. You can also use arXiv field prefixes for targeted searches:
- ti:term — search in title only
- au:term — search by author
- abs:term — search in abstract only
- all:term — search all fields (default)

Boolean operators AND, OR, ANDNOT can be used to combine terms. Example: "all:CRISPR AND all:gene therapy"

Results are sorted by relevance by default."""
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query. Example: 'all:transformer attention mechanism' or 'ti:CRISPR AND abs:gene therapy'"
        },
        "max_results": {
            "type": "integer",
            "nullable": True,
            "description": "Maximum number of results to return. Default is 5, max recommended is 20."
        }
    }
    output_type = "string"

    def forward(self, query: str, max_results: int = 5) -> str:
        import requests
        import xml.etree.ElementTree as ET

        params = {
            "search_query": query,
            "start": 0,
            "max_results": min(max_results, 20),
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        response = requests.get(
            "http://export.arxiv.org/api/query",
            params=params,
            timeout=120
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)

        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom"
        }

        entries = root.findall("atom:entry", ns)

        if not entries:
            return "No results found."

        results = []
        for entry in entries:
            title_el = entry.find("atom:title", ns)
            title = " ".join(title_el.text.split()) if title_el is not None and title_el.text else "No title"

            authors = []
            for author in entry.findall("atom:author", ns):
                name_el = author.find("atom:name", ns)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            abstract_el = entry.find("atom:summary", ns)
            abstract = " ".join(abstract_el.text.split()) if abstract_el is not None and abstract_el.text else ""

            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")
                    break

            published_el = entry.find("atom:published", ns)
            published = published_el.text[:10] if published_el is not None and published_el.text else ""

            paper = f"""### {title}
**Authors:** {", ".join(authors)}
**Published:** {published}
**PDF:** {pdf_url}
**Abstract:** {abstract}
"""
            results.append(paper)

        return "\n---\n".join(results)

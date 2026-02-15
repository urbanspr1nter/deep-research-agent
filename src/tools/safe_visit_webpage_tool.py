import requests
from smolagents import VisitWebpageTool


class SafeVisitWebpageTool(VisitWebpageTool):
    """VisitWebpageTool that checks Content-Type before processing.

    Sends a HEAD request first and rejects non-text content (e.g. PDFs,
    images, binaries) instead of hanging while markdownify tries to parse
    garbage input.
    """


    ALLOWED_CONTENT_TYPES = frozenset({
        "text/html",
        "text/plain",
        "application/json",
        "application/xhtml+xml",
    })

    @staticmethod
    def _is_text_content(content_type: str) -> bool:
        return (
            content_type.startswith("text/")
            or content_type in SafeVisitWebpageTool.ALLOWED_CONTENT_TYPES
        )

    def forward(self, url: str) -> str:
        try:
            head = requests.head(url, timeout=20, allow_redirects=True)
            content_type = (
                head.headers.get("Content-Type", "")
                .split(";")[0]
                .strip()
                .lower()
            )

            if content_type and not self._is_text_content(content_type):
                return (
                    f"Error: URL returns unsupported content type '{content_type}'. "
                    "Only text, HTML, and JSON are supported. "
                    "For PDFs, use the pdf_to_markdown tool instead."
                )
        except requests.exceptions.RequestException:
            # If HEAD fails, fall through — let the parent's GET handle it.
            pass

        return super().forward(url)

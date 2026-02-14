from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser
from smolagents.tools import Tool

# TODO: Add a tool that can convert PDF to markdown. This will be useful for agents to read and understand PDF content.

class PdfToMarkdownTool(Tool):
    name = "pdf_to_markdown"
    description = "Converts a PDF file in the file system to markdown text. The markdown can be used downstream for other tasks."
    inputs = {
        "pdf_filepath": {
            "type": "string",
            "description": "Absolute path to the PDF file in the current file system."
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__()


    def forward(self, pdf_filepath: str):
        config = {
            "output_format": "markdown"
        }
        config_parser = ConfigParser(config)

        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict()
        )
        rendered = converter(pdf_filepath)

        text, _, images = text_from_rendered(rendered)

        return text
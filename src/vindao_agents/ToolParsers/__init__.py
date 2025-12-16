from .ToolParser import ToolParser
from .AtSyntaxParser import AtSyntaxParser

# Registry of available parsers
parsers = {
    "at_syntax": AtSyntaxParser,
    "default": AtSyntaxParser,
}
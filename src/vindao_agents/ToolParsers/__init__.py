from .AtSyntaxParser import AtSyntaxParser
from .ToolParser import ToolParser

# Registry of available parsers
parsers = {
    "at_syntax": AtSyntaxParser,
    "default": AtSyntaxParser,
}

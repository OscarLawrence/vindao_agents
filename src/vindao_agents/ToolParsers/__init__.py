from .AtSyntaxParser import AtSyntaxParser as AtSyntaxParser
from .ToolParser import ToolParser as ToolParser

# Registry of available parsers
parsers = {
    "at_syntax": AtSyntaxParser,
    "default": AtSyntaxParser,
}

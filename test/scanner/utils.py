import os
from io import StringIO
import logging
from scanner import Lexer


def capture_lexer_log(input_text):
    """Capture the lexer's log output and return it along with the tokens.

        The logger is reset after capturing the output.

        Args:
            input_text: The text to tokenize.

        Returns:
            A tuple of (log_output, tokens), where log_output is the string
            output of the logger during tokenization, and tokens is the list
            of tokens produced by the lexer.
        """
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('lexer')
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    lexer = Lexer()
    tokens = list(lexer.tokenize(input_text))

    handler.flush()
    logger.removeHandler(handler)
    return stream.getvalue(), tokens

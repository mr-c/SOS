from pygments import highlight
from pygments.token import Name, Keyword
from pygments.lexers import PythonLexer, TextLexer, get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter, TerminalFormatter
from pygments.styles import get_all_styles
from pygments.util import shebang_matches



class SoS_Lexer(PythonLexer):
    """
    A Python lexer with SOS keywords, used for SoS directive
    """

    name = 'Sript of Scripts'
    aliases = ['sos']

    # override the mimetypes to not inherit them from python
    mimetypes = []
    filenames = ['*.sos']
    mimetypes = ['text/x-sos', 'application/x-sos']

    PythonLexer.tokens['root'].insert(0, (r'(^\w+)\s*:', Keyword.Namespace))

    EXTRA_KEYWORDS = set( SOS_INPUT_OPTIONS + SOS_OUTPUT_OPTIONS +
        SOS_DEPENDS_OPTIONS + SOS_RUNTIME_OPTIONS + SOS_SECTION_OPTIONS +
        get_actions())

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
                PythonLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.EXTRA_KEYWORDS:
                yield index, Keyword.Pseudo, value
            else:
                yield index, token, value

    def analyse_text(text):
        return (shebang_matches(text, r'sos-runner') or \
            '#fileformat=SOS' in text[:1000])
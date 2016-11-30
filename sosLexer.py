from pygments.lexers.agile import PythonLexer
from pygments.token import Name, Keyword

__all__=['sosLexer']

class sosLexer(PythonLexer):
    """
    A Python lexer with SOS keywords, used for SoS directive
    """

    name = 'Sript of Scripts'
    aliases = ['sos']

    SOS_INPUT_OPTIONS = ['group_by', 'filetype', 'paired_with', 'for_each', 'pattern']
    SOS_OUTPUT_OPTIONS = []
    SOS_DEPENDS_OPTIONS = []
    SOS_RUNTIME_OPTIONS = ['workdir', 'concurrent', 'active', 'walltime', 'env', 'prepend_path']
    SOS_ACTION_OPTIONS = ['workdir', 'docker_image', 'docker_file', 'active']

    SOS_DIRECTIVES = ['input', 'output', 'depends', 'task', 'parameter']
    SOS_SECTION_OPTIONS = ['skip', 'sigil', 'provides', 'shared']

    SOS_KEYWORDS = SOS_INPUT_OPTIONS + SOS_OUTPUT_OPTIONS + SOS_DEPENDS_OPTIONS + SOS_RUNTIME_OPTIONS \
    + SOS_ACTION_OPTIONS + SOS_DIRECTIVES + SOS_SECTION_OPTIONS

    # override the mimetypes to not inherit them from python
    mimetypes = []
    filenames = ['*.sos']
    mimetypes = ['text/x-sos', 'application/x-sos']

    PythonLexer.tokens['root'].insert(0, (r'(^\w+)\s*:', Keyword.Namespace))

    EXTRA_KEYWORDS = set( SOS_INPUT_OPTIONS + SOS_OUTPUT_OPTIONS +
        SOS_DEPENDS_OPTIONS + SOS_RUNTIME_OPTIONS + SOS_SECTION_OPTIONS)

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
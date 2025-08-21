import sly


class Lexer(sly.Lexer):
    tokens = {
        ID,
    }

    @_(r'\n+')
    def ignored_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignored_cpp_comment(self, t):
        self.lineno += 1

    # comment type cpp /* {anything} */
    @_(r'/\*.*?\*/')
    def ignored_comment(self, t):
        self.lineno += t.value.count('\n')

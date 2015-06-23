import sys
import cStringIO
import token
import tokenize


class Token:
    ops = '+-*/'

    def __init__(self, _token_type, _token_text):
        self.token_type = _token_type
        self.token_text = _token_text

    def is_number(self):
        return self.token_type == 2

    def is_left_paren(self):
        return self.token_type == 51 and self.token_text == '('

    def is_right_paren(self):
        return self.token_type == 51 and self.token_text == ')'

    def is_operator(self):
        return self.token_type == 51 and not self.is_left_paren() and not self.is_right_paren()

    def is_valid_token(self):
        return self.token_type == 2 or (self.token_type == 51 and
                                        (self.is_right_paren() or
                                         self.is_left_paren() or
                                         (len(self.token_text) == 1 and Token.ops.find(self.token_text) > -1)))

    def same_or_less_prec(self, op):
        return Token.ops.find(self.token_text) <= Token.ops.find(op.token_text)

    def get_val(self):
        return self.token_text

    def apply(self, v1, v2):
        ret_val = None
        if self.token_text == '+':
            ret_val = int(v1.get_val()) + int(v2.get_val())
        else:
            if self.token_text == '-':
                ret_val = int(v1.get_val()) - int(v2.get_val())
            else:
                if self.token_text == '/':
                    ret_val = int(v1.get_val()) / int(v2.get_val())
                else:
                    if self.token_text == '*':
                        ret_val = int(v1.get_val()) * int(v2.get_val())

        return Token(2, str(ret_val))


class Application:
    def __init__(self, _line2parse):
        self.line2parse = _line2parse
        self.tokens = []
        self.values = []
        self.operators = []

    def tokenize(self):
        text = cStringIO.StringIO(self.line2parse)
        #try:
        tokenize.tokenize(text.readline, self)
        #except tokenize.TokenError, ex:
        #pass

    def __call__(self, toktype, toktext, (srow, scol), (erow, ecol), line):
        """ Token handler.
        """

        t = Token(toktype, toktext)

        # yes, creating token even for invalid (ignorable) tokens but for bc is ok
        if t.is_valid_token():
            # ignoring invalid tokens
            self.tokens.append(t)

        if 1:
            print "type", toktype, token.tok_name[toktype], "text", toktext
            #print "start", srow, scol, "end", erow, ecol

    def parse(self):
        for t in self.tokens:
            if t.is_number():
                self.values.append(t)
            else:
                if t.is_left_paren():
                    self.operators.append(t)
                else:
                    if t.is_right_paren():
                        while not self.operators[-1].is_left_paren():
                            op = self.operators.pop()
                            v1 = self.values.pop()
                            v2 = self.values.pop()
                            self.values.append(op.apply(v1, v2))

                        # getting rid of left parenthesis
                        self.operators.pop()
                    else:
                        if t.is_operator():
                            while len(self.operators) > 0 and t.same_or_less_prec(self.operators[-1]):
                                op = self.operators.pop()
                                v1 = self.values.pop()
                                v2 = self.values.pop()
                                self.values.append(op.apply(v1, v2))

                            self.operators.append(t)

        # all tokens are processed
        while len(self.operators) > 0:
            op = self.operators.pop()
            v1 = self.values.pop()
            v2 = self.values.pop()
            self.values.append(op.apply(v1, v2))

        print(self.values[0].get_val())

    def run(self):
        self.tokenize()
        self.parse()

    @staticmethod
    def usage():
        print("usage " + sys.argv[0] + "<airthmetic expression>")
        print("for example " + sys.argv[0] + "2 + 3 * 4")

if __name__ == "__main__":
    f = sys.stdin
    if len(sys.argv) != 2:
        Application.usage()
    else:
        app = Application(sys.argv[1])
        app.run()

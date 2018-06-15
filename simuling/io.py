from csvw import UnicodeWriter


class CommentedUnicodeWriter (UnicodeWriter):
    def __init__(self, f=None, dialect=None, **kw):
        comment_prefix = kw.pop('commentPrefix', None)
        super().__init__(f=f, dialect=dialect, **kw)
        self.comment_prefix = comment_prefix

    def writecomment(self, comment):
        if self.comment_prefix is None:
            raise ValueError(
                'Cannot write comments in this csv dialect')
        for row in comment.split('\n'):
            self.f.write(self.comment_prefix)
            self.f.write(row)
            self.f.write('\n')

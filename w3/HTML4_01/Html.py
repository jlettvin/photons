"""Html.py
"""

# iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
import os.path
from bs4 import (BeautifulSoup)
from urllib2 import (urlopen)
from cPickle import (load, dump)
from pprint import (pprint)
from types import (MethodType)


# fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
def erase(s, R=u"\xa0\n"):
    """
    Eliminate special characters found in HTML from authoritative sources.
    """
    return u''.join([c for c in s if c not in R])


# fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
def cases(s):
    """
    Return a pair of unicode HTML keywords (tags or attributes) in both cases.
    """
    return [unicode(s.lower()), unicode(s.upper())]


# CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
class D(dict):
    """
    D is a class to turn dictionary key names into class member names.
    """
    @staticmethod
    def _name(K):
        return K.translate(None, '-<>')

    def _method(J, K):
        assert type(K) == type(D._name)
        return MethodType(K, J, D)

    def __init__(J, **K):
        J.__dict__ = J
        J.let(**K)

    def __call__(J, **K):
        J.let(**K)
        return J

    def let(J, **K):
        J.update({D._name(k): v for k, v in K.items()})

    def fun(J, **K):
        J.update({D._name(k): J._method(v) for k, v in K.items()})


# CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
class Html(D):
    """
    Html is a class that implements all legal HTML 4.0 tags as methods.
    Tags are typically implemented as contexts unless close tag is forbidden.
    For instance the following makes legal HTML.

    def hello():
        HTML = Html()
        with HTML.HTML():
            with HTML.BODY():
                HTML.text('hello')
                HTML.BR()
                HTML.text('world')
        return str(HTML)

    print hello()
    """

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _assert(self, condition, message):
        if not condition:
            error = 'Html: %s' % (message)
            assert False, error

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _indent(self):
        """
        Generate the newline indent needed for tags.
        """
        return '\n'+' '*self._level

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _confirm(self, tag, **kw):
        """
        _confirm is a private method that detects illegal attributes or
        illegal combinations of attributes for a given tag.
        kw contains candidate attributes for the tag.
        """
        tag = unicode(tag.upper())
        for attribute, value in kw.items():

            # Both upper and lower case versions are permitted.
            lk, uk = cases(attribute)

            # Check that the attribute is known by its uppercase name.
            atts = self._att.get(uk, None)
            self._assert(
                atts,
                '%s is not a recognized attribute' % (attribute))

            # Fetch the inclusive and exclusive tag lists.
            include = tag in atts[0]
            exclude = tag not in atts[1]
            if self.verbose:
                print tag, uk, atts, include, exclude

            # Identify illegal use of attribute.
            self._assert(
                include or exclude,
                "<%s %s='%s'> tag has a forbidden attribute" % (
                    tag, attribute, value))

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _push(self, tag, **kw):
        """
        _push is a private method for entering a tag context.
        """
        tag = unicode(tag)
        # Check for legal use of tag attributes in kw.
        self._confirm(tag, **kw)

        # Prevent illegal use of forbidden end tag.
        # _push is used for <tag>...</tag>.
        # _close is used for <tag />.
        close = (self._has[tag]['end'] == u'F')

        # Prevent use of deprecated tags.
        self._assert(
            self._has[tag]['deprecated'] != u'D',
            '<%s> Deprecated' % (tag))
        # Insert tag with attributes.
        self._text += '%s<%s%s%s>' % (
            self._indent(),
            tag,
            ' '+' '.join(['%s="%s"' % (k, v) for k, v in kw.items()])
            if kw else '',
            ' /' if close else '')

        # Put tag on stack for later closing.
        self.tagstack = [tag, ] + self.tagstack

        # Keep track of levels.
        # This could be the count of the tagstack instead.
        self._level += int(not close)

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _pop(self):
        """
        _pop is a private method for exiting a tag context.
        """

        # Pop the tagstack.
        tag, self.tagstack = self.tagstack[0], self.tagstack[1:]

        # Check for forbidden close.
        close = (self._has[tag]['end'] == u'F')

        if not close:
            # Keep track of levels.
            # Insert tag close.
            self._level -= 1
            self._text += '%s</%s>' % (self._indent(), tag)

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _close(self, tag, **kw):
        """
        _close is a private method for generating a self-closing tag.
        """

        # Special method to make a self-closing tag with attributes.
        self._text += '%s<%s%s />' % (
            self._indent(),
            tag,
            ' '+' '.join(['%s="%s"' % (k, v) for k, v in kw.items()])
            if kw else '')

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _tagMethod(self, tag):
        """
        _tagMethod generates a call to _push or _close for a tag name.
        This is how HTML.H1 (for instance) becomes a context managing method.
        """
        if tag == 'del':
            # the lowercase keyword 'del' interferes with the python keyword.
            return

        # Choose correct function depending on self-closing of tag.
        # fun = ['close', 'push'][int(self._has[tag]['end'] == u'F']
        fun = 'close' if self._has[tag]['end'] == u'F' else 'push'

        # Private function named with leading underscore.
        _tag = '_' + tag

        # Text used to compile private function.
        define = 'def %s(self, **kw): self._%s("%s", **kw); return self' % (
            _tag, fun, tag)

        # Text used to attach private function to instance.
        cmd = "self.fun(%s=%s)" % (tag, _tag)

        # Compile private function and attach to instance.
        exec(define)
        exec(cmd)

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _ingestTag(self, cell):
        """
        _ingestTag populates the self._tag and self._has lookup table.
        """
        if cell:
            # populate the _has member with cell contents.
            ltag, utag = cases(cell[0])
            # utag = cell[0].upper()
            # ltag = utag.lower()
            self._tag += [utag, ltag]
            self._has[utag] = self._has[ltag] = {
                'start': cell[1],
                'end': cell[2],
                'empty': cell[3],
                'deprecated': cell[4],
                'DTD': cell[5],
                'description': cell[6], }
            # Attach both lower and upper case tag methods to instance.
            self._tagMethod(utag)
            self._tagMethod(ltag)
        return self

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _ingestAtt(self, cell):
        """
        _ingestAtt populates the self._att lookup table.
        """
        if cell:
            # populate the _att member with cell contents.
            att = unicode(cell[0])
            latt, uatt = cases(cell[0])
            # uatt = unicode(cell[0].upper())
            # latt = unicode(cell[0].lower())
            tags = unicode(cell[1])

            # Separate attributes into inclusive and exclusive lists.
            include, exclude = [[], []]
            if tags.startswith('All elements but'):
                exclude += [unicode(t.upper()) for t in tags[17:].split(', ')]
                exclude += [unicode(t.lower()) for t in tags[17:].split(', ')]
            else:
                include += [unicode(t.upper()) for t in tags.split(', ')]
                include += [unicode(t.lower()) for t in tags.split(', ')]

            # Append results to previous lists if they exist.
            inc, exc = self._att.get(att, [[], []])
            # Allow lower and upper case attributes.
            self._att[uatt] = [inc+include, exc+exclude]
            self._att[latt] = [inc+include, exc+exclude]
        return self

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def _ingest(self):
        """
        _ingest is a private method for loading pre-fetched lists of
        tags and attributes or, if the pickle files do not exist,
        fetching those data from the authoritative sources,
        parsing them, and turning them into python-usable data structures,
        then pickling them.
        """

        try:
            # Load the pickle file, if it exists.
            self._tag, self._has, self._att = load(open(self.PKL))

            # Compile and attach methods for tags to instance.
            for tag in self._tag:
                self._tagMethod(tag)

            # Nothing else to do.
            return
        except:
            # If pickle files don't exist, fetch from authoritative source.
            pass

        # Authoritative sources are at these two URLs.
        # Name, Start, End, Empty, Deprecated, DTD, Description
        # O(ptional), F(orbidden), E(mpty), D(eprecated), L(oose), F(rameset)
        TAGURL = "http://www.w3.org/TR/html4/index/elements.html"
        # Name, Elements, Type, Default, Deprecated, DTD, Comment
        ATTURL = "http://www.w3.org/TR/html4/index/attributes.html"

        # Prepare empty data containers.
        self._tag, self._has, self._att = [], {}, {}

        # Fetch the legal tags by parsing the source.
        for row in BeautifulSoup(urlopen(TAGURL).read()).table.findAll("tr"):
            # Each row in the table has cells with values.
            # Eliminate bad characters from cells with 'erase'.
            self._ingestTag([erase(td.text) for td in row.findAll("td")])

        # Fetch the legal attributes by parsing the source.
        for row in BeautifulSoup(urlopen(ATTURL).read()).table.findAll("tr"):
            # Each row in the table has cells with values.
            # Eliminate bad characters from cells with 'erase'.
            self._ingestAtt([erase(td.text) for td in row.findAll("td")])

        # Make pickle file for later use.
        self._tag = set(self._tag)
        dump([self._tag, self._has, self._att], open(self.PKL, "w"))

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def __init__(self, *args, **kw):
        """
        Public initializer.
        This sets up a new HTML buffer, and ingests tags and attributes
        in preparation for tag deployment.
        """
        super(Html, self).__init__(**kw)
        self.verbose = kw.get('verbose', False)
        self.PKL = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "artifacts",
            "python.Html.pkl")
        self._ingest()
        self._level = 0
        self._text = ''
        self.tagstack = []
        self.marks = {}

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def __enter__(self):
        """
        Public context entrypoint used by all tag methods having a close.
        """
        return self

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def __exit__(self, aType, aValue, aTraceback):
        """
        Public context exitpoint used by all tag methods having a close.
        """
        self._pop()

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def __str__(self):
        """
        str(HTML) completes the buffer generation, takes a copy,
        then clears the HTML instance in preparation for another run.
        It returns the completed copy of the buffer.
        """
        _text, self._text = self._text, ''
        self._level = 0
        self.tagstack = []
        return '<!DOCTYPE html>'+_text

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def text(self, text=""):
        """
        Public method allowing entry of text into the buffer.
        """
        if text:
            self._text += '\n%s' % (text)
        return self

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def comment(self, text=""):
        """
        Public method allowing entry of a comment into the buffer.
        """
        if text:
            self._text += '%s<!-- %s -->' % (self._indent(), text)
        return self

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def mark(self, name):
        self.marks[name] = len(self._text)

    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    def between(self, A, B):
        keys = self.marks.keys()
        assert A in keys and B in keys
        a, b = [self.marks[c] for c in [A, B]]
        assert a < b
        return self._text[a:b]

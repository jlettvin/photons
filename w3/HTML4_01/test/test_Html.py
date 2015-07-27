#!/usr/bin/env python

"""test_Html.py

Usage:
    test_Html.py [(-v | --verbose)]
    test_Html.py (-h | --help)
    test_Html.py --version

Options:
    -v --verbose                            Execution details [default: False]
    -h --help                               This screen
    --version                               Version

"""

from formal.w3.HTML4_01.Html import (Html)

# MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
if __name__ == "__main__":
    from docopt import (docopt)
    kw = docopt(__doc__, version="0.0.1")

    w3 = Html(**kw)
    tags = "HTML,BODY,H1,B,BR,A,P,text,comment"
    for tag in tags.split(','):
        exec("%s=w3.%s" % (tag, tag))

    with HTML():
        with BODY():
            with H1():
                text('Hello world')
            with B():
                BR()
            with A(href="http://jonathan.lettvin.com"):
                text('My personal page.')
            comment('This is a comment')
            with P(style=""):
                pass
    with open('../artifacts/python.Html.html', 'w') as target:
        print>>target, w3

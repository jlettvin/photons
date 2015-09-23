#!/usr/bin/env python

"""photons.py

Usage:
    photons.py \
[(-d <decay>|--decay=<decay>)] \
[(-m <max>|--maximum=<max>)] \
[(-r <r>|--radius=<r>)] \
[(-w|--wiki)] \
[(-t <thr>|--threshold=<thr>)] \
[--tanh=<coeff>] \
[(-v|--verbose)]
    photons.py (-h|--help)
    photons.py --version

Options:
    -d <decay>, --decay=<decay>             Specify decay rate [default: 1e6]
    -t <thr>, --threshold=<thr>             Specify decay rate [default: 230]
    -e <ext>, --extension=<ext>             Specify extension [default: gif]
    -m <max>, --maximum=<max>               Specify photon count[default: 255]
    -f <filename>, --filename=<filename>    Specify file to transform
    -r <r>, --radius=<r>                    kernel radius [default: 11]
    -w --wiki                               Make web page describing photons
    --tanh=<coeff>                          tanh intensity [default: 0.0]
    -v --verbose                            Show details about execution
    -h --help                               Show this screen
    --version                               Show version

"""

from cPickle import (load, dump)
from random import (seed, random, randrange)
from scipy import (zeros, ones, array, maximum, exp, sqrt, tanh)
from scipy.misc import (imsave, toimage)
from scipy.ndimage.interpolation import(zoom)
from itertools import (product)
from subprocess import (Popen, PIPE)

import re

from w3.HTML4_01.Html import (Html)
from font.BIOSfont.BIOSfont import (FONT)

def execTAGs(s):
    toExec = ''
    for tag in s.split(','):
        toExec += "exec('%s = HTML.%s');" % (tag, tag)
    return toExec

def save(data, P, M, fmt, font, **kw):
    coeff = float(kw.get('--tanh', 0.0))
    count = "%07d" % (P)
    annotation = ["%02x" % (ord(c)) for c in count.lstrip('0')]
    if kw.get('--verbose', False):
        print annotation
    # TODO use BIOSFONT to annotate image
    #for n, code in enumerate([eval('0x%s' % (val)) for val in annotation]):
        #font.text(data, "a", (1,1))

    #if kw.get('constrain', False):
        #image = toimage(data, cmax=256, cmin=0, mode='RGB')
    #else:
        #image = toimage(data, mode='RGB')
    if coeff != 0.0:
        temp = tanh(coeff * data)
        image = toimage(temp, mode='RGB')
    else:
        image = toimage(data, mode='RGB')
    image = toimage(zoom(image, (4.0, 4.0, 1.0), order=0), mode='RGB')
    filename = fmt % (count)
    image.save(filename)
    return filename

def final(data, X, Y, **kw):
    decay = float(kw.get('--decay', '5e0'))
    threshold = int(kw.get('--threshold', '230'))
    maximum = int(kw.get('--maximum', '255'))

    print 'decay', decay, kw
    data[:,:,1] = (
        exp(-decay*data[:,:,1].astype(float)/256.0)
        *256).astype(int)
    image = toimage(data, mode='RGB')
    image.save('response.gif')
    G = array(data[:,:,1], float)
    data[:,:,:] = 0
    for y in range(2, Y-2):
        for x in range(2, X-2):
            if False:
                a = G[y-1:y+2,x-1:x+2].sum() / 9
                c = G[y,x]
                r = int(127 + (c - a)/2.0)
                if r > threshold:
                    data[y,x,1] = 255
            else:
                # (-2,+2)(-1,+2)(+0,+2)(+1,+2)(+2,+2)
                # (-2,+1)(-1,+1)(+0,+1)(+1,+1)(+2,+1)
                # (-2,+0)(-1,+0)(+0,+0)(+1,+0)(+2,+0)
                # (-2,-1)(-1,-1)(+0,-1)(+1,-1)(+2,-1)
                # (-2,-2)(-1,-2)(+0,-2)(+1,-2)(+2,-2)
                xy = x * y
                ax, ay = abs(x), abs(y)
                axy = abs(xy)
                center = G[y,x]
                if ay < 2:
                    # Along X axis
                    surround = (
                        (G[y+1,x-1]+G[y+1,x+1]) +
                        (G[y,x-1]+G[y,x+1]) +
                        (G[y-1,x-1]+G[y-1,x+1])
                        ) / 6.0
                elif ax < 2:
                    # Along Y axis
                    surround = (
                        (G[y-1,x+1]+G[y+1,x+1]) +
                        (G[y-1,x]+G[y+1,x]) +
                        (G[y-1,x-1]+G[y+1,x-1])
                        ) / 6.0
                elif xy < 0:
                    # Along down diagonal
                    surround = (
                        (G[y+0,x+1]+G[y-1,x+0])+
                        (G[y-1,x+1]+G[y+1,x-1])+
                        (G[y+0,x-1]+G[y+1,x+0])+
                        (G[y+0,x-2]+G[y+2,x+0])+
                        (G[y-2,x+0]+G[y+0,x+2])
                        ) / 10.0
                else:
                    # Along up diagonal
                    surround = (
                        G[y-1,x-1]+G[y+1,x-2]+G[y-2,x+0]+
                        G[y+1,x+1]+G[y+2,x+0]+G[y+0,x+2]+
                        G[y+1,x-1]+G[y-1,x+1]+G[y+1,x+0]+G[y+0,x+1]
                        ) / 10.0
                data[y,x,1] = int((center-surround) > threshold) * 255
    image = toimage(data, mode='RGB')
    image.save('laplace.gif')

def makeGIFs(HTML, **kw):
    ftype = kw.get('<ext>', 'gif')
    threshold = int(kw.get('--threshold', '230'))
    maximum = int(kw.get('--maximum', '255'))
    style = """\
"\
image-rendering: -moz-crisp-edges; \
image-rendering:   -o-crisp-edges; \
image-rendering: =webkit-optimize-contrast; \
image-rendering: crisp-edges; \
image-rendering: pixelated; \
-ms-interpolation-mode: nearest-neighbor; \
"
"""
    exec(execTAGs("H1,H2,H3,P,DIV,BR,IMG,text"))
    with H2():
        text("Create a movie from photon accumulations")
    with H3():
        text("Fetch resources")
    with P():
        text("""
A single photon from a single point source may be absorbed almost anywhere.
""")
        pass
    # use X.py to make an Airy kernel for convolution in "As".  Fetch it.
    resource = 'Airy.kernel.11.pkl'
    text("Fetch the convolution kernel made by X.py")
    text('and stored in the file "%s".' % (resource))
    with open(resource) as source:
        (shape, Xs, Ys, Rs, As) = load(source)

    font = FONT()

    X, Y = shape  # The GIF movie image size is the same as the kernel.
    Is = As**2  # The kernel is a wave function.  Square it to get intensity.
    Is /= Is.max()  # Normalize the intensity function.
    pshape = (X, Y, 3)
    data = zeros(pshape, int)  # Start image data with a no photon field.

    text("A movie of size (%d,%d) will be made." % (X,Y))
    BR()

    N, P = 0, 0  # N is the loop count.  P is the photon absorption count.
    last = False

    fmt = ftype + '/Airy.kernel.11.%s.' + ftype
    starname = fmt % ('*')
    cmd = "rm " + starname
    Popen([cmd], shell=True, stdout=PIPE).communicate()
    with DIV(align="center"):
        while True:
            M = 0
            N += 1  # Increment loop count
            x, y = [randrange(d) for d in (X, Y)]  # Choose a random position.
            if random() < Is[y][x]:  # If probability is within range
                if data[y][x][1] >= maximum:
                    filename = save(data, P, M, fmt, font, **kw)
                    last = True
                if not last:
                    data[y][x][1] += 1  # Add 1 photon to the image
                    M = max(M, data[y][x][1])
                    # M is used as a maximum intensity for annotations.
                P += 1  # and increase the absorption count.
                filename = save(data, P, M, fmt, font, **kw)  # save this image
                rows = 8
                imgs = 4
                if P <= imgs*rows:  # or last:
                    X4, Y4 = [edge*4 for edge in list(shape)]
                    #if last:
                        #BR()
                        #BR()
                        #BR()
                    IMG(
                            src=filename,
                            alt='%d photons' % (P),
                            title='%d photons' % (P),
                            #width="%d"%(X4),
                            #height="%d"%(Y4),
                            #style=style,
                            )
                    if not P&3:
                        BR()
            if last:
                final(data, X, Y, **kw)
                break
    gifname = "photons.%d.%d.gif" % (maximum, threshold)
    cmd = "convert -delay 1 -loop 0 " + starname + " " + gifname
    Popen([cmd], shell=True, stdout=PIPE).communicate()
    print '%d steps (%d photons).' % (N, P)
    return filename

def image(HTML, filename, XY=(100,100)):
    exec(execTAGs("IMG"))
    X, Y = XY
    IMG(
            src=filename,
            alt=filename,
            title=filename,
            width='%dpx' % (X),
            height='%dpx' % (Y),
       )

def wiki():
    HTML = Html()
    wiki = """
Visual photons are typically produced/consumed
by electrons jumping from one energy state to another
in a volume typically at atomic scale (1&Aring;).
The path taken between production and consumption
cannot be known.
The relative probability of photon consumption
on an image plane is calculable.
Variations in medium density are responsible
for the shape of the probability curve.
Refraction arises from increases/decreases in density.
Diffraction arises from boundaries between
opaque and transparent medium.
Standard formulae are published for these probability curves.

Small aperture images formed when photon counts are low
appear to violate laws of optics.
Words like "scatter" and "noise" are used indiscriminately.
Scatter results from photon probabilities inconsistent with optics.
Noise results from differential photon transduction or non-photon events.
"""
    exec(execTAGs("HEAD,BODY,STYLE,DIV,TABLE,TR,TD,IMG,P,text"))
    with HEAD():
        pass
    with BODY():
        pattern = re.compile(r'(\r\n){2,}|(\n\r){2,}|(\r){2,}|(\n){2,}')
        for paragraph in pattern.split(wiki):
            with P():
                text(paragraph)
    with open('wiki.html', 'w') as target:
        print>>target, HTML

def main():
    from docopt import (docopt)
    kw = docopt(__doc__, version="0.0.1")

    if kw.get('--wiki', False):
        wiki()

    seed()

    HTML = Html()
    exec(execTAGs("HEAD,BODY,STYLE,DIV,TABLE,TR,TD,IMG,text"))
    with HEAD():
        with STYLE(type="text/css"):
            text("""\
    img { 
     image-rendering: optimizeSpeed;             /* NO SMOOTHING, GIVE ME SPEED  */
     image-rendering: -moz-crisp-edges;          /* Firefox                      */
     image-rendering: -o-crisp-edges;            /* Opera                        */
     image-rendering: -webkit-optimize-contrast; /* Chrome (and maybe Safari)    */
     image-rendering: optimize-contrast;         /* CSS3 Proposed                */
     -ms-interpolation-mode: nearest-neighbor;   /* IE8+                         */
    }
    """)

    with BODY(align="center"):
        HTML.mark('A')
        with DIV():
            final = makeGIFs(HTML, **kw)
            M, T = [int(kw[key]) for key in ['--maximum', '--threshold']]
            source = [
                    ["photons.%d.%d.gif" % (M,T), "photon absorptions"],
                    [final, "final photon absorptions"],
                    ["response.gif", "physiological response"],
                    ["laplace.gif", "radial laplacian"],
                    ]
            with TABLE(border="1", align="center"):
                with TR():
                    for i in range(len(source)):
                        with TD(align="center"):
                            image(HTML, source[i][0])
                with TR():
                    for i in range(len(source)):
                        with TD(align="center"):
                            text('<BR />'.join(source[i][1].split(' ')))
        HTML.mark('B')
        content = HTML.between('A', 'B')
    #with open('photons' + '.html', 'w') as html:
        #print>>html, str(HTML)
    with open('photons' + '.html', 'w') as php:
        print>>php, content

main()

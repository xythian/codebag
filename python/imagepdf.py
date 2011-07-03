#!/usr/bin/python

import sys
import os
import pyx

sys.path.insert(0, '/home/fox/src/workspace/singleshot/src')
sys.path.insert(0, '/home/fox/src/workspace/singleshot/lib')

from singleshot.jpeg import JpegHeader
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, KeepTogether
from reportlab.platypus.flowables import Flowable

data = []

for f in os.listdir('images'):
    if f.endswith('.jpg'):
        o = JpegHeader('images/' +f)
        data.append((o.iptc.datetime, o))

data.sort()

f = open('files.txt', 'wt')

for k, o in data:
    print >>f, o.path

f.close()


class CartoonBlock(Flowable):
    def __init__(self, img, xoffset=0, size=None):
        self.img = img
        self.size = size
        self.xoffset = xoffset

    def wrap(self, *args):
        return (self.xoffset, self.size)

    def draw(self):
        canvas = self.canv
        h, w = float(self.img.height), float(self.img.width)
        if not self.img.iptc.caption:
            fsz = 5.0
        else:
            fsz = 0.85*inch
        if w > h*1.3:
            fsz = 0.25*inch
        s = self.size - fsz
        if h > w:
            ratio = w / h
            h = s
            w = s * ratio
        else:
            ratio = h / w
            w = s
            h = s * ratio
        img = Image(self.img.path, height=h, width=w)
        w, h = img.wrap(w, h)
        iw, ih = w, h
        imgx, imgy = (self.size - s - (fsz/2.0), self.size - h)
        img.drawOn(self.canv, imgx, imgy)
        print "%.2f x %.2f (%.2f x %.2f dpi)" % (w/inch, h/inch, float(o.width) / (w/inch), float(o.height) / (h/inch) )
        p = Paragraph(self.img.iptc.caption, styleN)
        w, h = p.wrap(self.size - 10.0, 1.3*inch)
        print "Text %.2f x %.2f" % (w/inch, h/inch)
        p.drawOn(self.canv, 3.0, (imgy - h) - 3.0)
        canvas.rect(imgx, imgy, iw, ih, stroke=1, fill=0)

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']
story = []

#add some flowables
for k, o in data:
    h = float(o.height) / 150.
    w = float(o.width) / 150.
    story.append(CartoonBlock(img=o, size=4.5*inch))

# 6.625" x 10.25

doc = SimpleDocTemplate('mydoc.pdf',pagesize = (6.625*inch, 10.25*inch),
                        topMargin = 0.5*inch,
                        leftMargin = 0.5*inch,
                        bottomMargin= 0.5*inch,
                        rightMargin = 0.5*inch)
doc.build(story)

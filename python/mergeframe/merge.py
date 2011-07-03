#!/usr/bin/python2.2
import Image
import sys
import os
import glob
import ImageFont
import ImageDraw

back = Image.open('travelogue-polaroid1.png')

def merge_image(inputfile):
    tgt = back.copy()

    target = Image.open(inputfile)
    w, h = target.size
    if w > 205 or h > 195:
        target = target.resize((205, 195), Image.ANTIALIAS)
        w, h = target.size
    t1 = Image.new("RGBA", (w+30, w+30))
    t1.paste(target, (15, 15))
    target = t1.rotate(10, Image.BICUBIC)
    tgt.paste(target, (20,10))
    tgt.paste(back, (0,0), back)
    return tgt

info = {}
for line in open('source/info.txt'):
    [name,caption,caption2] = line[:-1].split(',')
    info[name] = (caption, caption2)

captionfont = ImageFont.truetype('DEARJI__.TTF', 30)
#caption2font = ImageFont.truetype('DEAR_JI__.TTF', 15)

for path in glob.glob('source/*.jpg'):
    img = merge_image(path)
    bn = os.path.basename(path)
    root, ext = os.path.splitext(bn)
    (caption, caption2) = info[root]
    w, h = captionfont.getsize(caption)    
    captionbuffer = Image.new("RGBA", (w+30,h+30))
    draw = ImageDraw.Draw(captionbuffer)
    draw.text((15,15), caption, font=captionfont,fill=(0,0,0))
#    if caption2 != '-':
#        draw.text((200,220), caption2, font=caption2font)
    draw2 = captionbuffer.rotate(10, Image.BICUBIC)
    img.paste(draw2, (45,215), draw2)
    img.save('output/%s' % bn, "JPEG")
                      
#tgt.save(sys.stdout, "JPEG")

#tgt.save(open('out.jpg', 'wb'), "JPEG")


#!/usr/bin/python
"""Generate some rounded corner images for use in a CSS hack.  From 2006 -- obsolete now."""
import Image
import ImageDraw
import ImageChops

def hextotuple(h):
    vals = h[:2], h[2:4], h[4:6]
    toval = lambda x: eval('0x%s' % x)
    return tuple([toval(r) for r in vals])

boxcolor = hextotuple('CCE0DE')
boxcolor = hextotuple('81B1AD')

corners = (("tl", None),
           ("br", Image.ROTATE_180),
           ("bl", Image.FLIP_TOP_BOTTOM),
           ("tr", Image.ROTATE_270))

corner = Image.open("corner2.gif")
corner = corner.resize((10, 10), Image.ANTIALIAS)
corner = ImageChops.invert(corner)

for name, rotation in corners:
    if rotation:
        mask = corner.transpose(rotation)
    else:
        mask = corner
    box = Image.new("RGBA", (10, 10), boxcolor)
    box.putalpha(mask)
    box.save(name + ".png")

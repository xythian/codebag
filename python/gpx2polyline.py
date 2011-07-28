#
# Draw a map with a skate on it.
#

import sys
from numpy import array
import xml.parsers.expat
from mx.DateTime import ISO

EPSILON = 0.0000001

class Location(object):
    def __init__(self, lat, lon, time):
        self.point = array([lon, lat])
        self.time = ISO.ParseAny(time).ticks()

    def vect(self, dest):
        td = dest.time - self.time
        v = dest.point - self.point
        return v / td

def between2(p1, p2):
    return (p1[0] - p2[0])**2. + (p1[0] - p2[0])**2.

class Span(object):    
    def __init__(self, begin):
        self.begin = begin
        self.end = begin
        self.v = None

    def extend(self, point):
        if self.v is None: 
            # sure, we can extend
            self.end = point
            self.v = self.begin.vect(self.end)
            return True
        td = point.time - self.end.time
        extrap = self.end.point + (self.v * td)
        if between2(extrap, point.point) < EPSILON:
            self.end = point
            self.v = self.begin.vect(self.end)
            return True
        else:
            return False

class Track(object):
    def __init__(self):
        self.track = []
        self.inpoint = False
        self.intime = False
        self.points = 0

    def append(self, point):
        self.points += 1
        if not self.track:
            self.track.append(Span(point))
        else:
            if not self.track[-1].extend(point):
                self.track.append(Span(point))

    def start_element(self, name, attrs):
        if name == 'trkpt':
            self.inpoint = True
            self.lat = float(attrs['lat'])
            self.lon = float(attrs['lon'])
        elif name == 'time' and self.inpoint:
            self.intime = True
            self.time = ''

    def end_element(self, name):
        if name == 'time':
            self.intime = False
        elif name == 'trkpt' and self.inpoint:
            self.inpoint = False
            self.append(Location(self.lat, self.lon, self.time))

    def character_data(self, data):
        if self.intime:
            self.time += data        

    def parse(self, f):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.character_data
        p.ParseFile(f)

try:
    fn = open(sys.argv[1], "r")
except os.error:
    print "Can't open %s" % sys.argv[1]
    sys.exit(1)


track = Track()
track.parse(fn)
fn.close()

def togpoint(p):
    return "new GPoint(%f, %f)" % tuple(p.point)

out = sys.stdout
out.write("// %d track points simplified to %d points\n" % (track.points, len(track.track)))
out.write("map.centerAndZoom(%s, 4);\n" % togpoint(track.track[0].begin))

polypoints = [togpoint(span.end) for span in track.track]
polypoints.insert(0, togpoint(track.track[0].begin))

out.write("var pl = new GPolyline([%s]);" % ",".join(polypoints))
out.write("map.addOverlay(pl);\n")

out.close()

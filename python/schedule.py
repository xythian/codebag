from BeautifulSoup import BeautifulSoup
import apsw
import re
from pylab import *


DIGITS = re.compile('\d+')

def parse_stationinfo(name):
    soup = BeautifulSoup(open(name, 'rt').read())
    table = soup.find('table', border='1')
    stations = {}
    for row in table.findAll('tr'):        
        columns = row.findAll('td')
        if not columns:
            # header row
            continue
        
        zone = str(columns[0].string)
        station = str(columns[1].find(text=True).string)
        if station == '22nd St.':
            # sigh
            station = '22nd Street'
        elif station[-1] == '.':
            # trim the trailing . in California Ave.
            station = station[:-1]
        mile = 47.5 - float(columns[3].find(text=True).string)
        if mile < 0:
            continue
        stations[station] = (zone, mile)
    bymile = list((mile, station) for station, (zone, mile) in stations.items())    
    return stations, bymile

def tominute(when):
    ix = when.find(':')
    return int(when[:ix])*60 + int(when[ix+1:])

def fmtminute(when, pos=None):
    hours = int(when / 60)
    minutes = (when - hours*60)
    return '%d:%02d' % (hours, minutes)

def fmtminute_tick(when, pos=None):
    ampm = ' am'
    if when > 12*60-1:
        ampm = ' pm'
        when -= 12*60
    if when > 12*60-1:
        ampm = ' am'
        when -= 12*60
    hour = int(when/60)
    if hour == 0:
        hour = 12
    return  str(hour) + ampm
    


    

def main():
    cursor = None
    stations, stationsbymile = parse_stationinfo('caltrain_stations.html')
    timetable = BeautifulSoup(open('timetable.html', 'rt').read())
    def ttfind(name):
        return timetable.find('a', attrs={'name':name}).findNextSibling('table')

    def parse_timetable(table):
        trains = []
        firstrow = table.find('tr')    
        for th in firstrow.findAll('th', text=DIGITS):
            trains.append([str(th), []])
        for row in firstrow.findNextSiblings('tr'):        
            stationname = str(row.find('th').string)
            stationname = stationname.replace('&nbsp;', ' ').strip()
            if not stations.get(stationname):
                continue
            for i, td in enumerate(row.findAll('td')):
                if td.contents:
                    when = str(td.contents[0])
                    if when != '-':
                        trains[i][1].append([stationname, when])
        # now fix 12hr times
        laststart = 0
        for train, stops in trains:
            last = 0
            for i, [name, when] in enumerate(stops):
                x = tominute(when)
                if last > x or (i == 0 and laststart > x):
                    afternoon = True                
                    x += 12*60
                    if last > x or (i == 0 and laststart > x):
                        # still -- must be 1am
                        x += 12*60
                    stops[i][1] = fmtminute(x)
                if i == 0:
                    laststart = x
                last = x
        return trains
    
                         
    weekday_northbound = parse_timetable(ttfind("weekday-northbound"))
    weekday_southbound = parse_timetable(ttfind("weekday-southbound"))
    weekend_northbound = parse_timetable(ttfind("weekend-northbound"))
    weekend_southbound = parse_timetable(ttfind("weekend-southbound"))
    def plot_train(train, clr):
        name = train[0]
        stops = train[1]
        x = []
        y = []
        for station, when  in stops:
            when = tominute(when)
            x.append(when)
            y.append(stations[station][1])
        plot(x, y, clr + '-', linewidth=0.8)
        scatter(x, y, 5)
        # text(x[0], y[0], name, fontsize=8)
    def plot_trains(trains, clr):
        for train in trains:
            plot_train(train, clr)
    def init_axis():
        xlabel("Time of day")
        ylabel("Stations")
        ax = gca()
        yticks([float(mile) for mile, station in stationsbymile],
               [station for mile, station in stationsbymile], fontsize=7)
#        ax.yaxis.grid(True, 'major')
        ax.xaxis.grid(True, 'major')
        ax.xaxis.set_major_formatter(FuncFormatter(fmtminute_tick))
        ax.xaxis.set_major_locator(FixedLocator(arange(0, 1440+120, 120)))
        ax.xaxis.set_minor_locator(FixedLocator(arange(0, 1440+120, 30)))
        xlim(0, 1440)

    figure()
    init_axis()
    title('Caltrain Weekday Schedule')
    plot_trains(weekday_northbound, 'g')
    plot_trains(weekday_southbound, 'g')
    savefig('weekday')
    figure()
    init_axis()
    title('Caltrain Weekend/Holiday Schedule')
    plot_trains(weekend_northbound, 'k')
    plot_trains(weekend_southbound, 'k')
    savefig('weekend')
    show()
    return


if __name__ == '__main__':
    main()

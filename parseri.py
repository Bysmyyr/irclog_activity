
#!/usr/bin/python

# remember to install humour-sans to use XKCD

# GPL 2
# copyright Olli Syrjala (Bysmyyr)

import sys
import re
from dateutil import parser
import pandas
import ConfigParser


#IRSSI = re.compile('[0-9 :]+<[@+ ]?([^>]+)>.*')  #this not work
WEECHAT = re.compile(r'^(?P<day>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})\s+[+@%]?(?P<nick>\S+)')


def printing(data, days, users, output_path, colormap, xkcd, widget, outputs, plt):

    if xkcd:
        plt.xkcd(1, 100, 2)
    df = pandas.DataFrame(data, columns=users, index=days)

    for output in outputs:
        if output[0] == "rolling":
            pandas.rolling_mean(df, int(output[1])).plot(colormap=colormap)
            name = output[1]+"d"
        elif output[0] == "exp":
            pandas.ewma(df, span=int(output[1])).plot(colormap=colormap)
            name = output[1]+"exp"
        elif output[0] == "norm":
            df.plot(colormap=colormap)
            name = "norm"
        elif output[0] == "cumsum":
            df.cumsum().plot(colormap=colormap)
            name = "cumsum"
        else:
            print "output config not work:" + output[0] + ":end"
            break
        plt.title(name)
        if not widget:
            plt.legend(loc='best', fontsize='xx-small', ncol=2)
            plt.savefig(output_path + name + ".png", dpi=600)
            print output_path + name + ".png"

    if widget:
        plt.show() # show widgets


def parsefile(data, file_object, aliases, user_count, verbose):
    date = None
    for line in file_object:
        match = WEECHAT.match(line)
        if not match:
            if verbose:
                print line
            continue
        date_str = match.group('day')
        date = parser.parse(date_str)
        name = match.group('nick')
        name = name.lower()
        who = aliases.get(name)
        if not who:
            if verbose:
                print name
        else:
            if date not in data:
                data[date] = [0] * user_count
            data[date][who] += 1 #how about collections.Counter ?


def process(config_path, plt):
    Config = ConfigParser.ConfigParser()
    Config.read(config_path)
    output_path = Config.get("main", "output_path")
    colormap = Config.get("main", "colormap")
    log_folder = Config.get("main", "log_folder")

    widget =  Config.getboolean("main", "widget")
    verbose = Config.getboolean("main", "verbose")
    xkcd = Config.getboolean("main", "xkcd")


    log_files = []
    log_path_items = Config.items("log_paths")
    for key, path in log_path_items:
        log_files.append(path)

    output_configs = []
    output_items = Config.items("output_configs")
    for key, output in output_items:
        output = output.split()
        output_configs.append(output)

    users = []
    aliases = {}
    users_c = Config.items("users")
    users_c = sorted(users_c,key=lambda x: x[1])
    for user, user_id in users_c:
        users.append(user)
        aliases[user] = int(user_id)
    user_count = len(users)

    aliases_config = Config.items("aliases")
    for user, user_id in aliases_config:
        aliases[user] = int(user_id)

    data = {}

    for logfile in log_files:
        with open(log_folder+logfile) as file_object:
            parsefile(data, file_object, aliases, user_count, verbose)

    dates = []
    points = []
    data = data.items()
    data.sort()
    for t, p in data:
        dates.append(t)
        points.append(p)
    printing(points, dates, users, output_path, colormap, xkcd, widget, output_configs, plt)


def main():

    config_paths = sys.argv[2:]
    if not config_paths:
        config_paths = ['./conf']

    import matplotlib
    if sys.argv[1] is "noX":
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    for path in config_paths:
        process(path, plt)


if __name__ == "__main__":
    main()



#!/usr/bin/python

# remember to install humour-sans to use XKCD

#GPL 2
#copyright Olli Syrjälä

import sys
import re
from dateutil import parser
import pandas
import ConfigParser
import matplotlib
matplotlib.use('Agg') # use this when no Xorg. no widgets, but exported images work, commend out if you want widgets
import matplotlib.pyplot as plt

USERNAME = re.compile('[0-9 :]+<[@+ ]?([^>]+)>.*')


def printing(data, days, users, output_path, colormap, xkcd, widget, outputs):
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
        if line[0] == '-':
            dateline = line[19:]
            date = parser.parse(dateline)
            date = date.isoformat() #strip time
        elif line[6] == '<':
            name_match = USERNAME.match(line)
            if not name_match:
                if verbose:
                    print line
                continue
            name = name_match.group(1).lower()
            who = aliases.get(name)
            if not who:
                if verbose:
                    print name
            else:
                if date not in data:
                    data[date] = [0] * user_count
                data[date][who] += 1


def process(filename):
    Config = ConfigParser.ConfigParser()
    Config.read(filename)
    output_path = Config.get("main", "output_path")
    colormap = Config.get("main", "colormap")
    log_folder = Config.get("main", "log_folder")

    if Config.get("main", "widget") == '1':
        widget = True
    else:
        widget = False

    if Config.get("main", "verbose") == '1':
        verbose = True
    else:
        verbose = False

    if Config.get("main", "xkcd") == '1':
        xkcd = True
    else:
        xkcd = False

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
    for d in data:
        p = d[1]
        t = d[0]
        t = parser.parse(t)
        dates.append(t)
        points.append(p)
    printing(points, dates, users, output_path, colormap, xkcd, widget, output_configs)


def main():
    config_paths = []

    if len(sys.argv) != 0:
        i = 1
        while i < len(sys.argv):
            config_paths.append(sys.argv[i])
            i += 1
    else:
        config_paths.append("./conf")

    for path in config_paths:
        process(path)


if __name__ == "__main__":
    main()


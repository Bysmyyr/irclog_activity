irclog_activity
===============

Basic script for creating activity charts from default weechat logfile.(there is older version for irssi, check second commit) Other logfile types should be easy to add. If you do so, please submit merge request. No error detection. Errors will throw basic python errors.

Just fill the config file and run.

running: ./parseri.py noX/X [config_file]

but either noX if you do not have X(then widgets do not work)

It uses Python 2.7 and needs matplotlib and pandas.

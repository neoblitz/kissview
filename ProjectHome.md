# What is kissview? #
kissview  is an ultrasimple yet powerful webserver log analysis tool. The rationale behind this tool is to output simple visualizations gleaned from an HTTP logfile. This tool is nowhere as feature-rich as compared to the power of [awstats](http://awstats.sourceforge.net/) and neither intended to be. Thus the name **kissview** _(**Keep it Simple**, **Stupid Viewer**)_.

Kissview takes in a Apache logfile(ASCII or Gzipped) and produces a static HTML file containing  visualizations written using Google Visualization APIs.

It tries to satisfy the following requirements:
  * Be as braindead and simple as possible.
  * Provide simple, cool yet powerful visualization of the usage of a site.
  * Use the extensive visualization library provided by Google in useful ways.
  * Allow extensions to code as desired with very little effort.
  * Require no maintainance.
  * Run on archived data, run locally or fetch data from a remote site.

# Why should i use it? #
It helps answering the following questions for now:
  * What is the geographical distribution of people who access my site?
  * What files are accessed and who accesses them?
  * What spurious IPs access my site?

The future versions would allow much more detailed introspection.

# Dependencies #
  * Python gviz\_api (bundled with source) [gviz\_api\_py](http://code.google.com/apis/visualization/documentation/dev/gviz_api_lib.html)
  * html2text (Normally contained in distributions else download and install) [html2text](http://www.mbayer.de/html2text/)
  * curl (Normally contained in distributions)
  * Access to the free geoip service [geoiptool.com](http://geoiptool.com) for geoip queries.

# Usage #
  * First run logmonitor.sh from the src directory as follows:
```
$ ./logmonitor.sh <path_to_accesslog> <path_to_outputlog> [ssh <user>@<remotehost>.com]

The accesslog could either be an Apache access.log in ASCII format or gzipped format.
The ssh part is optional and required only if your access-log resides on a remote site.
```


  * Then run kissview.py to create the visualization
```
$ python kissview.py --log=<path_to_outputlog> --output=<path_to_outputhtml>

The --log directive takes as input the output of the previous command.
The --output contains path and filename of the generated HTML output.
```

  * Ideally you would want to setup a cron job for your desired time to generate the HTML periodically.

Sample Screenshots are available [here](Screenshots.md)

# Known Issues #
  * The logmonitor.sh is slow for now because of the geoiptool fetch for every IP.
  * This is tested on the standard Apache log format. If you use something different please modify kissview and logmonitor appropriately.
  * If you generate the html file on your local machine and use file:// to access the html, then clicking on the file table does not do anything. This is a known limitation of the Google Visualization APIs.To workaround this, start a local webserver and then access the file.
  * This solution may be too slow for websites with "very high" traffic volumes. This will be fixed in the next release.
  * Refer the Issues tab to see a list of issues that i am working on.

# Additional notes #
  * kissview can be very easily extended to support any other logfile.
  * Another way to do this would be to use a dynamic way of generating the HTML. This would be my next TODO.
  * There is good reason for keeping the logmonitor and kissview.py separate. Assures robustness in face of failures.
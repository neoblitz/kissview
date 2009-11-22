#!/bin/bash
# logmonitor.sh 
#
# Reads the Apache accesslog and produces a log suitable for consumption
# by kissview.py
#
# Usage: logmonitor.sh <logfile> <outfile> [location]
# 
# Copyright (C) Arun Viswanathan (arunv@arunviswanathan.com)
# This software is licensed under the GPLv3 license, included in
# ./GPLv3-LICENSE.txt in the source distribution
#---------------------------------------------------------------------------

# The logfile to access. This could be an ASCII file or a gzipped file(as is typical of archives)
LOGFILE=$1
# OUTPUT Log
OUTPUTLOG=$2
echo "Input :" $LOGFILE
echo "Output:" $OUTPUTLOG
if [ "$LOGFILE" = "" ] ; then
	echo "Missing Arguments"
	exit
fi

if [ "$OUTPUTLOG" = "" ] ; then
	echo "Missing Arguments"
	exit
fi

# Decide on the cat command to use based on the type of file
CATCMD="cat"
TYPE=`file $LOGFILE|grep -c gzip`
if [ $TYPE -eq 1 ] ; then
	CATCMD="zcat"
fi
echo $CATCMD

# If inputfile is on local system LOCATION should be left blank else specify 
# ssh <user>@<host.com>
# Note that you should have keys setup for passwordless working etc.
LOCATION=$3

# Delete stale output logs
rm -f $OUTPUTLOG

# Read the following entries: 
# ip, date, file, httpcode, referrer
# Change the file values of cut if your access log is formatted different
$LOCATION $CATCMD $LOGFILE | cut -d' ' -f1,4,7,9,11 | while read ip dt file code ref; do
	
	# Do a geoiplookup to get geolocation of the IP. We are interested in Country, City, Lat, Long
	# Part of this commandline was inspired by commandlinefu.com 
	#DETAILS=`curl -s "http://www.geoiptool.com/?IP=$ip" | html2text -ascii -nobs | egrep 'IP Address:|Latitude:|Longitude:|Country code:|City:'|cut -d: -f2 | tr -s '|' ' ' | tr -s '_' ' '| sed 's/\n/ /' | sed 's/ //g'`
	DETAILS=`curl -s "http://www.geoiptool.com/?IP=$ip" | html2text -ascii -nobs |\
	 egrep 'IP Address:|Latitude:|Longitude:|Country code:|City:'|\
	 tr '_' ' '|\
	 awk '/IP Address:/{if($4 == "|") {print "127.0.0.1,"} else {print $4 ","}}\
	 	  /Country code:/{if($4 == "()") {print "US(USA),"} else {print $4 ","}}\
	 	  /City:/{if($3 == "|") {print "LosAngeles,"} else {print $3 ","}}\
	 	  /Longitude:/{if($3 == "|") {print "-118.006,"} else {print $3 ","}}\
	      /Latitude:/{if($3 == "|"){print "33.8856,"} else {print $3 ","}} '`
	echo -n $DETAILS | sed 's/ //g' >> $OUTPUTLOG
	echo -n $file","$code","$ref",">> $OUTPUTLOG
	echo $dt | tr '[' ' ' >> $OUTPUTLOG
	echo $DETAILS $file","$code","$ref","$dt 
done
exit

#!/usr/bin/python
'''
kissview.py 

Produces a static HTML to view HTTP logs using Google Visualization APIs 
This code expects input in the format as produced by logmonitor.sh.

Usage:
    1. First run logmonitor.sh as follows:
       ./logmonitor.sh <path_to_accesslog> <path_to_outputlog> 
    2. python kissview.py --log <path_to_outputlog> --ouput <path_to_outputhtml>

Refer README for details.

Copyright (C) 2009 Arun Viswanathan (arunv@arunviswanathan.com)
This software is licensed under the GPLv3 license, included in
./GPLv3-LICENSE.txt in the source distribution
'''

# Necessary python libraries
import gviz_api
import sys
import getopt

page_template = """
<html>
<head>
  <script src="http://www.google.com/jsapi" type="text/javascript"></script>
  <script>
	var chart;   // Chart   	
	var gmap;    // GeoMap
    var table;   // File Table
    var ngip_table; //NonGeoIP table
     
	// Data Tables
    var map_dt;  // Data for geomap  
    var filefreq_dt; // Data for table
    var fileclient_dt; // Contains remote IPs corresponding to file 
	var iplocation_dt; // Contains geolocation of a IP
	var chart_dt; // Data for the chart
	var nongeoip_dt; // Data for the nongeoip table

    // Load necessary visualization libraries
    google.load('visualization', '1', {packages:['geomap']});
	google.load('visualization', '1', {packages:['table']});
	google.load('visualization', '1', {packages:['barchart']});

    // Entry Point
    google.setOnLoadCallback(buildView);  

    /* 
     * Builds the visualization
     */ 
    function buildView() {
             
         // DataTables for storing different types of data  
         filefreq_dt   = new google.visualization.DataTable(%(filefreq_json)s, 0.6);
         fileclient_dt = new google.visualization.DataTable(%(fileclient_json)s, 0.6);
         iplocation_dt = new google.visualization.DataTable(%(iplocation_json)s, 0.6);
         chart_dt = new google.visualization.DataTable(%(chart_json)s, 0.6);
         nongeoip_dt = new google.visualization.DataTable(%(nongeoip_json)s, 0.6);
         map_dt = new google.visualization.DataTable(%(map_json)s, 0.6);
                  
         // Build options for gmap
         var options = {};
         options['colors'] = [0xFF8747, 0xFFB581, 0xc06000];
         
         // Markers mode supports latitude/longitude data 
         options['dataMode']    = 'markers';
         options['width']       = 1024;
         options['height']      = 800;
         options['showZoomOut'] = false;

                  
         // Create a GeoMap object
         gmap   = new google.visualization.GeoMap(document.getElementById('map_canvas'));
         gmap.draw(map_dt, options);
         
         // Draw the Bar Graph
         drawGraph();
         
         // Draw the File Table
         drawFileTable();
         
         // Draw nongeoip table
         drawNonGeoIPTable();
         
         // This would be a good place to add more extensions...
         
    }

    /* 
     * Draws the file access table
     */ 
	function drawFileTable() {

          table = new google.visualization.Table(document.getElementById('file_div_json'));
          table.draw(filefreq_dt, {showRowNumber: true});

	      google.visualization.events.addListener(table, 'select', selectHandler);
    }

    /* 
     * Draws the Non GeoIP table
     */ 
    function drawNonGeoIPTable() {

          ngip_table = new google.visualization.Table(document.getElementById('ngip_div'));
          ngip_table.draw(nongeoip_dt, {showRowNumber: true});
    }

    /* 
     * Event handler for handling clicks on the table
     */ 
	function selectHandler() {
	      var selection = table.getSelection();
	      var message = '';
	  
	      for (var i = 0; i < selection.length; i++) {
		        var item = selection[i];
		
		        // Get the file name that was selected 
 	            var file = filefreq_dt.getFormattedValue(item.row, 0);
 	            
 	            // Get list of IPs accessing the file
 	            var ipstr= fileclient_dt.getFormattedValue(item.row, 1);

                // Clean the string of unnecessary characters. This is required
                // because i convert the python list of ipaddresses to a string.
                // A little ugly for now
		        ipstr = ipstr.replace(/'/g,'');
		        ipstr = ipstr.replace(/ /g,'');
		        ipstr = ipstr.replace(/\[/g,'');
		        ipstr = ipstr.replace(/\]/g,'');
		        
		        //Get individual IPs and sort them
		        var iparr = ipstr.split(/,/);
		        iparr = iparr.sort();
		        
		        // Find the counts of all IPs
		        var countarr = new Array();
        		for( var i = 0; i < iparr.length; i++) {
        			var count = 1;
        			while ( (i < iparr.length) && (iparr[i] == iparr[i+1])) {
        				count++;	
        				i++;
        			}
        			countarr[iparr[i]] = count;   				
        		} 	
        		
        		// Form the message to be displayed corresponding to the file click
        		var msg = '<b>File Accessed: '+file+'</b><BR><BR>';
        		for(var ip in countarr){
        		    // Get the list of rows from iplocation database which contains the 
        		    // ip. There should be only one (hopefully).
        			var rowindices = iplocation_dt.getFilteredRows([{column: 0,value: ip}]);
        			
        			// Use the indices to get the location corresponding to the IP
        			var location = iplocation_dt.getFormattedValue(rowindices[0],1);
        			
        			// For message
        			msg = msg + ip +' ( '+location+') '+ ' ('+countarr[ip]+' accesses)' + '<BR>';
        		}	
        		// Set the message in the details div
        		document.getElementById('details').innerHTML = msg;
        		
	      } // Outer For
	}//End of selectHandler


    /* 
     * Draws a stacked bar graph
     */ 
	function drawGraph() {
		// Create a data view 
		var dataView = new google.visualization.DataView(chart_dt);
		dataView.setColumns([0, 1, 2]);

		chart = new google.visualization.BarChart(document.getElementById('chart'));
	    chart.draw(dataView, {is3D: true, width: 800, height: 400, legend: 'bottom', isStacked:true});
		// Add over/out handlers for mouse.
		google.visualization.events.addListener(chart, 'onmouseover', barMouseOver);
		google.visualization.events.addListener(chart, 'onmouseout', barMouseOut);

	}

	function barMouseOver(e) {
		chart.setSelection([e]);
	}	
  
	function barMouseOut(e) {
		chart.setSelection([{'row': null, 'column': null}]);
    }  	


  </script>
  <style type="text/css">
	.info {
	    font-size: 12px;
		display: block;
		text-align: left;
		font-family: Verdana, Arial, sans-serif;
		background: #f0f0f0;	
		color: #000000;
		font-weight: normal;
		padding-left: 4px;
	}

	.head {
	    font-size: 14px;
		display: block;
		text-align: center;
		font-family: Verdana, Arial, sans-serif;
		background: #000000;	
		color: #ffffff;
		font-weight: bold;
	}
	h1 {
	    font-size: 24px;
		display: block;
		text-align: center;
		font-family:  Verdana, Arial, sans-serif;
		color: #F0F0F0;
		background-color: #000000;
		font-weight: bold;
	}
	h2 {
	    font-size: 14px;
		text-align: center;
		font-family:  Verdana, Arial, sans-serif;
		font-weight: bold;
	}
	h3 {
	    font-size: 12px;
		text-align: center;
		font-family:  Verdana, Arial, sans-serif;
		font-weight: normal;
	}
  </style>
</head>
  <body>
	<h1> Webserver Access Log %(sdate)s - %(edate)s </h1>
	<h2> Created using <a href="http://code.google.com/p/kissview/">kissview</a>: Keep It Simple, Stupid Viewer</h2>
	<h3> <a href="http://code.google.com/p/kissview/">kissview</a> (the Keep it Simple, Stupid Viewer) takes in a Apache logfile(ASCII or Gzipped) and produces a static HTML file containing 
visualizations written using Google Visualization APIs.</h3>
    <h3> <a href="mailto:arunv@arunviswanathan.com">Arun Viswanathan</a></h3>
	<table border=0 cellpadding=20>
	<tr>
		<td colspan=2>
			<center>
				<p class="head"> GeoMap (Measures your popularity in the world!) </p>
				<div id="map_canvas"></div>
			</center>
		</td>
	</tr>
	<tr>
		<td valign="top">
			<p class="head"> Unique and Total Visitor Counts </p>
			<div id="chart"></div>
			<p></p>
			<p class="head"> IPs without any GeoLocation Information </p>
            <div id="ngip_div"></div>
		</td>
		<td valign="top">
			<p class=head> Click on table rows to find Remote IPs responsible for the file access </p> 
			<p></p> 
			<div id="details" class=info></div>
			<p></p>
			<div id="file_div_json"></div>
		</td>
	</tr>
	</table>
  </body>
</html>
"""

def main():
	# Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['log=', 'output='])
    except getopt.error, msg:
        print 'python kissview.py --log [access log] --output [output html file]'
        sys.exit(2)
    
    log        = ''
    htmlout    = ''

    # Process options
    for option, arg in opts:
        if option == '--log':
          log = arg
        elif option == '--output':
          htmlout = arg
	try:
		file = open(log,"r")
	except:
		print ("ERR: Could not Open File")
		sys.exit(2);
	
    try:
        outfile = open(htmlout,"w")
    except:
        print ("ERR: Could not Open File for writing HTML output!")
        sys.exit(2);
    
    
    # Hashes for storing computed data
    iphash = {}
    totalvisitshash = {}	
    uniquevisitshash = {}	
    latlonghash = {}	
    filefreqhash = {}	
    fileclienthash = {}	
    iplocationhash = {}
    nongeoiphash = {}

    # Start Date and End Date
    sdate = None
    edate = None
    
    # Read the file line by line and process the input
    for line in file:
        fields = line.split(',')
        if(len(fields) < 9):
        	continue
        
        # Split the line 
        # Expected format:
        #ip countrycode(countrycode) city long lat url status referrer date 
        ip       = fields[0]
        country  = fields[1]
        city     = fields[2]	
        long     = fields[3]	
        lat      = fields[4]	
        url      = fields[5]	
        status   = fields[6]	
        referrer = fields[7]	
        dt = fields[8]	
        
        # Assume that the first line is the startdata
        if not sdate:
        	sdate = dt
        
        # Increment the number of accesses per IP
        if ip in iphash:
        	iphash[ip] = iphash[ip] + 1
        else:
        	iphash[ip] = 1
        
        # Increment the number of accesses per url
        if url in filefreqhash:
        	filefreqhash[url] = filefreqhash[url] + 1
        else:
        	filefreqhash[url] = 1
        
        if url in fileclienthash:
        	l = fileclienthash[url]
        	l.append(ip)
        else:
        	fileclienthash[url] = [ip]
        
        # We proceed only if the IP was successfully geolocated
        # If lat and long are seen that means atleast country is resolved.
        # City may not be resolved.
        if lat and long:
            if city == "NONE":
                lockey = "UnknownCity"+","+country.split('(')[0]
            else:
                lockey = city + "," + country.split('(')[0]
            
            latlang = lat + "," + long + "," + lockey
        
            #Store location corresponding to a IP
            #An IP always has a single location (well it should)
            iplocationhash[ip] = lockey
        
            # Record unique IPs from a region
            if iphash[ip] == 1:
        	       if lockey in uniquevisitshash:
        		          uniquevisitshash[lockey] = uniquevisitshash[lockey]+1
        	       else:
        		          uniquevisitshash[lockey] = 1
        	
            # Total visits from a particular location	
            # A location can have many IPs associated with it thus the addition
            if lockey in totalvisitshash:
                totalvisitshash[lockey] = totalvisitshash[lockey] + 1
            else:
                totalvisitshash[lockey] = 1
            
            if latlang in latlonghash:                    
                latlonghash[latlang] = latlonghash[latlang] + 1
            else:
                latlonghash[latlang] = 1
        else:
            # Put the nongeolocated IPs in a separate hash
            if ip in nongeoiphash:
                nongeoiphash[ip] = nongeoiphash[ip] + 1
            else:
                nongeoiphash[ip] = 1 
            
    file.close()

    # The last record will be the one from which end date is computed            
    if not edate:
		edate = dt

    # Create schemas for all the data tables to be passed to the Javascript
    table_description = {"location": ("string", "Location"),
						 "uvisitors": ("number", "Unique Visits"),
						 "tvisitors": ("number", "Total Visits")}
  
    file_description = {"filepath": ("string", "Filepath"),
						 "frequency": ("number", "Frequency")}
	
    filehash_description = {"filepath": ("string", "Filepath"),
						 "ips": ("string", "IPs")}

    iplocation_description = {"ip": ("string", "IP"),
						 "location": ("string", "Location")}
    
    nongeoip_description = {"ip": ("string", "IP"),
                            "freq": ("number", "Frequency")}
	
    map_description = {"lat": ("number", "LATITUDE"),
					   "long": ("number", "LONGITUDE"),
					   "value": ("number", "Total Visits"),
					   "hover": ("string", "HOVER")	}
	
    # Populate with actual data
    table_data = []
    for lockey, tvisits in totalvisitshash.iteritems():
			h = {'location':lockey, 'uvisitors':uniquevisitshash[lockey],'tvisitors': tvisits}
			table_data.append(h)
	
    file_data = []
    for file, freq in sorted(filefreqhash.iteritems()):
			h = {'filepath':file, 'frequency': freq}
			file_data.append(h)
	
    iplocation_data = []
    for ip, loc in sorted(iplocationhash.iteritems()):
			h = {'ip':ip, 'location': loc}
			iplocation_data.append(h)
	
    filehash_data = []
    for file, ips in sorted(fileclienthash.iteritems()):
            # Note: I am converting the ips list to a string
            # for ease of use. There is definitely a better way
            # but i want to avoid declaring difficult table_descriptions
			h = {'filepath':file, 'ips': str(ips)}
			filehash_data.append(h)
	
    map_data = []
    for latlong, ip in latlonghash.iteritems():
			la = float(latlong.split(',')[0]) 	
			lg = float(latlong.split(',')[1]) 	
			loc = latlong.split(',',2)[2]
			h = {'lat':la, 'long':lg, 'value':ip, 'hover':loc}
			map_data.append(h)
    
    nongeoip_data = []
    for ip, freq in sorted(nongeoiphash.iteritems()):
            h = {'ip':ip, 'freq': freq}
            nongeoip_data.append(h)
    
    # Load data into gviz_api.DataTable 
    map_data_table = gviz_api.DataTable(map_description)
    map_data_table.LoadData(map_data)
	
    table_data_table = gviz_api.DataTable(table_description)
    table_data_table.LoadData(table_data)

    file_data_table = gviz_api.DataTable(file_description)
    file_data_table.LoadData(file_data)
	
    filehash_data_table = gviz_api.DataTable(filehash_description)
    filehash_data_table.LoadData(filehash_data)

    iplocation_data_table = gviz_api.DataTable(iplocation_description)
    iplocation_data_table.LoadData(iplocation_data)
	
    nongeoip_data_table = gviz_api.DataTable(nongeoip_description)
    nongeoip_data_table.LoadData(nongeoip_data)
    
	# Create JSON strings 
    # Note that these variables are embedded in the javascript above
    chart_json = table_data_table.ToJSon(columns_order=("location", "uvisitors", "tvisitors"))
    map_json = map_data_table.ToJSon(columns_order=("lat", "long","value","hover"))
    filefreq_json = file_data_table.ToJSon(columns_order=("filepath", "frequency"))
    fileclient_json = filehash_data_table.ToJSon(columns_order=("filepath", "ips"))
    iplocation_json = iplocation_data_table.ToJSon(columns_order=("ip", "location"))
    nongeoip_json = nongeoip_data_table.ToJSon(columns_order=("ip", "freq"))

	# Put the JSon string into the template
    # Magic of Python !!!
    outfile.write("\n");
    outfile.write(page_template % vars())
    outfile.close()



if __name__ == '__main__':
	main()

# vim: tabstop=4 shiftwidth=4 softtabstop=4

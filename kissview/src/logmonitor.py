
# Requirements
# 
# 1. Download the GeoLiteCity database from 
#    wget -N -q http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
# 2. Uncompress the file
# 3. Install pygeoip python libraries
#
#    Installation instructions
#        http://code.google.com/p/pygeoip/wiki/Install
#    Usage instructions
#        http://code.google.com/p/pygeoip/wiki/Usage

import pygeoip

gi = pygeoip.GeoIP('../tars/GeoLiteCity.dat', pygeoip.MEMORY_CACHE)
print gi.record_by_addr("203.195.93.0")


# Usage 
#
#>>> import pygeoip
#>>> gic = pygeoip.GeoIP('/path/to/GeoIPCity.dat')
#>>> gic.record_by_addr('64.233.161.99')
#{'city': 'Mountain View', 'region_name': 'CA', 'area_code': 650, 'longitude': -122.0574, 'country_code3': 'USA', 'latitude': 37.419199999999989, 'postal_code': '94043', 'dma_code': 807, 'country_code': 'US', 'country_name': 'United States'}
#>>> gic.record_by_name('google.com')
#{'city': 'Mountain View', 'region_name': 'CA', 'area_code': 650, 'longitude': -122.0574, 'country_code3': 'USA', 'latitude': 37.419199999999989, 'postal_code': '94043', 'dma_code': 807, 'country_code': 'US', 'country_name': 'United States'}
#>>> gic.region_by_name('google.com')
#{'region_name': 'CA', 'country_code': 'US'}
#>>> gic.region_by_addr('64.233.161.99')
#{'region_name': 'CA', 'country_code': 'US'}
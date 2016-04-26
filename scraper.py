# This is the scraper that collects the aged care data.

import scraperwiki
import os
import requests

if os.path.isfile("providers.xlsx") == False: # This checks if the providers file has been downloaded (mainly for faster development)

	dls = 'https://www.dss.gov.au/sites/default/files/documents/02_2016/service_list_-_australia.xlsx'

	resp = requests.get(dls)
	with open('providers.xlsx', 'wb') as output:
	    output.write(resp.content)

import pandas as pd

providers = pd.read_excel('providers.xlsx',skiprows=[0]) # Load the providers.
resi = providers[providers['Care Type']=='Residential']	# Filter out non-reisidential providers.
names = resi['Service name'].tolist() # Create a list, ready for the lookup process.
subs = resi['Physical Address Suburb'].tolist()

# Now let's search the aged care for each home and capture the data we want. Some searches will return multiple homes, so we will also match the suburb.
# The website has multiple entries for some homes, so we will just take the first one.

# We want two tables, one for the general details of each home and one for each room offered (with a field linking it to the home)
import json

ids = []

print 'Length:',len(names)
for i,name in enumerate(names):
	print i,name
	url = "https://servicefinder.myagedcare.gov.au/api/acg/v1/agedCareHomeFinder"

	payload = "{\"agedCareHomeFinderRequest\":{\"agedCareHomeFinderInput\":{\"serviceType\":\"Residential Permanent\",\"catersForDiverseNeedsFlag\":\"false\",\"name\":\"%s\"}}}"%name
	headers = {
	    'accept': "application/json",
	    'x-env-dss': "UAT03",
	    'origin': "https//servicefinder.myagedcare.gov.au",
	    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36",
	    'x-api-key': "7ca4c25771c54ca283c682a185e72277",
	    'content-type': "application/json",
	    'referer': "https//servicefinder.myagedcare.gov.au/service-finder?tab=aged-care-homes",
	    'accept-encoding': "gzip, deflate",
	    'accept-language': "en-US,en;q=0.8",
	    'cookie': "X-Mapping-omgbnpna=BD3B66FC92A02E30955C08E08600418A; _gat=1; _ga=GA1.3.1705425098.1461048959; X-Mapping-omgbnpna=BD3B66FC92A02E30955C08E08600418A; _gat=1; _ga=GA1.3.1705425098.1461048959; X-Mapping-omgbnpna=BD3B66FC92A02E30955C08E08600418A; _ga=GA1.3.1705425098.1461048959; _gat=1",
	    'cache-control': "no-cache",
	    'postman-token': "c9ee5217-9a1c-df1d-1991-5210e0845728"
	    }

	response = requests.request("POST", url, data=payload, headers=headers, verify=False)
	jso = json.loads(response.text) # Create a json object out of the response

	# Now let's save the IDs
	if len(jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']) > 1: # This means there was both a response message and an object with results
		if type(jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']['agedCareHomes']['agedCareHome']) == list: # If more than one home was returned...
			for home in jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']['agedCareHomes']['agedCareHome']:
				#print home['businessAddress']['suburb'],subs[i]
				if home['businessAddress']['suburb']==subs[i]:
					ids.append([name,subs[i],home['iD'],home['serviceID']]) # ... save the ids of the first one
					break # ... before stopping (because we are happy to have a record with the correct name and suburb)
		else:
			#print name,jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']['agedCareHomes']['agedCareHome']['businessAddress']['suburb'],subs[i]
			if jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']['agedCareHomes']['agedCareHome']['businessAddress']['suburb']==subs[i]: # If there was just one results
				ids.append([name,subs[i],jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']['agedCareHomes']['agedCareHome']['iD'],jso['agedCareHomeFinderResponse']['agedCareHomeFinderOutput']['agedCareHomes']['agedCareHome']['serviceID']])
	else: # No records found
		ids.append([name,subs[i],None,None])

# So now we have the ids, let's get the results we want.
# We will make two tables, one for the general residential care info and one for the separate room info.
#print ids

#ids = [[u'501 Respite & Care Services', u'BIGGERA WATERS', u'1-E6-2072', u'1-EP-49'], [u'70 Lowe Street', u'ARARAT', u'1-E6-962', u'1-EP-393'], [u'A H Orr Lodge', u'ASHFIELD', u'1-E6-10', u'1-EP-1025'], [u'A M Ramsay Village', u'PORT AUGUSTA', u'1-E6-1545', u'1-EP-3240'], [u'A. G. Eastwood Hostel', u'CHELTENHAM', u'1-AU-58', u'1-B5-29'], [u'Abberfield Aged Care Facility', u'SANDRINGHAM', u'1-AU-88', u'1-B5-147'], [u'Abbeyfield Hostel', u'WILLIAMSTOWN', None, None], [u'Abbeyfield House Hostel', u'MORTLAKE', u'1-E6-804', u'1-GHXQUQ'], [u'Abel Tasman Village', u'CHESTER HILL', u'1-E6-263', u'1-EP-2022'], [u'Abernethy Nursing Home', u'CESSNOCK', u'1-E6-663', u'1-EP-7305'], [u'Abrina Nursing Home', u'ASHFIELD', u'1-E6-406', u'1-EP-5353'], [u'Acacia House Residential Aged Care Service', u'SHEPPARTON', u'1-E6-1094', u'1-17R42Q'], [u'ACDMA Aged Hostel', u'CANLEY VALE', u'1-E6-271', u'1-EP-1233'], [u'Ada Cottage', u'KANDOS', u'1-E6-238', u'1-EP-104'], [u'Adelene Court Hostel', u'WYOMING', u'1-E6-143', u'1-EP-4020'], [u'Adelene Nursing Home', u'WYOMING', u'1-E6-586', u'1-EP-3059'], [u'Adria Village Ltd', u'STIRLING', u'1-E6-705', u'1-EP-4077'], [u'Advantaged Care at Barden Lodge', u'BARDEN RIDGE', u'1-E6-2336', u'1-EP-74'], [u'Advantaged Care at Georges Manor', u'GEORGES HALL', u'1-E6-2346', u'1-EP-2137']]

general = []
rooms = []
for i in ids:
	row = dict()
	url = "https://servicefinder.myagedcare.gov.au/api/acg/v1/getHomeDetails"

	payload = "{\"getHomeDetailsRequest\":{\"getHomeDetailsInput\":{\"iD\":\"%s\",\"serviceID\":\"%s\",\"fundedFlag\":\"true\"}}}"%(i[2],i[3])
	headers = {
	    'accept': "application/json",
	    'x-env-dss': "UAT03",
	    'origin': "https//servicefinder.myagedcare.gov.au",
	    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36",
	    'x-api-key': "7ca4c25771c54ca283c682a185e72277",
	    'content-type': "application/json",
	    'referer': "https//servicefinder.myagedcare.gov.au/service-finder/aged-care-home-detail/item-detail-id-0?d=1-E6-804&svc=1-MAAJUC&fnd=y",
	    'accept-encoding': "gzip, deflate",
	    'accept-language': "en-US,en;q=0.8",
	    'cookie': "X-Mapping-omgbnpna=BD3B66FC92A02E30955C08E08600418A; _ga=GA1.3.1705425098.1461048959; _gat=1; X-Mapping-omgbnpna=BD3B66FC92A02E30955C08E08600418A; _gat=1; _ga=GA1.3.1705425098.1461048959; X-Mapping-omgbnpna=BD3B66FC92A02E30955C08E08600418A; _ga=GA1.3.1705425098.1461048959; _gat=1",
	    'cache-control': "no-cache",
	    'postman-token': "7921ee2d-db4c-f61e-06da-a05717ea653d"
	    }

	response = requests.request("POST", url, data=payload, headers=headers,verify=False)
	#print response.text
	jso = json.loads(response.text)

	print i[0],i[1]
	if 'homeDetails' in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"].keys(): # First, let's get all the basic info
		for key in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"].keys():
			if key == 'serviceSubTypes':
				if u'homeServiceSubType' in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key].keys():
					if type(jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key]['homeServiceSubType']) == list: # If there is more than one room listed
						for room in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key]['homeServiceSubType']:
							roomrow = {'home':i[0],'suburb':i[1],'iD':i[2],'serviceID':i[3]}
							for roomkey in room.keys():
								if roomkey == 'attributes':
									for attr in room['attributes']['attribute']:
										roomrow[attr['name']] = attr['value']
								elif roomkey in [u'commonAreaDescription',u'explanationOfPaymentOptions',u'commonAreaDescription',u'additionalCare',u'roomDescription',
									u'specificFeatures',u'extraServiceFees','additionalAmenitiesAtExtraCost']:
									pass
								else:
									roomrow[roomkey] = room[roomkey]
							scraperwiki.sqlite.save(unique_keys=[], data=roomrow)
					else:
						roomrow = {'home':i[0],'suburb':i[1],'iD':i[2],'serviceID':i[3]}
						for roomkey in room.keys():
							if roomkey == 'attributes':
								for attr in room['attributes']['attribute']:
									roomrow[attr['name']] = attr['value']
							elif roomkey in [u'commonAreaDescription',u'explanationOfPaymentOptions',u'commonAreaDescription',u'additionalCare',u'roomDescription',
								u'specificFeatures',u'extraServiceFees','additionalAmenitiesAtExtraCost']:
								pass
							else:
								roomrow[roomkey] = room[roomkey]
						scraperwiki.sqlite.save(unique_keys=[], data=roomrow)


			elif key != 'serviceInventoryAttributes' and key != 'attachmentList':
				if type(jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key]) == dict:
					for key2 in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key].keys():
						if type(jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2]) == dict:
							for key3 in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2].keys():
								if type(jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2][key3]) == dict:
									for key4 in jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2][key3].keys():
										if type(jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2][key3][key4]) == dict:
											row[key+ "_" + key2 + "_" + key3 + "_" + key4] = str(jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2][key3][key4])
										else:
											row[key+ "_" + key2 + "_" + key3 + "_" + key4] = jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2][key3][key4]
								else:
									row[key+ "_" + key2 + "_" + key3] = jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2][key3]	
						else:
							row[key+ "_" + key2] = jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key][key2]
				else:
					row[key] = jso["getHomeDetailsResponse"]["getHomeDetailsOutput"]["homeDetails"][key]
		scraperwiki.sqlite.save(unique_keys=[], data=row)
		#general.append(row)
	else:
		print 'NO HOME DETAILS'
	#pd.DataFrame(general).to_csv('general.csv',encoding='utf-8')
	#pd.DataFrame(rooms).to_csv('rooms.csv',encoding='utf-8')
	print ''
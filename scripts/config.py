'''
	This is the config file for the autoreport script.
	Modify this for the project/task you as configuring this for

'''


#dictionary declarations
dataPath = {}
dataNameFields ={}
searchDistance = {}
inputFields = {}



'''CONFIG SECTION
	dataPath[layername] = path
	dataNameFields[layername] = dictionary of template variable, fieldnames
	these two dictionaries must have identical keys, or you will get yelled at

	searchDistance[layername] = max distance to look for a spatial intersection from centroid
'''



'''
dictionary of GIS data paths
any arcgis supported vector data should work

example: dataPath['name'] = r'\path\to\data'
'''
dataPath['supportdata'] = r'C:\Users\porters1\Dropbox\Work\GVS_Work\AutoReport\fromODNR\Auto_PDF_Project\Reporting_Feature_Classes.gdb\SupportData_Project'


'''
field to template text mappings for the above data paths
fieldname:templatevalue

templatevalues are the placeholders in the template such as {name} which will be replaced using the value in the field from the source data
example: dataNameFields['name'] = {"field_name":"name","field_name2":"name2"}

the keys of this dictionary must match the keys of dataPath
'''
dataNameFields['supportdata'] = {"county":"COUNTY","township":"Township_1","section":"SectionNum","quad":"QUAD_NAME","watershed":"HU_12_Name"}


'''
distance to search from input layer for intersecting features in projected units within each respective data source

example: searchDistance['name'] = 1000
would search for example 1000 feet from the input in layer 'name' for an intersection if the projection is in feet. Closest feature in this range is returned.
'''
searchDistance['supportdata'] = 10

#polygon types
inputFields  = {'date':'Edit_Date','acres':'Acres','comments':'Comment','priority':'Priority','keyword':'PT_Abbrev','staff':'Staff'}


#be careful here
batchMode = True #allow iteration over several features? if FALSE input must be a layer with a single feature (or selected feature)

#file output format, filedate and padno are defined later
outputFormat = u'{staff}_{priority}{keyword}_{filedate}_{padno}.htm'

#
#
#END CONFIG
#
##########################################

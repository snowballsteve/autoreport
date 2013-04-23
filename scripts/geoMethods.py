'''
  geoMethods.py
  supporting classes and methods for the autoreport tool
  
  author -- steven c. porter
  version -- 3

'''
import arcpy, os, math, sys

class geoProcessor:
	'''      
		Geoprocessor class for the autopdf script.
		Handles the spatial intersections and relationships   
		
	'''

	def __init__(self, input_geom):
		'''
		Class constructor

		input_geom - an input layer, or geometry object,  representing only one geometry

		'''
		
		#garbage collection, since the arctoolbox model does not do this
		if arcpy.Exists("in_memory\centroidLayer"): self.cleanUp() 
		if arcpy.Exists("in_memory\layer"): arcpy.Delete_management("in_memory\layer")
		
		#only the centroid of the input geometry will be used
		self.point = arcpy.PointGeometry(input_geom.centroid)
		self.centroidLayer = arcpy.CopyFeatures_management(self.point, "in_memory\centroidLayer")
		
		#get the input type
		inlayer = arcpy.CopyFeatures_management(input_geom,'in_memory/temp') #doing his allows us to work with geometry objects also 
		self.inputLayerType = arcpy.Describe(inlayer).shapeType
		arcpy.Delete_management(inlayer)
			
	def featureIn(self, layer, namefields,threshold):
		'''
			Returns the content of namefield of the feature layer in which the centroid lies
			First by checking for an intersection relationship, if that returns null then
			Searches within the threshold.
			
			Keyword arguments:
			layer -- layer to test against the centroid
			namefields -- a dictionary of name, and fieldnames to return for intersecting features
			threshold -- distance in map units to look for intersecting feature
			
			Returns:
				dictionary of name:fieldvalues
		'''
		result = self.featureNear(layer, namefields, 1)
		if result == {}:
			return self.featureNear(layer, namefields, threshold)
		else:
			return result
		
	def featureNear(self, layer, namefields, threshold):
		'''
			Returns the content of namefield of the feature layer within the threshold of the centroid
			In the case of more than one result for layer within the threshold of the centroid, results are ordered by increasing distance
			The namefields dictionary contains a key for each with a numerical increment at the end of the key
		
			Keyword arguments:
			layer -- layer to test against the centroid
			namefields -- a dictionary of name, and fieldnames to return for intersecting features
			threshold -- distance in projected units to search
			
			Returns:
				dictionary of name:fieldvalues
		'''
		
		#verify that layer exists
		if not arcpy.Exists(layer) : arcpy.AddError("%s does not exist, or is not found")

		olayer = layer
		#perform selection by location
		layer = arcpy.CopyFeatures_management(layer, "in_memory\layer")
		selectLayer = arcpy.MakeFeatureLayer_management(layer,"selectLayer")
		arcpy.SelectLayerByLocation_management(selectLayer, "WITHIN_A_DISTANCE", self.centroidLayer,threshold,"NEW_SELECTION")
		selectedLayer = arcpy.CopyFeatures_management(selectLayer, "in_memory\selectedLayer")
		
		#we now have a layer of selected features, time to build the dictionary		
		
		
		#sort the selection by distance, this returns a sorted list of dictionary representation of the layer
		rows = self.sortRowsByDistance(self.point,selectedLayer) 
		
		#create empty dict
		result = {}

		
		#loop over the sorted selection
		i = 0
		for row in rows:
			#loop over the fields of each row
			#checking against passed namefields
			for name,field in namefields.iteritems():
				if i>0: name = name + str(i) #append a numerical increment to key
				result[name] = row[field]
			i+=1
			
		#if we had more than one result, print a warning
		if i > 1:
			arcpy.AddWarning("%d intersections found with %s" %(i,olayer))

		#cleanup
		arcpy.Delete_management(layer)
		arcpy.Delete_management(selectLayer)
		arcpy.Delete_management(selectedLayer)
		
		return result
	
	def sortRowsByDistance(self,comparisonPoint,layer):
		'''
			returns a list of dictionary data structures representing the row structure of layer in order of increasing distance form comparisonpoint
			
			comparisonPoint -  arcpy.Point geometry
			layer - arcgis layer to be sorted and returned
			
		'''
		rowlist = []
		distlist = []
		fieldlist = self.getFieldNames(layer)
		for row in arcpy.SearchCursor(layer):
			rowDict ={}
			for field in fieldlist:
				rowDict[field] = row.getValue(field)
			rowlist.append(rowDict)
			st = arcpy.Describe(layer).shapeType
			if st == 'Point' or st == 'MultiPoint':
				distlist.append(self.distanceBetweenPoints(row.shape,comparisonPoint.centroid))
			elif st == 'Polygon':
				distlist.append(self.distPointFromPolygon(comparisonPoint.centroid,row.shape))
			elif st == 'Polyline':
				distlist.append(self.distPointFromPolyline(comparisonPoint.centroid,row.shape))
			else:
				distlist.append(self.distanceBetweenPoints(row.shape.centroid,comparisonPoint.centroid))
				
		if len(rowlist)<=1: return rowlist
		else: return self.sortAbyB(rowlist,distlist)
			
		
	def distanceBetweenPoints(self,pointA,pointB):
		''' returns the distance between two point objects, must be projected coordinates '''
		return math.hypot(pointB.X-pointA.X,pointB.Y-pointA.Y)
		
	
	def sortAbyB(self,listA,listB):
		''' returns list A sorted based on corrosponding values in list B '''
		combined = zip(listB,listA)
		combined.sort()
		sortedB, sortedA = zip(*combined)
		
		return sortedA
	
	def getFieldNames(self,layer):
		''' 
			Returns a list of field names that exist in the layer
			Keyword Arguments:
			layer -- a feature layer
		'''
		fields = arcpy.ListFields(layer)
		names = []
		for field in fields:
			names.append(field.name)
			
		return names
	
	def ringToPoints(self,polygon):
		'''a recursive function that returns a list of ring coordinates'''
		rings = []
		if polygon.isMultipart:
			for i in range(0,polygon.partCount-1):
				for item in self.ringToPoints(polygon.getPart(i)):
					rings.append(item)
		else:
			rings.append(polygon.getPart(0))
			
		return rings
		
	def distPointFromSegment(self,point, segPointA, segPointB):
		''' distance from point to line segment segPointA - segPointB '''
		m = math.hypot(segPointB.X - segPointA.X,segPointB.Y - segPointA.Y)
		
		u1 = ((point.X - segPointA.X) * (segPointB.X - segPointA.X)) + ((point.Y - segPointA.Y) * (segPointB.Y - segPointA.Y))
		u = u1 / m
		
		
		if u < 0 or u > 1: #point is closest to line segment end point
			dbp = math.hypot(segPointB.X - point.X,segPointB.Y - point.Y)
			dap = math.hypot(segPointA.X - point.X,segPointA.Y - point.Y)
			if dbp > dap: return dap
			else: return dbp
		else: #calculate distance to point on line segment and perpindicular line that passes through input point
			x = segPointA.X + u * (segPointB.X - segPointA.X)
			y = segPointA.Y + u * (segPointB.Y - segPointA.Y)
			return math.hypot(x - point.X, y - point.Y)
		
		
	def distPointFromPolygon(self,point, polygon):
		''' get distance from point to polygon '''
		if polygon.contains(point): return 0 #if point inside polygon, then distance is zero
		else: return self.distPointFromPolyline(point,polygon) #else distance is from ring segments
			
		
			
	def distPointFromPolyline(self, point, polyline):
		''' get distance from point to polyline '''
		dist = None
		rpoints = self.ringToPoints(polyline)
		for ring in rpoints:
			for i in range(0,len(ring)-2):
				d = self.distPointFromSegment(point,ring[i],ring[i+1])
				if dist == None: dist = d
				elif d < dist: dist = d
		return dist
		
		
	def cleanUp(self):
		''' delete the in memory centroid layer so that we can use this class again '''
		arcpy.Delete_management("in_memory\centroidLayer")

class templateParser:
	'''
		Template parser class for the AutoPDF script
		Handles the opening of templates, parseing text, and producing output
	'''
	
	def __init__ (self):
		pass

	def is_number(self, s):
		'''returns true if s can be converted to a float, credit to George Stocker on stackoverflow'''
		try:
			float(s)
			return True
		except ValueError:
			return False
		except TypeError:
			return False

	def formatText(self, format_dict):
		'''
			Iterates over a dictionary and returns the same dictionary with formated values
			
			Keyword arguments:
			format_dict -- dictionary whose values need to be capitalized
		'''
		for k,v in format_dict.iteritems():
			if self.is_number(v): 
				v = round(float(v),1) #round all numbers
				if int(v) == v: v = int(v) #convert to int if this is an int
			format_dict[k] = str(v) #.capitalize() #capitalize formatting
		return format_dict

	def readTemplate(self,fileTemplate):
		'''
			reads content of template file and returns a list of each line

			Keyword arguments:
			fileTemplate -- the template file

		'''

		#read template file to string
		template = open(fileTemplate)
		templateText = template.readlines()
		template.close
		return templateText

	def writeResult(self,template_text,swap_dict,fileOutput):
		'''
			writes formatted string to result file line by line
			if file exists creates file_n where n is the next available number

			Keyword arguments:
			template_text -- list of template lines
			swap_dict -- dictionary to use in string formatting
			fileOutput -- the path of the output file

		'''

		#if file exists, keep looping to find file_number to write.
		n=1
		fileOutput2 = fileOutput
		while os.path.exists(fileOutput2):
				fileOutput2 = os.path.splitext(fileOutput)[0]+"_%s" %(n)+os.path.splitext(fileOutput)[1]
				n=n+1
				
		del(n)
		fileOutput = fileOutput2
		del(fileOutput2)
		
		#write output, format string using dictionary keys
		output = open(fileOutput,'w')
		output.write(self.swapText(template_text, swap_dict)) 
		output.close()
		arcpy.AddMessage("Wrote output to %s" %(fileOutput))

	def swapText(self, inputStringList, swap_dict):
		'''
			Formats inputStringList item by item (idea is that this list is each line of a file) using the dictionary as the keys to swap
			returns output as string
		'''
		output = ''
		for line in inputStringList:
			loutput = ''
			for lex in line.split(' '):
				try:
					loutput = loutput + str(lex).format(**self.formatText(swap_dict)) + ' '
				#there are some inherit problems doing this, but since there is css in the templates, this ignores other brackets
				#preventing them from breaking the tool without diving into xml parser methods
				#dump the line as is without formatting
				except ValueError:
					loutput = loutput + str(lex) + ' '
				except KeyError:
					loutput = loutput + str(lex) + ' '
					
			output = output + str(loutput) + '\n\r'	
		return output

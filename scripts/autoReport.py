'''
  AutoReport script
  Usage -- ./autoReport.py inputLayer OutputFolder templateFile
  
  Author -- Steven C. Porter
  Version -- 5
    
'''
import arcpy, sys, os, geoMethods
from geoMethods import geoProcessor
from geoMethods import templateParser


#import the config file
from config import *


#get inputs
arguments = {}
dataPath['in_layer'] = arcpy.GetParameter(0)
outputFolder = arcpy.GetParameterAsText(1)
templatefile = arcpy.GetParameterAsText(2)

def autorun():
	'''
		This function controls the process if this python script is run as main (which is the intended purpose)
	'''
	
	
	if not checkInputs():
		arcpy.AddError("Input Error")
		sys.exit(1)  #inputs did not check out, abort
		
	rows = arcpy.SearchCursor(dataPath['in_layer'])
	for row in rows:
		#lets create the geoProcessor object
		auto_gp = geoProcessor(row.Shape)
		
		
		searchDistance['in_layer'] = 1
		
		if not checkConfig():
			arcpy.AddError("Config Error")
			sys.exit(1)  #config did not check out, abort
		

		#run geoprocessing iterations
		swapDict = {}
		for layer in dataPath.keys():
			if not layer == "in_layer":
				result = auto_gp.featureIn(dataPath[layer],dataNameFields[layer],searchDistance[layer])
				swapDict.update(result)
				
		auto_gp.cleanUp()
		
		#append input to swapdict
		result = {}
		for name,field in dataNameFields['in_layer'].iteritems():
			result[name] = row.getValue(field) 
		swapDict.update(result)

		#error report
		for k in dataNameFields.keys():
			for item in dataNameFields[k].keys():
				if not item in swapDict.keys(): arcpy.AddWarning("Value for %s from layer %s not found within %d projected Units" %(item,k,searchDistance[k]))
		
		auto_tp = templateParser()
	
		auto_tp.writeResult(auto_tp.readTemplate(templatefile),swapDict,outputFolder +'\\'+ outputFormat.format(**swapDict))
		
		#close
		
	pass
	

def checkInputs():
	'''
		Checks the user input
			Does layer exist? 
			Does it have records?
			Batchmode, only one record?
			
	'''
	#does input layer exist
	if not arcpy.Exists(dataPath['in_layer']): 
		arcpy.AddError("Input Layer\n%s\nDoes not exist or is not supported" %(dataPath['in_layer']))
		return False
	
	#any records?
	n_records = int(arcpy.GetCount_management(dataPath['in_layer']).getOutput(0))
	if n_records == 0:
		arcpy.AddError("No records found in input\n%s" %(dataPath['in_layer']))
		return False
		
	#if not in batchmode, there must be only 1 input record
	if not batchMode:
		if not n_records  == 1: 
			arcpy.AddError("%d records found in input\n%s\nBatchmode is not enabled" %(n_records,dataPath['in_layer']))
			return False
		
	#if we get this far, yay!
	return True

def checkConfig():
	'''
		Checks the configuration of this script.
			Are all data paths valid?
			Are all fields present?
			Do keys match?
	'''
	
			
	#both dictionaries should have identical keys
	if not sorted(dataPath.keys()) == sorted(dataNameFields.keys()) or not sorted(dataPath.keys()) == sorted(searchDistance.keys()):
		arcpy.AddError("Configuration dictionaries do not have identical keys.\n Please check configuration of these keys\n\t%s\n\t%s\n\t%s" %(sorted(dataPath.keys()),sorted(dataNameFields.keys()),sorted(searchDistance.keys())))
		return False
	
	
	#check all support data
	for layer,path in dataPath.iteritems():
		#does layer exist
		if not arcpy.Exists(path): 
			arcpy.AddError("Path to configured layer\n%s\nis invalid or not supported" %(path))
			return False
		#do the namefields exist
		for name in dataNameFields[layer].values():
			if not name in getFieldNames(path): 
				arcpy.AddError("Field %s does not exist in layer\n%s\n" %(name,path))
				return False
				
	#if we get this far, yay!
	return True
	
def getFieldNames(layer):
	''' Returns a list of field names that exist in the layer'''
	fields = arcpy.ListFields(layer)
	names = []
	for field in fields:
		names.append(field.name)
		
	return names
	
def vLookup(table,lookField,lookValue,targetField):
	''' does a table look up in one field and returns value of another'''
	lookrows = arcpy.SearchCursor(table)
	targetValue = ''
	for lookrow in lookrows:
		if lookrow.getValue(lookField) == lookValue: targetValue = lookrow.getValue(targetField)
	
	del lookrows
	return targetValue
		
#if this script is executed then we run the main function
if __name__ == '__main__':
	autorun()

import os
import time
import datetime
import re
import sys
import math
#import Queue
import random

def showMenu():
	print("")
	print("Menu:")
	print("m:  shows this menu")
	print("h:  shows the header (first) rows of the file")
	print("t:  shows the tail (last) rows of the file")
	print("e:  shows sample example rows selected randomly in the file")
	print("r:  replaces one string with another ('rx' does the same for regexps)")
	print("c:  toggles the source file")
	print("s:  scans file for a string and prints lines where found ('sx' for regexps)")
	print("d:  checks the dimensions (data columns) row-by-row given a separator")
	print("dx: removes all rows that don't have the right number of dimensions")
	print("n:  gives the number of rows in a file")
	print("l:  splits a large file into multiple smaller ones")
	print("f:  filters only rows where a dimension matches a value ('fx' for regexp)")
	print("z:  prints the name of the current file being worked on")
	print("p:  toggles printing to a file versus printing to console" )
	print("q:  closes / quits the program")
	print("")
	print("General utilization tips:")
	print("The input files need to be in the same folder where this program is executed.")
	print("If you to iterate through the entire file, enter a negative number (e.g. -1)")
	print("when a sample number is requested")
	print("")

def showHeaderRows():
	global nSampleRows
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	# start the main iteration
	sourceFile = open(inputFileName, "r")
	initializeOutputFile()
	for i in range(0, nSampleRows):
		outputString(sourceFile.readline())
	sourceFile.close()
	closeOutputFile()

def showTailRows():
	global nSampleRows
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	# start the main iteration
	fNumLines = numLines()
	lineCounter = 0
	initializeOutputFile()
	sourceFile = open(inputFileName, "r")
	for line in sourceFile:
		lineCounter += 1
		if lineCounter > fNumLines - nSampleRows:
			outputString(line)
	sourceFile.close()
	closeOutputFile()

def showExampleSampleRows():
	global nSampleRows, fileNumLines
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	initializeOutputFile()
	sourceFile = open(inputFileName, "r")
	# excluding the header, create an array of rows that will be selected
	selectedRowsArray = random.sample(range(2, numLines()-1), nSampleRows)
	selectedRowsArray.sort()
	print(selectedRowsArray)
	# get the first line
	with open(inputFileName, 'r') as sourceFile:
		outputString(sourceFile.readline())
    # print out the rest
	j = 0
	i = 0
	sourceFile = open(inputFileName, "r")
	for line in sourceFile:
		if i == selectedRowsArray[j]:
			outputString(line)
			j += 1
			# break if we reached end of selected rows
			if j == len(selectedRowsArray):
				break
		i += 1
	closeOutputFile()

def numLines():
	global fileNumLines
	if fileNumLines < 0:
		with open(inputFileName, "r") as f:
			for i, l in enumerate(f):
				pass
		fileNumLines = i + 1
	print(">> File has " + "{:,}".format(fileNumLines) + " lines")
	return fileNumLines

def checkDimensions():
	global lastSeparator, nSampleRows
	lastSeparator = input("Provide the separator[" + lastSeparator + "]: ") or lastSeparator
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	# start the main iteration
	sourceFile = open(inputFileName, "r")
	initializeOutputFile()
	lineCounter = 0
	headerDimensions = 0
	resultDims = {}
	for line in sourceFile:
		lineCounter += 1
		lineDim = len(line.split(lastSeparator))
		# increment the value in the dictionnary
		if not lineDim in resultDims:
			resultDims[lineDim] = 1
		else:
			resultDims[lineDim] += 1
		# final operations before ending loop
		if lineCounter == 1:
			headerDimensions = lineDim
		if lineCounter == nSampleRows:
			break
	# print out results
	outputString(">> Analyzed " + "{:,}".format(lineCounter) + " lines")
	outputString(">> Header # of dimensions: " + "{:,}".format(headerDimensions))
	for k, v in resultDims.items():
		outputString(">> " + "{0:.2f}".format(float(v)/lineCounter*100) + "% (#" + "{:,}".format(v) + ") of lines with " + str(k) + " dimensions")
	sourceFile.close()
	closeOutputFile()

def cleanUpDimensions():
	global lastSeparator, nSampleRows
	lastSeparator = input("Provide the separator[" + lastSeparator + "]: ") or lastSeparator
	# get the number of dimensions from the header
	sourceFile = open(inputFileName, "r")
	firstline = sourceFile.readline()
	numDimensions = len(firstline.split(lastSeparator))
	sourceFile.close()
	# now we can continue querying for correct dimension number and sample rows
	numDimensions = input("Provide the correct number of dimensions[" + str(numDimensions) + "]: ") or numDimensions
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	# start the main iteration
	sourceFile = open(inputFileName, "r")
	initializeOutputFile()
	lineCounter = 0
	changedLines = 0
	for line in sourceFile:
		lineCounter += 1
		if len(line.split(lastSeparator)) == numDimensions:
			if not(printToConsole):
				outputString(line)
		else:
			changedLines += 1
		if lineCounter == nSampleRows:
			break
	# finished the iteration
	print(">> Finished parsing " +  "{:,}".format(lineCounter) + " lines from file")
	print(">> Made " +  "{:,}".format(changedLines) + " line deletions")
	sourceFile.close()
	closeOutputFile()

def splitFile():
	fNumLines = numLines()
	numFileSplits = getNumberfromUser("Define amount of splits required", 10)
	keepHeader = input("Keep header (Y/n): ") or "y"
	# open file and extract first line if required
	source = open(inputFileName, "r")
	firstLine = ""
	if keepHeader.lower() == "y" or keepHeader.lower() == "yes":
		firstline = source.readline()
		fNumLines = fNumLines - 1
	# define appropriate amount of lines to 
	floatNewNumLines = math.ceil(float(fNumLines) / float(numFileSplits))
	newNumLines = int(floatNewNumLines)
	lineCounter = 0
	fileLineCounter = 0
	fileCounter = 1
	# start the loop that splits the files
	copy = open(futureFileMain + "_part_" + str(fileCounter) + "." + futureFileExt, "wt")
	while lineCounter < fNumLines:
		# read and write the line
		line = source.readline()
		copy.write(str(line))
		# increase the counters
		lineCounter += 1
		fileLineCounter += 1
		# check if we need to start a new file
		if fileLineCounter >= newNumLines:
			# we need to create a new file, close the old one and reinitialize the fileLineCounter
			copy.close()
			print(">> Generated file part # " + str(fileCounter))
			fileCounter += 1
			fileLineCounter = 0
			copy = open(futureFileMain + "_part_" + str(fileCounter) + "." + futureFileExt, "wt")
			if keepHeader == 1:
				copy.write(str(firstline))
		else:
			if keepHeader == 1:
				copy.write(str(firstline))
	print(">> Generated file part # " + str(fileCounter))

def replaceRegExpOrString(regExpFlag):
	global oldRegexp, nSampleRows, fileNumLines
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	replaceThing = "string"
	if regExpFlag:
		replaceThing = "regexp"
		print(">> Note that parentheses will create groups that you can later reference with backslash number (e.g. \\1)")
	try:
		oldRegexp = input("Old " + replaceThing + " to be replaced [ "+ oldRegexp +" ]: ") or oldRegexp
		newRegexp = input("New " + replaceThing + " to replace old (e.g. .\\1\\2 ): ")
		counter = 0
		lineCounter = 0
		initializeOutputFile()
		sourceFile = open(inputFileName, "r")
		for line in sourceFile:
			lineCounter += 1
			newLine = ""
			if regExpFlag:
				regExp = re.compile(oldRegexp)
				newLine = regExp.sub(newRegexp, line)
			else:
				newLine = line.replace(oldRegexp, newRegexp)
			outputString(newLine)
			if newLine != line:
				counter += 1
			if counter == nSampleRows:
				sourceFile.close()
				closeOutputFile()
				return
		print(">> Finished parsing file with " +  "{:,}".format(lineCounter) + " lines")
		fileNumLines = lineCounter
	except:
		print(">> Unexpected error:", sys.exc_info()[0])
	sourceFile.close()
	closeOutputFile()

def scanFileForRegExpOrString(regExpFlag):
	global oldRegexp, nSampleRows, fileNumLines
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	replaceThing = "string"
	if regExpFlag:
		replaceThing = "regexp"
	oldRegexp = input("Scan the file for this " + replaceThing + "[ "+ oldRegexp +" ]:") or oldRegexp
	counter = 0
	lineCounter = 0
	initializeOutputFile()
	# get the number of dimensions from the header
	sourceFile = open(inputFileName, "r")
	firstline = sourceFile.readline()
	outputString(firstline)
	sourceFile.close()
	# now start the loop
	sourceFile = open(inputFileName, "r")
	for line in sourceFile:
		lineCounter += 1
		found = False
		if regExpFlag:
			searchObj = re.search(oldRegexp, line, flags=0)
			if searchObj:
				found = True
		else:
			if line.find(oldRegexp) > -1:
				found = True
		if found:
			counter += 1
			outputString(line)
			if counter == nSampleRows:
				sourceFile.close()
				closeOutputFile()
				return
	sourceFile.close()
	closeOutputFile()
	print(">> Finished parsing file with " +  "{:,}".format(lineCounter) + " lines")
	fileNumLines = lineCounter

def filterRows(regExpFlag):
	global oldRegexp, nSampleRows, fileNumLines, lastSeparator
	nSampleRows = getNumberfromUser("Number of sample rows requested", nSampleRows)
	filterThing = "string"
	if regExpFlag:
		filterThing = "regexp"
	oldRegexp = input("Filter the file for this " + filterThing + "[ "+ oldRegexp +" ]:") or oldRegexp
	counter = 0
	lineCounter = 0
	initializeOutputFile()
	# get the number of dimensions from the header
	lastSeparator = input("Provide the separator[" + lastSeparator + "]: ") or lastSeparator
	sourceFile = open(inputFileName, "r")
	firstline = sourceFile.readline()
	colNum = getColumnNumber(firstline, lastSeparator)
	while colNum < 0:
		colNum = getColumnNumber(firstline, lastSeparator)
	outputString(firstline)
	# now start the loop
	sourceFile = open(inputFileName, "r")
	for line in sourceFile:
		rowColumnValue = getRowColumnValue(line, lastSeparator, colNum)
		lineCounter += 1
		found = False
		if regExpFlag:
			searchObj = re.search(oldRegexp, rowColumnValue, flags=0)
			if searchObj:
				found = True
		else:
			if rowColumnValue == oldRegexp:
				found = True
		if found:
			counter += 1
			outputString(line)
			if counter == nSampleRows:
				sourceFile.close()
				closeOutputFile()
				return
	sourceFile.close()
	closeOutputFile()

# -----------------------------------------------------------------------------
# LIBRARY FUNCTIONS
# -----------------------------------------------------------------------------

def getColumnNumber(headerLine, separatorStr):
	strInput = input("Provide the column name or number: ")
	headerArr = headerLine.split(separatorStr)
	try:
		colIndex = int(strInput)
		# remove 1 to make it translatable to the array
		colIndex = colIndex - 1
		# user provided a number
		if len(headerArr) > colIndex:
			print("Selected column: " + headerArr[colIndex])
			return colIndex
		else: 
			print("Error, identifier too high for length of header")
			return -1
	except ValueError:
		colIndex = -1
		for i in range(0, len(headerArr)):
			if headerArr[i] == strInput:
				print("Found column " + headerArr[i] + " at position " + str(i))
				colIndex = i
		if colIndex == -1:
			print("Error, column name not found")
		return colIndex

def getRowColumnValue(rowStr, separatorStr, colNum):
	lineDims = rowStr.split(separatorStr)
	return lineDims[colNum]

def getNumberfromUser(strRequest, defaultValue):
	strNum = input(strRequest + "[" + str(defaultValue) + "]: ") or str(defaultValue)
	try:
		num = int(strNum)
		return num
	except ValueError:
		print(">> Didn't provide a number, defaulting to 10")
		return 10

def getSourceFileName():
	global futureFileExt, futureFileMain, fileNumLines, printToConsole, nSampleRows
	fileNumLines = -1
	print("Available files found in folder for selection:")
	listFilesInFolder(-1)
	print("")
	iFileName = input("Enter name or number of input file[" + lastFileGenerated + "]: ") or lastFileGenerated
	# do a quick check that the file is available before starting the loop
	try:
		val = int(iFileName)
		iFileName = listFilesInFolder(val)
	except:
		pass
	try:
		source = open(iFileName, "r")
		source.close()
		printToConsole = True
		nSampleRows = 10
		print(">> Found file " + iFileName)
		print(">> Defaulting to console-print (select p to toggle)")
		print(">> Type \"m\" for menu if you are unsure which functions are availble.")
		# extract the file extension and main file name for potential later re-use
		tempStr = iFileName.split(".")
		futureFileMain = tempStr[0]
		if len(tempStr) > 1:
			futureFileExt = tempStr[len(tempStr)-1]
			for i in range(1, len(tempStr)-1):
				futureFileMain = futureFileMain + "." + tempStr[i]
		return iFileName
	except:
		print(">> File not found, please provide a valid file name")
		return ""

def listFilesInFolder(requestNumber):
	fileNameRequested = ""
	dirs = os.listdir(".")
	fileCounter = 0
	for fileName in dirs:
		fileCounter += 1
		if requestNumber == fileCounter:
			return fileName
		if requestNumber < 0:
			if fileCounter < 10:
				print(str(fileCounter) + ":  " + fileName)
			else:
				print(str(fileCounter) + ": " + fileName)
	return ""

# functions for outputing stuff to a correctly timestamped file

def outputString(printStr):
	global outputFile
	if printToConsole:
		print(printStr)
	else:
		outputFile.write(printStr)
		
def initializeOutputFile():
	global outputFile, lastFileGenerated, futureFileMain
	if not(printToConsole):
		fileHasTimeStampInFront = fileNameRegExp.match(futureFileMain)
		if fileHasTimeStampInFront:
			# this file also starts with a timestamp, delete it so the one we will add later doesn't duplicate
			futureFileMain = fileNameRegExp.sub("", futureFileMain)
		outputFileName = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H%M%S') + " - " + futureFileMain + "." + futureFileExt
		outputFile = open(outputFileName, "wt")
		lastFileGenerated = outputFileName

def closeOutputFile():
	global outputFile
	if not(printToConsole):
		outputFile.close()

# -----------------------------------------------------------------------------
# MAIN PROGRAM
# -----------------------------------------------------------------------------

# initialize overall variables
version = "1.2"
usrInput = ""
outputFile = None
printToConsole = True
futureFileExt = "txt"
futureFileMain = ""
oldRegexp = ",([0-9])([0-9])"
lastUserInput = "h"
lastFileGenerated = ""
fileNumLines = -1
lastSeparator = ","
nSampleRows = 10

# prepare the main filename regexp to identify if this one of our files
fileNameRegExp = re.compile("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9][0-9][0-9][0-9][0-9] - ")

print("This is version " + version + " of the file explorer for large file exploation (by bap)")
print("")
# get a valid file name
inputFileName = getSourceFileName()
while inputFileName == "":
	inputFileName = getSourceFileName()
# main loop
while usrInput != "q":
	print("")
	usrInput = input("Call function[" + lastUserInput + "]: ") or lastUserInput
	usrInput = usrInput.lower()
	if usrInput == "h":
		showHeaderRows()
	elif usrInput == "t":
		showTailRows()
	elif usrInput == "e":
		showExampleSampleRows()
	elif usrInput == "r":
		replaceRegExpOrString(False)
	elif usrInput == "rx":
		replaceRegExpOrString(True)
	elif usrInput == "n":
		numLines()
	elif usrInput == "m":
		showMenu()
	elif usrInput == "f":
		filterRows(False)
	elif usrInput == "fx":
		filterRows(True)
	elif usrInput == "z":
		print(">> Current file name: " + inputFileName)
	elif usrInput == "s":
		scanFileForRegExpOrString(False)
	elif usrInput == "sx":
		scanFileForRegExpOrString(True)
	elif usrInput == "l":
		splitFile()
	elif usrInput == "d":
		checkDimensions()
	elif usrInput == "dx":
		cleanUpDimensions()
	elif usrInput == "c":
		tmpFileName = getSourceFileName()
		if tmpFileName != "":
			inputFileName = tmpFileName
	elif usrInput == "p":
		printToConsole = not(printToConsole)
		if printToConsole:
			print(">> Printing output to console")
		else:
			print(">> Printing output to files")
	elif usrInput == "q":
		print(">> Bye bye")
	else:
		print(">> No such command available, enter 'm' to select menu")
		usrInput = "m"
	if not(usrInput == "p" or usrInput == "v" or usrInput == "m"):
		lastUserInput = usrInput
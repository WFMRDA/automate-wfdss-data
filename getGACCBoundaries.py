#Download and unzip the GACC boundaries layer
#Check to see if the new file is different from the last file using a list of file names and hashes
#If is isn't different, delete the new file, and leave the list alone
#If it is different, keep the new file, and add it (and its hash) to the list
#Notify data manager of the results by email

#Set to run getGACCBoundaries.py as a scheduled service to get this daily, weekly, or monthly.

#Future improvements: 
#	use a file for list of emails
#	use a file for a list of download URLs
#	implement error handling
#	implement logging

#Import needed libraries
# urllib for download
import urllib
# zipfile and os.path to unzip
import zipfile,os.path 
#time for date functions
import time
#import hashlib and csv for creating, reading, and modifying file hash list
from hashlib import sha1
import csv
#import logging module to create a script output log
import logging

#set up variables
workingFolder = r'H:\Projects\AutomationTesting\\'
dateTime = time.strftime("%Y%m%d%H%M%S") 
downZipLocation = workingFolder + "GACCBoundaries" + dateTime + ".zip"
dateTimeFolder = workingFolder + "GACCBoundaries" + dateTime
hashListFile = workingFolder + 'getGACCBoundaries.hash'
logFile = workingFolder + 'getGACCBoundaries.log'

#start system log
logging.basicConfig(filename=logFile,level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.info('getGACCBoundary.py initiated at ' + dateTime)


#Download the GACC boundaries file. If download fails, fail with an error message.
try:
	urllib.urlretrieve ("http://psgeodata.fs.fed.us/data/gis_data_download/static/GACC_2012.zip", downZipLocation)
	logging.info('GACC Boundaries successfully downloaded to ' + downZipLocation)
except:
	print "File download failed. Either no file is present with that name, or the internet connection has been interrupted at the client or server"
	logging.exception("Exception handled requiring exit: File download failed. Either no file is present with that name, or the internet connection has been interrupted at the client or server")
	raise
	
#unzip the downloaded file to a date and time folder
#from phihag at http://stackoverflow.com/questions/12886768/simple-way-to-unzip-file-in-python-on-all-oses
def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)
			
#create an sha1 hash for the downloaded file
#from hughdbrown at http://stackoverflow.com/questions/6963610/how-in-python-check-if-two-files-string-and-file-have-same-content
def shafile(filename):
    with open(filename, "rb") as f:
        return sha1(f.read()).hexdigest()

#calculate the hash for the new file
newFileHash = shafile(downZipLocation)
#print the download location and the sha1 hash of the new file
print (downZipLocation, newFileHash)

#open the hash list file in read mode and read all the hashes and file names
#compare to the current downloaded file hash
#From examples in docs.python.org
try:
	with open(hashListFile, 'rb') as csvfile:
		hashListReader = csv.reader(csvfile)
		for hashRow in hashListReader:
			if hashRow[1] == newFileHash:
				print "MATCH!"
			else:
				print "NO MATCH!"
			print hashRow[1]
	csvfile.close()
except IOError:
	logging.error(hashListFile + ' does not exist. Cannot compare to older versions - there may not be any. Will create a new ' + hashListFile + ' and treat this as the first time this download has been attempted.')

#open the hash list file in append/binary mode, and write the file name 
# and sha1 hash to a file containing a list of hashes
#From examples in docs.python.org
with open(hashListFile, 'ab') as csvfile:
	hashListWriter = csv.writer(csvfile)
	hashListWriter.writerow([downZipLocation, newFileHash])
csvfile.close()

#unzip the file into a folder named with the date and time
unzip(downZipLocation, dateTimeFolder)
		
		
#psuedocode for calculating hashes of downloaded files and keeping them as a list
#checksums = []
#for url in all_urls:
#    data = download_file(url)
#    checksum = make_checksum(data)
#    if checksum not in checksums:
#         save_to_file(data)
#         checksums.append(checksum)

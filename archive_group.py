'''
Yahoo-Groups-Archiver Copyright 2015, 2017, 2018 Andrew Ferguson and others

YahooGroups-Archiver, a simple python script that allows for all
messages in a public Yahoo Group to be archived.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

cookie_T = 'COOKIE_T_DATA_GOES_HERE'
cookie_Y = 'COOKIE_Y_DATA_GOES_HERE'

import json #required for reading various JSON attributes from the content
import requests #required for fetching the raw messages
import os #required for checking if a file exists locally
import time #required if Yahoo blocks access temporarily (to wait)
import sys #required to cancel script if blocked by Yahoo
import shutil #required for deletung an old folder
import glob #required to find the most recent message downloaded
import time #required to log the date and time of run
import traceback #required for try-catch

def archive_group(groupName, mode="update"):
	log("\nArchiving group '" + groupName + "', mode: " + mode + " , on " + time.strftime("%c"), groupName)
	startTime = time.time()
	msgsArchived = 0
	if mode == "retry":
		#don't archive any messages we already have
		#but try to archive ones that we don't, and may have
		#already attempted to archive
		min = 1
	elif mode == "update":
		#start archiving at the last+1 message message we archived
		mostRecent = 1
		if os.path.exists(groupName):
			oldDir = os.getcwd()
			os.chdir(groupName)
			for file in glob.glob("*.json"):
				if int(file[0:-5]) > mostRecent:
					mostRecent = int(file[0:-5])
			os.chdir(oldDir)
		
		min = mostRecent
	elif mode == "restart":
		#delete all previous archival attempts and archive everything again
		if os.path.exists(groupName):
			shutil.rmtree(groupName)
		min = 1
		min = 51 # about kurzlist start.
		
	else:
		print ("You have specified an invalid mode (" + mode + ").")
		print ("Valid modes are:\nupdate - add any new messages to the archive\nretry - attempt to get all messages that are not in the archive\nrestart - delete archive and start from scratch")
		sys.exit()
	
	if not os.path.exists(groupName):
		os.makedirs(groupName)
	max = group_messages_max(groupName)
	for x in range(min,max+1):
		if not os.path.isfile(groupName + '/' + str(x) + ".json"):
			print ("Archiving message " + str(x) + " of " + str(max))
			sucsess = archive_message(groupName, x)
			if sucsess == True:
				msgsArchived = msgsArchived + 1
	
	log("Archive finished, archived " + str(msgsArchived) + ", time taken is " + str(time.time() - startTime) + " seconds", groupName)
		

def group_messages_max(groupName):
	s = requests.Session()
	resp = s.get('https://groups.yahoo.com/api/v1/groups/' + groupName + '/messages?count=1&sortOrder=desc&direction=-1', cookies={'T': cookie_T, 'Y': cookie_Y})
	try:
		pageHTML = resp.text
		pageJson = json.loads(pageHTML)
	except ValueError:
		if "Stay signed in" in pageHTML and "Trouble signing in" in pageHTML:
			#the user needs to be signed in to Yahoo
			print ("Error. The group you are trying to archive is a private group. To archive a private group using this tool, login to a Yahoo account that has access to the private groups, then extract the data from the cookies Y and T from the domain yahoo.com . Paste this data into the appropriate variables (cookie_Y and cookie_T) at the top of this script, and run the script again.")
			sys.exit()
	return pageJson["ygData"]["totalRecords"]

def archive_message(groupName, msgNumber, depth=0):
	global failed
	failed = False
	try:
		s = requests.Session()
		resp = s.get('https://groups.yahoo.com/api/v1/groups/' + groupName + '/messages/' + str(msgNumber) + '/raw', cookies={'T': cookie_T, 'Y': cookie_Y})
		if resp.status_code != 200:
			#some other problem, perhaps being refused access by Yahoo?
			#retry for a max of 3 times anyway
			if depth < 3:
				print ("Cannot get message " + str(msgNumber) + ", attempt " + str(depth+1) + " of 3 due to HTTP status code " + str(resp.status_code))
				time.sleep(0.1)
				archive_message(groupName,msgNumber,depth+1)
			else:
				if resp.status_code == 500:
					#we are most likely being blocked by Yahoo
					log("Archive halted - it appears Yahoo has blocked you.", groupName)
					log("Check if you can access the group's homepage from your browser. If you can't, you have been blocked.", groupName)
					log("Don't worry, in a few hours (normally less than 3) you'll be unblocked and you can run this script again - it'll continue where you left off." ,groupName)
					sys.exit()
				log("Failed to retrive message " + str(msgNumber) + " due to HTTP status code " + str(resp.status_code), groupName )
				failed = True
	except Exception as err:
		exc_type, exc_value, exc_tb = sys.exc_info()
		tbe = traceback.TracebackException(
			exc_type, exc_value, exc_tb,
		)
		print('\nProblem with Connection')
		print(''.join(tbe.format_exception_only()))
		print('\nSleeping 5 minutes to sidestep throttling/error')
		time.sleep(300)


	if failed == True:
		return False
	
	msgJson = resp.text
	writeFile = open((groupName + "/" + str(msgNumber) + ".json"), "wb")
	writeFile.write(msgJson.encode('utf-8'))
	writeFile.close()
	return True
			

global writeLogFile
def log(msg, groupName):
	print (msg)
	if writeLogFile:
		logF = open(groupName + ".txt", "a")
		logF.write("\n" + msg)
		logF.close()


if __name__ == "__main__":
	global writeLogFile
	writeLogFile = True
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	if "nologs" in sys.argv:
		print ("Logging mode OFF")
		writeLogFile = False
		sys.argv.remove("nologs")
	if len(sys.argv) > 2:
		archive_group(sys.argv[1], sys.argv[2])
	else:
		archive_group(sys.argv[1])

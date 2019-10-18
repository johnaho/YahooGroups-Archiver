#!/usr/local/bin/python
'''
Yahoo-Groups-Archiver, HTML Archive Script Copyright 2019 Robert Lancaster and others

YahooGroups-Archiver, a simple python script that allows for all
messages in a public Yahoo Group to be archived.

The HTML One Page Archive Script allows you to take the downloaded json documents
and turn them into a single html-based archive of the emails.
Note that the archive-group.py script must be run first.

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
import email
from json2html import *
import os
import sys
from datetime import datetime
from natsort import natsorted, ns
import importlib

 

def archiveYahooMessage(file, archiveFile,  format):
     try:
          f = open(archiveFile, 'a')
          f.write(convertYahooMessageIntoHtml(file, format) +  '<br /><hr><br />')
          f.close()
          print( 'Yahoo Message: ' + file + ' archived to: ' + str(archiveFile) )
     except Exception as e:
          print( 'Yahoo Message: ' + file + ' had an error:')
          print( e)

def closeArchive(archiveFile,  format):
     try:
          f = open(archiveFile, 'a')
          f.write('</body></html>')
          f.close()
          print( 'Yahoo archive closed')
     except Exception as e:
          print( 'Yahoo archive closing had an error:')
          print( e)         

def openArchive(archiveFile,  format):
     try:
          f = open(archiveFile, 'a')
          f.write('<html><head><title>In Progress One Page archive repository</title></head><body>')
          f.close()
          print( 'Yahoo archive open')
     except Exception as e:
          print( 'Yahoo archive opening had an error:')
          print( e)          

def convertYahooMessageIntoHtml(file, format):
     f1 = open(file,'r')
     fileContents=f1.read()
     f1.close()
     quicktable = json2html.convert(json = fileContents)
     messageText = quicktable
     return messageText
 
  

## This is where the script starts

if len(sys.argv) < 2:
     sys.exit('You need to specify your group name')

groupName = sys.argv[1]
oldDir = os.getcwd()
if os.path.exists(groupName):
     archiveDir = os.path.abspath(groupName + '-archive')
     if not os.path.exists(archiveDir):
          os.makedirs(archiveDir)
     os.chdir(groupName)
     archiveFile = archiveDir + '/archive-' + str(groupName) + '_one_page.html'
     openArchive(archiveFile, 'utf-8')
     for file in natsorted(os.listdir(os.getcwd())):         
          archiveYahooMessage(file, archiveFile, 'utf-8')

     closeArchive(archiveFile, 'utf-8')
else:
     sys.exit('Please run archive-group.py first')

os.chdir(oldDir)
print('Complete')



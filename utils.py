
from config       import *



def parse_data(raw_line):
  #print(raw_line)
  raw_line=raw_line.replace('\n', ' ')
  strip_line=raw_line.replace('\t',' ')
  strip_line=strip_line.replace(',',' ') #comma separated values
  split_line=strip_line.split(' ')
  data_list=[]
  for item in split_line:
    if item!='':
      data_list.append(item)
  return data_list
def sublist(list1,x1,x2,y1,y2):
  sublist=[]
  for i in range(x1,x2):
    sublist.append(list1[i][y1:y2]) #doesn't include list1[i][y2]
  return sublist

class Parser(object):
	def __init__(self,document_name):
		self.doc=open(document_name,'r')
		self.doc_lines=self.doc.readlines()
		#print(self.doc_lines)
		self.line= -1
	def parse_lines(self):	#returns integer 0 if at end of document
		try:
			self.doc_lines[self.line+1]
		except:
			return 0
		else:
			self.line += 1
		#print(self.doc_lines[self.line]+'data')
		return self.doc_lines[self.line].rstrip('\n')
	def close(self):
		self.doc.close()
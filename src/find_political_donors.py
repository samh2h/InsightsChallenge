import pandas as pd
import numpy as np
import re
import datetime
import bisect 
from operator import itemgetter


zip_codes = pd.read_csv('./us_postal_codes.csv')
total_records = [[]]
ID_Date_combination = ''
ID_Zip_combination = ''
zip_records = [[]]
date_records = [[]]
return_date_records = [[]]

def check_transaction(transaction):
	if(str(re.search('[a-zA-Z]', transaction)) != "None"):
		return False
	if(int(transaction) < 1):
		return False
	return True

def check_ID(id):
	if(len(id) != 9):
		return False
	# Check if ID is alphanumeric
	if(str(re.search('[a-zA-Z0-9]', id)) != "None"):
		return True
	return False


def check_date(dateString):
	try:
		datetime.datetime.strptime(dateString,'%m%d%Y')
	except ValueError:
		return False
	return True



def check_zip_codes(state, zip):

	state_code = zip_codes[zip_codes['State.1'] == state]

	# Checking if the state given is valid
	if(len(state_code) == 0):
		return False
	if(str(re.search('[a-zA-Z]', zip)) != "None" or len(zip) ==0):
		return False
	result = state_code[state_code['Zip Code'] == int(zip)]
	# Checking if there is at least one matching zip code in table
	if(len(result) !=0 ):
		return True
	return False

# This will allow searched to be done in O(lg(n))
def binarySearch(alist, item,recordType):
   first = 0
   last = len(alist)-1
   found = False
   midpoint = 0
   while first<=last and not found:
       midpoint = (first + last)//2
       if alist[midpoint][recordType] == item:
           found = True
       else:
         if item < alist[midpoint][recordType]:
                last = midpoint-1
         else:
                first = midpoint+1
       if(alist[midpoint][recordType] < item):
       		midpoint = midpoint + 1

   return found, midpoint


# Given the way it is stored and read, get_median has O(1)
def get_median(index, all_records):

	donar_record = (all_records[index])[1:]
	median = 0

	if (len(donar_record)) % 2 == 0:
		middleLeft = (len(donar_record)-1) /2
		middleRight = middleLeft + 1

		leftValue = int((donar_record[middleLeft])[2])
		rightValue = int((donar_record[middleRight])[2])
		median = (leftValue + rightValue + 1)/2

	elif len(donar_record) == 1:
		median = (donar_record[0])[2]

	else:
		middle = (len(donar_record)-1)/2 + 1
		median = (donar_record[middle])[2]

	return median



def get_record_sum(index,all_records):

	sum = 0
	donor_record = (all_records[index])[1:]
	for n in donor_record:
		sum += int(n[2])
	return sum


def print_zip(zip_record):
	global zip_records

	found, index =  binarySearch(zip_records,zip_record[0],0)
	return_record = (zip_record[1])
	return_string = ''
	for i in range(0, len(return_record)-1):
		return_string = return_string +'|'+return_record[i]
	return_string = return_string[1:]
	median = get_median(index, zip_records)
	count = len( (zip_records[index])[1:] )
	sum = get_record_sum(index, zip_records)
	return_string = return_string+'|'+str(median)+'|'+str(count)+'|'+str(sum)
	print(return_string)
	with open('../output/medianvals_by_zip.txt','a') as output:
		output.write(return_string+'\n')


def add_record(donor_record,total_records):

	if(len(total_records) == 0):
		total_records.append(donor_record)
		return

	result, index = binarySearch(total_records,donor_record[0],0)
	if(result == False):
		#insert into last index checked by binary sort to maintain sorted list
		total_records.insert( (index), donor_record)
	else:
		donor_records = (total_records[index])[1:]
		donorResult, donorIndex = binarySearch(donor_records, donor_record[1][2],2)

		total_records[index].insert( (donorIndex+1) , donor_record[1])


def print_date(date_record):
	global date_records
	global return_date_records

	found, index =  binarySearch(date_records,date_record[0],0)
	return_record = (date_record[1])

	return_string = ''
	for i in range(0, len(return_record)-1):
		return_string = return_string +'|'+return_record[i]
	return_string = return_string[1:]
	#print(date_records)
	median = get_median(index, date_records)
	count = len( (date_records[index])[1:] )
	sum = get_record_sum(index, date_records)
	return_string = return_string+'|'+str(median)+'|'+str(count)+'|'+str(sum)

	found, index = binarySearch(return_date_records,date_record[0],0)
	store_record = [date_record[0] ,return_string]
	if found == False:
		return_date_records.insert(index, store_record)
	else:
		return_date_records[index] = store_record

def process(account):

	global total_records
	global ID_Date_combination
	global ID_Zip_combination
	global zip_records

	input = account.split('|')


	# If the length of record is not 21, then some elements are missing
	if(len(input)!=21):
		return


	CMTE_ID=input[0]
	if(check_ID(CMTE_ID) == False):
		return

	STATE_CODE=input[9]
	ZIP_CODE=input[10][:5]
	if(check_zip_codes(STATE_CODE, ZIP_CODE) == False):
		ZIP_CODE = 'empty'


	TRANSACTION_DT=input[13]
	if(check_date(TRANSACTION_DT) == False):
		TRANSACTION_DT='empty'

	TRANSACTION_AMT=input[14]
	if(check_transaction(TRANSACTION_AMT) == False):
		return

	OTHER_ID=input[15]
	if(OTHER_ID != ''):
		return


	if(TRANSACTION_DT != 'empty'):
		ID_Date_combination = CMTE_ID+TRANSACTION_DT
	else:
		ID_Date_combination = 'empty'
	if(ZIP_CODE != 'empty'):
		ID_Zip_combination = CMTE_ID+ZIP_CODE
	else:
		ID_Zip_combination = 'empty'


	if(ID_Zip_combination != 'empty'):
		zip_record = [ID_Zip_combination, [CMTE_ID,ZIP_CODE,TRANSACTION_AMT]]
		add_record(zip_record,zip_records)
		print_zip(zip_record)

	if(ID_Date_combination != 'empty'):
		date_record = [ID_Date_combination, [CMTE_ID, TRANSACTION_DT,TRANSACTION_AMT]]
		add_record(date_record,date_records)
		print_date(date_record)

zip_records.pop(0)
date_records.pop(0)
return_date_records.pop(0)

with open('../output/medianvals_by_zip.txt','w') as output:
	output.write('')

with open('../input/itcont.txt') as f:
	for line in f:
		process(line)

print('\n\n')
for n in return_date_records:
	print(n[1])
with open('../output/medianvals_by_date.txt','w') as output:
	for n in return_date_records:
		output.write(n[1]+'\n')


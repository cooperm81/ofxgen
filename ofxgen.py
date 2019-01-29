#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3

import configparser
import argparse
import os
import sys
import logging

ofx = {
    'VERSION': '220',
    'OFXHEADER': '200',
    'SECURITY': 'NONE',
    'ENCODING': 'USASCII',
    'CHARSET': '1252',
    'COMPRESSION': 'NONE',
    'OLDFILEUID': 'NONE',
    'NEWFILEUID': 'NONE',
    'DTSTART': "",
    'DTEND': ""
}

# STEPS
# ---------------------
# read config file
# read command line options
# read profile file
# determine mandatory fields
# determine OFX header info
# write header info to output
# read input file
# determine file type
# for text file
    # read transactions and parse them into a dict
    # write the record to output

#-----------------------------------
# read the profile file
#-----------------------------------
def readprofile( filename ):
    profile = configparser.ConfigParser()
    try:
        if os.path.exists(filename):
            logging.debug("profile does exist")
        else:
            raise IOError("unable to read profile file")
    except IOError:
        logging.error("unable to read profile file \"{}\"".format(filename)) 
        logging.error("please specify a valid profile filename")
        exit()
    
    # profile filename exists, try to read it
    logging.debug("reading profile \"%s\"", filename)
    profile.read(filename)

    # separator character is mandatory. ensure one was specified
    try:
        logging.debug("separator \"{}\" will be used".format(profile['DEFAULT']['separator']))
    except KeyError:
        logging.error("\"Separator\" is a mandatory item in profile and it was not found in \"{}\"".format(filename))
        exit()
    return( profile )

#-----------------------------------
# read the data transaction file
#-----------------------------------
def readdatafile( filename ):
    global ofx
    transactionList = []
    transactionInfo = {}

    try:
        if os.path.exists(filename):
            logging.debug("datafile does exist")
        else:
            raise IOError("unable to read datafile")
    except IOError:
        logging.error("unable to read datafile \"%s\"",filename) 
        logging.error("please specify a valid datafile filename")
        exit()

    with open(filename, 'r', errors='ignore') as f:
        try:
            # do stuff
            for line in f:
                line = line.rstrip() # remove all trailing whitespace (including newline)
                logging.debug("read data from datafile: \"%s\"", line)

                # detect if the separator character is present
                if profile['DEFAULT']['separator'] not in line:
                    logging.warning("invalid line of transaction data. \"%s\" separator not found", profile['DEFAULT']['separator'])
                else:
                    # process line in data file
                    # split by separator
                    fields = line.split(profile['DEFAULT']['separator'])
                    transactionDate = fields[int(profile['Position Information']['TransactionDatePosition'])]
                    if (int(profile['Date Information']['inputdateformat']) != int(profile['Date Information']['outputdateformat'])):
                        # need to transform the dates
                        logging.debug("transforming date \"{}\"".format(transactionDate))
                        if (int(profile['Date Information']['inputdateformat']) == 1):
                            # input is type 1 ("euro style")
                            #print("type 1 input ")
                            (day, month, year) = transactionDate.split("/")
                        elif (int(profile['Date Information']['inputdateformat']) == 2):
                            # input is type 2 ("u.s. style")
                            #print("type 2 input ")
                            (month, day, year) = transactionDate.split("/")
                        if (int(profile['Date Information']['outputdateformat']) == 1):
                            transactionDate = "{}/{}/{}".format(day,month,year)
                        elif (int(profile['Date Information']['outputdateformat']) == 2):
                            transactionDate = "{}/{}/{}".format(month,day,year)
            
                    logging.debug("Transaction Date=\"%s\"", transactionDate)
                    transactionInfo['TransactionDate'] = transactionDate
                    transactionInfo['DTPOSTED'] = "{}{}{}000000".format(year,month,day)
                    # check if this is the first transaction
                    if (ofx['DTSTART'] == ""): #TODO: need to convert this to a proper date data structure and ensure the earliest date is used
                        # earliest transaction
                        ofx['DTSTART'] = "{}{}{}000000".format(year,month,day)

                    ofx['DTEND'] = "{}{}{}000000".format(year,month,day)#TODO: need to convert this to a proper date data structure and ensure the latest date is used

                    transactionDescription = str(fields[int(profile['Position Information']['DescriptionPosition'])])
                    logging.debug("Transaction Description=\"%s\"", transactionDescription)
                    transactionInfo['TransactionDescription'] = transactionDescription
                    transactionAmount = str(fields[int(profile['Position Information']['TransactionAmountPosition'])])
                    logging.debug("Transaction Amount=\"%s\"", transactionAmount)
                    transactionInfo['TransactionAmount'] = transactionAmount
                    if (float(transactionAmount) >= 0.0):
                        transactionInfo['TransactionType'] = "CREDIT"
                    else:
                        transactionInfo['TransactionType'] = "DEBIT"

                    transactionList.append(transactionInfo)
                    transactionInfo = {}
        except IOError:
            print ("Could not read file: {}").format(filename)

    return(transactionList)

def parsecommandline():
    parser = argparse.ArgumentParser(description='convert bank transaction data files into proper OFX files')
    parser.add_argument("profile", help="the institution-specific profile to use for parsing the data file")
    parser.add_argument("datafile", help="the data transaction file downloaded from the financial institution")
    args = parser.parse_args()
    logging.debug("user defined profile to be used: %s", args.profile)
    logging.debug("data file to be used: %s", args.datafile)
    return(args)

#-----------------------------------
# take all the data and write to the OFX output
#-----------------------------------
def writeheader():
    global ofx
    global profile
    
    print("OFXHEADER:{}".format(ofx['OFXHEADER']))
    print("DATA:OFXSGML")
    print("VERSION:{}".format(ofx['VERSION']))
    print("SECURITY:{}".format(ofx['SECURITY']))
    print("ENCODING:{}".format(ofx['ENCODING']))
    print("CHARSET:{}".format(ofx['CHARSET']))
    print("COMPRESSION:{}".format(ofx['COMPRESSION']))
    print("OLDILEUID:{}".format(ofx['OLDFILEUID']))
    print("NEWFILEUID:{}".format(ofx['NEWFILEUID']))
    print("\n")
    print("<OFX>")
    print("<SIGNONMSGSRSV1>")
    print("<SONRS>")
    print("<STATUS>")
    print("\t<CODE>0")
    print("\t<SEVERITY>INFO")
    print("</STATUS>")
    print("<DTSERVER>20160723000000") #TODO: hardcoded
    print("<LANGUAGE>{}".format(profile['DEFAULT']['language']))
    print("</SONRS>")
    print("</SIGNONMSGSRSV1>")
    print("<BANKMSGSRSV1>")
    print("<STMTTRNRS>")
    print("<TRNUID>0") #TODO: hardcoded
    print("<STATUS>")
    print("<CODE>0")
    print("<SEVERITY>INFO")
    print("</STATUS>")
    print("<STMTRS>")
    print("<CURDEF>{}".format(profile['DEFAULT']['currency']))
    print("<BANKACCTFROM>")
    print("<BANKID>000000000")#TODO: hardcoded
    print("<ACCTID>111111111")#TODO: hardcoded
    print("<ACCTTYPE>SAVINGS")#TODO: hardcoded
    print("</BANKACCTFROM>")
    print("<BANKTRANLIST>")
    print("<DTSTART>{}".format(ofx['DTSTART']))
    print("<DTEND>20160723000000")#TODO: hardcoded
    return()

def writeoutputfile(transactionList):

    # counter for internal purposes
    i = 1
    
    # iterate through and print the transaction fields into the OFX file
    for transactionInfo in transactionList:
        #print("{}. {}".format(i, transactionInfo['TransactionDescription']))
        i = i + 1
        print("<STMTTRN>")          
        print("\t<TRNTYPE>{}".format(transactionInfo['TransactionType']))
        print("\t<DTPOSTED>{}".format(transactionInfo['DTPOSTED']))
        print("\t<TRNAMT>{}".format(transactionInfo['TransactionAmount']))
        print("\t<FITID>133") #TODO: hardcoded
        print("\t<REFNUM>133") #TODO: hardcoded
        print("\t<NAME>{}".format(transactionInfo['TransactionDescription']))
        print("</STMTTRN>") #TODO: hardcoded

        logging.info("Found {} transactions".format(i))

    # close up all the fields
    print("</BANKTRANLIST>")
    print("</STMTRS>")
    print("</STMTTRNRS>")
    print("</BANKMSGSRSV1>")
    print("</OFX>")
    
    return

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    args = parsecommandline()
    profile = readprofile(args.profile)
    transactionList = readdatafile(args.datafile)
    writeheader()
    writeoutputfile(transactionList)
    exit()
#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3

import configparser
import argparse
import os
import sys
import logging
import datetime

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
    
    if (profile['DEFAULT']['enclosedinquotes']):
        logging.info("Found option: EnclosedInQuotes = {}".format(profile['DEFAULT']['enclosedinquotes']))

    return( profile )

#-----------------------------------
# read the data transaction file
#-----------------------------------
def readdatafile( filename ):
    global ofx
    transactionList = []
    transactionInfo = {}
    earliestTransactionDate = datetime.datetime.max # set to the maximum (i.e. newest possible) date: "9999-12-31"
    latestTransactionDate = datetime.datetime.min # set to the maximum (i.e. newest possible) date: "0000-01-01"

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
                    # process line in data fileq
                    # split by separator
                    fields = line.split(profile['DEFAULT']['separator'])
                    transactionDate = fields[int(profile['Position Information']['TransactionDatePosition'])]
                    # if needed, remove leading and trailing quotations
                    if (bool(profile['DEFAULT']['enclosedinquotes'])):
                        logging.debug("removing quotes from transaction date {}.".format(transactionDate))
                        transactionDate = transactionDate.strip('"') # remove leading and trailing quote marks
                        logging.debug("Transaction date now {}.".format(transactionDate))

                    #if (int(profile['Date Information']['inputdateformat']) != int(profile['Date Information']['outputdateformat'])):
                    #    # need to transform the dates
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
                        t = datetime.datetime(int(year),int(month),int(day))
                        if (earliestTransactionDate == None or earliestTransactionDate > t):
                            logging.debug("Previous DTSTART was {}. Found new earliest transaction {}".format(earliestTransactionDate, t))
                            earliestTransactionDate = t
                        if (latestTransactionDate == None or latestTransactionDate < t):
                            logging.debug("Previous DTEND was {}. Found new earliest transaction {}".format(latestTransactionDate, t))
                            latestTransactionDate = t
                    elif (int(profile['Date Information']['outputdateformat']) == 2):
                        t = datetime.datetime(int(year),int(month),int(day))
                        transactionDate = "{}/{}/{}".format(month,day,year)
                        if (earliestTransactionDate == None or earliestTransactionDate > t):
                            logging.debug("Previous DTSTART was {}. Found new earliest transaction {}".format(earliestTransactionDate, t))
                            earliestTransactionDate = t
                        if (latestTransactionDate == None or latestTransactionDate < t):
                            logging.debug("Previous DTEND was {}. Found new earliest transaction {}".format(latestTransactionDate, t))
                            latestTransactionDate = t
                    logging.debug("Transaction Date=\"%s\"", transactionDate)
                    transactionInfo['TransactionDate'] = transactionDate
                    transactionInfo['DTPOSTED'] = "{}{}{}000000".format(year,month,day)
                    # check if this is the first transaction
                    # if (ofx['DTSTART'] == ""): #TODO: need to convert this to a proper date data structure and ensure the earliest date is used
                    #     # earliest transaction
                    #     ofx['DTSTART'] = "{}{}{}000000".format(year,month,day)

                    # ofx['DTEND'] = "{}{}{}000000".format(year,month,day)#TODO: need to convert this to a proper date data structure and ensure the latest date is used

                    transactionDescription = str(fields[int(profile['Position Information']['DescriptionPosition'])])
                    # if needed, remove leading and trailing quotations
                    if (bool(profile['DEFAULT']['enclosedinquotes'])):
                        logging.debug("removing quotes from description {}.".format(transactionDescription))
                        transactionDescription = transactionDescription.strip('"') # remove leading and trailing quote marks
                        logging.debug("Transaction description now {}.".format(transactionDescription))
                    logging.debug("Transaction Description=\"%s\"", transactionDescription)
                    transactionInfo['TransactionDescription'] = transactionDescription
                    
                    transactionAmount = str(fields[int(profile['Position Information']['TransactionAmountPosition'])])
                     # if needed, remove leading and trailing quotations
                    if (bool(profile['DEFAULT']['enclosedinquotes'])):
                        logging.debug("removing quotes from amount {}.".format(transactionAmount))
                        transactionAmount = transactionAmount.strip('"') # remove leading and trailing quote marks
                        logging.debug("Transaction amount now {}.".format(transactionAmount))
                    logging.debug("Transaction Amount=\"%s\"", transactionAmount)
                    transactionInfo['TransactionAmount'] = transactionAmount
                    if (float(transactionAmount) >= 0.0):
                        transactionInfo['TransactionType'] = "CREDIT"
                    else:
                        transactionInfo['TransactionType'] = "DEBIT"

                    transactionReference = str(fields[int(profile['Position Information']['ReferenceNumberPosition'])])
                    # if needed, remove leading and trailing quotations
                    if (bool(profile['DEFAULT']['enclosedinquotes'])):
                        logging.debug("removing quotes from amount {}.".format(transactionReference))
                        transactionReference = transactionReference.strip('"') # remove leading and trailing quote marks
                        logging.debug("Transaction amount now {}.".format(transactionReference))
                    logging.debug("Transaction Reference=\"%s\"", transactionReference)
                    transactionInfo['TransactionReference'] = transactionReference

                    transactionList.append(transactionInfo)
                    transactionInfo = {}
        except IOError:
            logging.error("Could not read file: {}".format(filename))
        
        formattedDate = earliestTransactionDate.strftime("%Y%m%d%H%M%S")
        ofx['DTSTART'] = formattedDate
        formattedDate = latestTransactionDate.strftime("%Y%m%d%H%M%S")
        ofx['DTEND'] = formattedDate
        logging.debug("Setting DTSTART to earliest transaction value {}".format(ofx['DTSTART']))
        logging.debug("Setting DTEND to latest transaction value {}".format(ofx['DTEND']))


    return(transactionList)

def parsecommandline():
    parser = argparse.ArgumentParser(description='convert bank transaction data files into proper OFX files')
    parser.add_argument("profile", help="the institution-specific profile to use for parsing the data file")
    parser.add_argument("datafile", help="the data transaction file downloaded from the financial institution")
    parser.add_argument("output", help="the filename of the .ofx file to create")
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
    
    out.write("OFXHEADER:{}\n".format(ofx['OFXHEADER']))
    out.write("DATA:OFXSGML\n")
    out.write("VERSION:{}\n".format(ofx['VERSION']))
    out.write("SECURITY:{}\n".format(ofx['SECURITY']))
    out.write("ENCODING:{}\n".format(ofx['ENCODING']))
    out.write("CHARSET:{}\n".format(ofx['CHARSET']))
    out.write("COMPRESSION:{}\n".format(ofx['COMPRESSION']))
    out.write("OLDILEUID:{}\n".format(ofx['OLDFILEUID']))
    out.write("NEWFILEUID:{}\n".format(ofx['NEWFILEUID']))
    out.write("\n")
    out.write("<OFX>\n")
    out.write("\t<SIGNONMSGSRSV1>\n")
    out.write("\t\t<SONRS>\n")
    out.write("\t\t\t<STATUS>\n")
    out.write("\t\t\t\t<CODE>0\n")
    out.write("\t\t\t\t<SEVERITY>INFO\n")
    out.write("\t\t\t</STATUS>\n")
    out.write("\t\t<DTSERVER>{}\n".format(ofx['DTEND'])) # setting to the latest transaction date
    out.write("\t\t<LANGUAGE>{}\n".format(profile['DEFAULT']['language']))
    out.write("\t\t</SONRS>\n")
    out.write("\t</SIGNONMSGSRSV1>\n")
    out.write("\t<BANKMSGSRSV1>\n")
    out.write("\t<STMTTRNRS>\n")
    out.write("\t\t<TRNUID>0\n") #TODO: hardcoded
    out.write("\t\t<STATUS>\n")
    out.write("\t\t\t<CODE>0\n")
    out.write("\t\t\t<SEVERITY>INFO\n")
    out.write("\t\t</STATUS>\n")
    out.write("\t\t\t<STMTRS>\n")
    out.write("\t\t<CURDEF>{}\n".format(profile['Account Information']['currency']))
    out.write("\t\t<BANKACCTFROM>\n")
    out.write("\t\t\t<BANKID>{}\n".format(profile['Account Information']['accountnumber']))
    out.write("\t\t\t<ACCTID>{}\n".format(profile['Account Information']['accountid']))
    out.write("\t\t\t<ACCTTYPE>{}\n".format(profile['Account Information']['accounttype']))
    out.write("\t\t</BANKACCTFROM>\n")
    out.write("\t\t\t\t<BANKTRANLIST>\n")
    out.write("\t\t\t\t\t<DTSTART>{}\n".format(ofx['DTSTART']))
    out.write("\t\t\t\t\t<DTEND>{}\n".format(ofx['DTEND']))
    return()

def writeoutputfile(transactionList):

    # counter for internal purposes
    i = 1
    
    # iterate through and print the transaction fields into the OFX file
    for transactionInfo in transactionList:
        #print("{}. {}".format(i, transactionInfo['TransactionDescription']))
        i = i + 1
        out.write("\t\t\t\t\t<STMTTRN>\n")          
        out.write("\t\t\t\t\t\t<TRNTYPE>{}\n".format(transactionInfo['TransactionType']))
        out.write("\t\t\t\t\t\t<DTPOSTED>{}\n".format(transactionInfo['DTPOSTED']))
        out.write("\t\t\t\t\t\t<TRNAMT>{}\n".format(transactionInfo['TransactionAmount']))
        out.write("\t\t\t\t\t\t<FITID>133\n") #TODO: hardcoded
        out.write("\t\t\t\t\t\t<REFNUM>{}\n".format(transactionInfo['TransactionReference']))
        out.write("\t\t\t\t\t\t<NAME>{}\n".format(transactionInfo['TransactionDescription']))
        out.write("\t\t\t\t\t</STMTTRN>\n") 

        logging.info("Found {} transactions".format(i))

    # close up all the fields
    out.write("\t\t\t\t</BANKTRANLIST>\n")
    out.write("\t\t\t</STMTRS>\n")
    out.write("\t\t</STMTTRNRS>\n")
    out.write("\t</BANKMSGSRSV1>\n")
    out.write("</OFX>\n")
    
    return

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    args = parsecommandline()
    try:
        out = open(args.output, 'w', errors='ignore')
        logging.info("Opening file {} for writing ofx output".format(args.output))
    except IOError:
        logging.error("Could not open {} for writing".format(args.output))
        exit()
    
    profile = readprofile(args.profile)
    transactionList = readdatafile(args.datafile)
    writeheader()
    writeoutputfile(transactionList)
    out.close()

    exit()
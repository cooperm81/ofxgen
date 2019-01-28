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
    transaction = {}
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
                    logging.debug("Transaction Date=\"%s\"", transactionDate)
                    transaction['TransactionDate'] = transactionDate
                    transactionDescription = str(fields[int(profile['Position Information']['DescriptionPosition'])])
                    logging.debug("Transaction Description=\"%s\"", transactionDescription)
                    transaction['TransactionDescription'] = transactionDescription
                    transactionAmount = str(fields[int(profile['Position Information']['TransactionAmountPosition'])])
                    logging.debug("Transaction Amount=\"%s\"", transactionAmount)
                    transaction['TransactionAmount'] = transactionAmount

        except IOError:
            print ("Could not read file: {}").format(filename)

    return()

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
    
    print("OFXHEADER:{}".format(ofx['OFXHEADER']))
    print("DATA:OFXSGML")
    print("VERSION:{}".format(ofx['VERSION']))
    print("SECURITY:{}".format(ofx['SECURITY']))
    print("ENCODING:{}".format(ofx['ENCODING']))
    print("CHARSET:{}".format(ofx['CHARSET']))
    print("COMPRESSION:{}".format(ofx['COMPRESSION']))
    print("OLDILEUID:{}".format(ofx['OLDFILEUID']))
    print("NEWFILEUID:{}".format(ofx['NEWFILEUID']))
    print("all the transaction magical goodness goes here ...")

    return()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    args = parsecommandline()
    profile = readprofile(args.profile)
    readdatafile(args.datafile)
    writeheader()
    #writeoutputfile()
    exit()
# ofxgen profile for banco sabadell text file downloads
# note: section names are case SENSITIVE, but keys are case INSENSITIVE

[DEFAULT]
Separator = |
Language = ESP
# set to true if each field is wrapped in quotation marks (")
# Example: "2018/01/34","transaction name"
EnclosedInQuotes = False

[Account Information]
AccountNumber = 000000000
AccountId = 999999999
AccountType = SAVINGS
Currency = EUR

[Date Information]
# 1 = dd/mm/yyyy ("euro style")
# 2 = mm/dd/yyyy ("u.s. style")
InputDateFormat = 1
# DTPOSTED field uses YYYYMMDDHHMMSS format. The 'OutputDateFormat' field is used when outputting the date in other fields.
OutputDateFormat = 2

[Position Information]
# data = field number. fields are zero based. so the line will look like this:
# field 0|field 1|field 2|field 3
TransactionDatePosition = 0
DescriptionPosition = 1
TransactionAmountPosition = 3

# Reference number that uniquely identifies the transaction. Can be used in addition to or instead of a <CHECKNUM>
# used for <REFNUM>
ReferenceNumberPosition = 5

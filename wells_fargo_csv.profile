# ofxgen profile for wells fargo csv file downloads
# note: section names are case SENSITIVE, but keys are case INSENSITIVE

[DEFAULT]
Separator = ,
Language = USD
# set to true if each field is wrapped in quotation marks (")
# Example: "2018/01/34","transaction name"
EnclosedInQuotes = True

[Account Information]
AccountNumber = 000000000
AccountId = 999999999
AccountType = CHECKING
Currency = USD

[Date Information]
# 1 = dd/mm/yyyy ("euro style")
# 2 = mm/dd/yyyy ("u.s. style")
InputDateFormat = 2
# DTPOSTED field uses YYYYMMDDHHMMSS format. The 'OutputDateFormat' field is used when outputting the date in other fields.
OutputDateFormat = 2

[Position Information]
# data = field number. fields are zero based. so the line will look like this:
# field 0|field 1|field 2|field 3
TransactionDatePosition = 0
DescriptionPosition = 4
TransactionAmountPosition = 1

# Reference number that uniquely identifies the transaction. Can be used in addition to or instead of a <CHECKNUM>
# used for <REFNUM>
ReferenceNumberPosition = 3

# ofxgen profile for banco sabadell text file downloads
# note: section names are case SENSITIVE, but keys are case INSENSITIVE

[DEFAULT]
Separator = |
Currency = EUR
AccountType = SAVINGS
Language = ESP

[Date Information]
# 1 = dd/mm/yyyy ("euro style")
# 2 = mm/dd/yyyy ("u.s. style")
InputDateFormat = 1
OutputDateFormat = 2

[Position Information]
# data = field number. fields are zero based. so the line will look like this:
# field 0|field 1|field 2|field 3
TransactionDatePosition = 0
DescriptionPosition = 1
TransactionAmountPosition = 3


ReadMe.txt for London Weekly Bills of Mortality 1644-1849 data collection
-------------------------------------------------------------------------

Manifest
--------
This data collection comprises this ReadMe file of documentation/metadata, and 7 further files representing historical information on burials and christenings in London transcribed from weekly Bills of Mortality from 1644 to 1849:

WeekDict.txt is a pipe-separated text file containing date and coverage details of weekly Bills of Mortality

counts.txt is a pipe-separated text file containing counts of persons reported buried/buried of plague/christened in each London parish per week, 1644-1849

ParCodeDict.txt is a pipe-separated text file containing details of London parishes specified in counts.txt

cods.txt is a pipe-separated text file containing counts of persons dying per cause of death each week for all London parishes together, 1644-1845

ages.txt is a pipe-separated text file containing counts of persons dying in circa 12 age groups each week for all London parishes together, 1729-1849

bread.txt is a pipe-separated text file containing mandatory weekly assizes (weights) for bread at standard value in London, 1644-1815

inputtingnotes.txt is a pipe-separated text file containing descriptions of numeric discrepancies and observations arising during transcription


About this dataset
------------------
This dataset comprises enumerations relating to London burials (and baptisms) transcribed from 9,950 extant Weekly Bills of Mortality from 1644 to 1849. Each Bill is typically printed on both sides of a single sheet and comprises four main sections containing different types of information for that week, all of which were transcribed:

1. counts - the number of persons buried, dying of plague or christened weekly in each parish from 1644 to 1849.
2. ages - the number of dead persons in all parishes together in each of circa twelve age groups weekly from 1729 to 1849.
3. cods - the number of dead persons in all parishes together ascribed to particular causes of death, ie each 'disease or casualty', weekly from 1644 to 1845.
4. bread - the weight of bread of several types sold at a standard price in London (usually penny value), weekly from 1644 to 1815.

The enumerated data from these four sections comprises in total 975,163 non-zero observations.


Provenance
-----------
These files were created for a Wellcome Trust funded research project named on Mortality, Migration and Medicalisation led by Richard Smith and Romola Davenport, reference 360G-Wellcome-103322_Z_13_Z. They were exported in delimited text format from an Access 2016 relational database created in 2017 by Gill Newton at the Cambridge Group for the History of Population and Social Structure (CAMPOP). The data were input into Excel spreadsheets with cross-checks on totals in 2014-16 by Rosie Goldsmith, guided by Newton. Data from every post-1644 extant Weekly Bill of Mortality for London were abstracted and transcribed from documents archived at the Bodleian Library in Oxford, London Metropolitan Archive, British Library, Wellcome Library, and Cambridge University Library, depending on availability (scattered earlier Weekly Bills exist but do not form a complete series and were not transcribed). The database was compiled from Excel spreadsheets, one spreadsheet per year, containing one worksheet for each of the four sections comprising a Bill, on counts, ages, causes and bread assizes respectively. These Excel files were harmonized into one dataset by Gill Newton in April 2016 - February 2017 by extracting, concatenating and restructuring using Python scripts to generate output, initially into four delimited text files that were imported into an Access database, where notes, checks and totals were split manually from the remaining data into separate database tables and various tidyings and consistency checks were performed using database queries. In a few cases where these checks revealed that inputter notes did not clarify substantial discrepancies or portions of missing data, source documents were consulted and notes amended or added. 


WeekDict.txt description and variables
--------------------------------------
Records/lines in this file give date and coverage details for each weekly Bill of Mortality 1644-1849. Variable names are on the first line. Including these variable names there are 10,634 lines in total. This file can be related to other files in this data collection using the variable weekID which is common to all except ParCodeDict.txt

weekID - Text - unique identifier for lines/records in this file; formed from a given year and week number, eg "1644/1"; same as weekID variable in other files

yeartext - Text - calendar years covered by the annual set to which a given week belongs, in the form yyyy-yyyy where yyyy is a four digit year

year - Integer - four digit Gregorian calendar year of given week

week - Integer - number representing place in annual sequence of given week. The begnning of the sequence, week 1, is usually mid-December. Most years have 52 weeks with occasional 53 week years.

begindate - Text - full week beginning date (dd-mmm-yyyy where dd is a two digit day, mmm is a three character month and yyyy is a four digit year) for a given week, in the Julian calendar to 1751 and Gregorian calendar thereafter; NULL if there is no extant Bill of Mortality for that week

countsmissing - Boolean - TRUE if no counts of burials/baptisms are available for a given week; see also countsproblem variable

codmissing - Boolean - TRUE if no causes of death are available for a given week; see also codproblem variable

breadmissing - Boolean - TRUE if no bread assizes are available for a given week; see also breadproblem variable 

agemissing - Boolean - TRUE if no age breakdowns are available for a given week; see also ageproblem variable

countsproblem - Text - briefly states the nature of the problem in cases where counts are absent or incomplete in a given week; NULL if no problem is known to exist

codproblem - Text - briefly states the nature of the problem in cases where causes of death are absent or incomplete; NULL if no problem is known to exist

breadproblem - Text - briefly states the nature of the problem in cases where bread assizes are absent or incomplete; NULL if no problem is known to exist

ageproblem - Text - briefly states the nature of the problem in cases where age breakdowns are absent or incomplete; NULL if no problem is known to exist


counts.txt description and variables
------------------------------------
Records/lines in this file give the number of persons buried, buried of plague, or baptised (christened), in each parish within the Bills of Mortality, per weekly Bill 1644-1849 for which this information is extant and transcribed. Each line represents a count of baptisms or burials in a given London parish in a given week, for each week with an available Bill containing this information in the period 1644-1849. Variable names are on the first line. Including these variable names there are 552,441 lines in total. This file can be related to other files in this data collection using the variable weekID which is common to all other files except ParCodeDict.txt. This file can also be related to ParCodeDict.txt using the variable parcode which is common to both.

countID - Integer - unique numeric identifier for lines/records in this file

weekID - Text - unique identifier for given week composed of 4 digit year and week number, eg "1644/1"; same as weekID variable in other files

parcode - Text - unique identifier of London parish, abbreviated from its full name; same as parcode variable in ParCodeDict.txt

counttype - Text - whether count is of burials, plague burials or christenings

countn - Integer - number of persons in the given parish in the given week subject to the given type of vital event


ParCodeDict.txt description and variables
-----------------------------------------
Records/lines in this file give the full name and locational group of London parishes included in the Bills of Mortality as specified in counts.txt. Variable names are on the first line. Including these variable names there are 163 lines in total. This file can be related to counts.txt using the variable parcode which is common to both. 

parcode - Text - unique identifier of London parish, as four characters abbreviated from its full name; same as parcode variable in counts.txt

parish - Text - full name of London parish

alias1 - Text - alternative name of London parish as given in some weekly Bill(s), included for disambiguation purposes

alias2 - Text - second alternative name of London parish as given in some weekly Bill(s), included for disambiguation purposes

billsgroupbefore1660 - Text - locational category of London parish as listed in Bills before 1660; NULL if not present before this date. Options are: within/without/outparishes/other

billsgroupafter1660 - Text - locational category of London parish as listed in Bills after 1660. Options are: within/without/outparishes/other


cods.txt description and variables
----------------------------------
Records/lines in this file give the number of persons dying of a specified cause of death in London in a given week, for each week with an available Bill containing this information in the period 1644-1845. Variable names are on the first line. Including these variable names there are 329,667 lines in total. This file can be related to other files in this data collection using the variable weekID which is common to all other files except ParCodeDict.txt.

codID - Integer - unique numeric identifier for lines/records in this file

weekID - Text - unique identifier for given week composed of 4 digit year and week number, eg "1644/1"; same as weekID variable in other files

cod - Text - cause of death descriptor as given in weekly Bill (abbreviated where indicated by "[...]")

codspellcorrex - Text - cause of death descriptor standardised to one spelling (abbreviated where indicated by "[...]")

codn - Integer - number of persons dying of a given cause of death in London in a given week


ages.txt description and variables
----------------------------------
Records/lines in this file give the number of persons dying by age group in London in a given week, for each week with an available Bill containing this information in the period 1729-1849. Variable names are on the first line. Including these variable names there are 79,474 lines in total. This file can be related to other files in this data collection using the variable weekID which is common to all other files except ParCodeDict.txt.

ageID - Integer - unique numeric identifier for lines/records in this file

weekID - Text - unique identifier for given week composed of 4 digit year and week number, eg "1644/1"; same as weekID variable in other files

agegroup - Text - age group category giving age range in years as specified in weekly Bills. Options are: stillborn/under 2/2-5/5-10/10-20/20-30/30-40/40-50/50-60/60-70/70-80/90 upwards/100 upwards. Stillborn is specified from 1832 onwards only.

ageyearmin - Integer - minimum year of age for persons in this age group 

ageyearmax - Integer - maximum year of age for persons in this age group

agen - Integer - number of persons dying in a given age group in London in a given week


bread.txt description and variables
-----------------------------------
Records/lines in this file give the assize of bread values: the mandatory weight of bread sold at a fixed price in London in a given week, for each week with an available Bill containing this information in the period 1644-1815. Variable names are on the first line. Including these variable names there are 21,006 lines in total. This file can be related to other files in this data collection using the variable weekID which is common to all other files except ParCodeDict.txt.

breadID - Integer - unique numeric identifier for lines/records in this file

weekID - Text - unique identifier for given week composed of 4 digit year and week number, eg "1644/1"; same as weekID variable in other files

breadtype - Text - type of loaf category. Options are: white/3 halfpenny white/wheaten/household

lb - Integer - bread weight in whole pounds*

oz - Floating point number - bread weight in ounces and fractions of ounces converted to decimal*

dr - Integer - bread weight in whole drams or pennyweights*

*Note on weights: avoirdupois weights except around the end of 1696 when Troy weights are mentioned; see inputternotes.txt


inputtingnotes.txt description and variables
--------------------------------------------
Records/lines in this file give notes on total discrepancies, missing information and interpretations made during transcription of weekly Bills of Mortality. Variable names are on the first line. Including these variable names there are 3,149 lines in total. This file can be related to other files in this data collection using the variable weekID which is common to all other files except ParCodeDict.txt.

notesID - Integer - unique numeric identifier for lines/records in this file

weekID - Text - unique identifier for given week composed of 4 digit year and week number, eg "1644/1"; same as weekID variable in other files

billsection - Text - which of the four types of information transcribed from each printed Bill that this note refers to. Options are: ages/bread/cod/counts

inputternote - Text - full text of note made by inputter

notetype - Text - categorisation of notes, with multiple categories separated by semi-colons. The six most common categories are: totals discrepancy/no Bill/format change/part missing: damaged/interpretation/reporting period !=this week



Written by Gill Newton, CAMPOP, Dec 2019-Jan 2020.















 

 















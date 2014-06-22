#=================================================
#The Munden Project DCF
# Usage -
# python dcf.py cashflows.csv discountfactors.csv
#
#=================================================

#Neccessary Imports
import sys, getopt
import csv
import datetime
import scipy
import numpy as np
import matplotlib.pyplot as plt
import pylab
import scipy.interpolate
from datetime import datetime
from collections import defaultdict
from datetime import date
from scipy.interpolate import interp1d
from scipy.optimize import fmin


# date difference function
def diff_dates(date1, date2):
    return  abs(date2-date1).days if (date1 < date2) else abs(date1-date2).days

#lists used for cashflow / dcf calculations	
flows = []
resultingFlows = []
allFlows = []
allDCFs = []
discountFactors = []
allCurves =[]
points =[]


#read in the discount factors and get into a list for processing
ratefile = sys.argv[2]
with open(ratefile) as csvfile:
    rreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	#skip header row
    rreader.next()
	#now process each row in the sheet
    for row in rreader:
        #print(len(row))
        for x in range(3, int(row[1])+3):
		   discountFactors.append(row[x])
		   #print(discountFactors)
        #discountFactors.extend(row)
        #print (discountFactors)
        allCurves.append(list(discountFactors))
        #print(allCurves)
        discountFactors[:] = []
   
#print ('allcurves:')   
#print(allCurves)

discountFactors.extend(allCurves[int(sys.argv[3])])
#print(discountFactors)

for z in range(0, len(discountFactors)):
   points.append(z)
		   
#print(points)

# read in the cashflows
infile = sys.argv[1]
with open(infile) as csvfile:
    creader = csv.reader(csvfile, delimiter=',', quotechar='|')
	#skip header row
    creader.next()
	#now process each row in the sheet
    for row in creader:
        #print(row[0]);print(row[1])  
        description = row[0]
        startdate = row[1]
        enddate = row[2]		
        period = row[3]
        revExp = row[4]
		#determine total number of periods between start time and end time
        if period == "Annually":
           p = 1.0
        if period == "Semi-annually":
           p = 0.5
        if period == "Daily":
           p = float(1.0/365)
        if period == "Weekly":
           p = float(1.0/52)
        if period == "Monthly":
           p = float(1.0/12)
        
        print(description)
        print('Period: {0}'.format(period))
        #print(p)   
   
        sdate = datetime.strptime(startdate, "%m/%d/%Y")
        edate = datetime.strptime(enddate, "%m/%d/%Y")
		
        d1 = datetime.date(sdate)
        d2 = datetime.date(edate)
		
        print('Start Date: {0}'.format(sdate))
        print('End Date: {0}'.format(edate))
		
        result1 = diff_dates(d2, d1)
        #print (result1, d1, d2)
		
        if p == 1.0:
           result1 = result1 / 365
        if p == 0.5:
           result1 = result1 / (365 / 2)
        if p == 1.0/12:
           result1 = result1 / (365.0 / 12.0)
        if p == 1.0/52:
           result1 = result1 / (365.0 / 52.0)

        #print(p)	
        #print(result1)

        #print('Input Flows: {0}'.format(flows))
        #see if flows should start before the included flows (ie start date > now) if so add to flows
        # note it is assumed the period is same for all flows 

        tmp = int(result1)
        #print('cashflows to add {0}'.format(tmp))

        if result1 > 0:
           for j in range (0,tmp) :
              flows.append(revExp)

        now = datetime.now()
        #print(now.year)
        #print(now.day)
        #print(now.month)

        d1 = datetime.date(sdate)
        d2 = datetime.date(now)
        result1 = diff_dates(d2, d1)
        #print (result1, d1, d2)

        if p == 1.0:
           result1 = result1 / 365
        if p == 0.5:
           result1 = result1 / (365 / 2)
        if p == 1.0/12:
           result1 = result1 / (365.0 / 12.0)
        if p == 1.0/52:
           result1 = result1 / (365.0 / 52.0)

        #print(p)	
        #print(result1)

        #print('Input Flows: {0}'.format(flows))
        #see if flows should start before the included flows (ie start date > now) if so add to flows
        # assuming period is same for all flows 

        tmp = int(result1)

        if result1 > 0:
           for j in range (0,tmp) :
              resultingFlows.append(0)
   
        resultingFlows.extend(flows)
        #print(resultingFlows)
        print('Output Flows: {0}'.format(resultingFlows))
		
        totalPeriods = len(resultingFlows)
        print('Total Periods: {0}'.format(totalPeriods))
		
        allFlows.append(list(resultingFlows))
        flows[:] = []
		
		
        
		#discount factors by period

           
        x = np.array(points)
        y = np.array(discountFactors)

        # create the interpolating function
        f = interp1d(x, y, kind='cubic', bounds_error=False)
		
        #calculate dcf
		#use f(period) to get the interpolated point needed for r
		# e.g. f(360) to get the point on the curve at x=360 

        i= 1.0
        dcf = 0.0
        df=f(i)
		# use if rates need to be converted to discount factors
		# currently assumption that discountfactor file is in discount factors not rates
        #df = 1/(1+ r/100)
        k=0
        for C in resultingFlows:
           dcf = dcf + (float(C)/(1+df)**i )
           i+=p
           k=k+1
           df=f(i)
		   # line below for rate to discount factor would uncomment to convert
           #df = 1/(1+ r/100)
           #print(i)
           #print(df)
        print('DCF: {0}'.format(dcf))
        print(' ')
        resultingFlows[:] = []
        allDCFs.append(dcf)

		
#print('allflows:')		
#print ('allflows: {0}'.format(allFlows))
print ('DCFs: {0}'.format(allDCFs))
print ('Final DCF : {0}'.format(sum(allDCFs)))

xfit = np.linspace(x[0],x[-1])
#print(xfit)
y_interp=f

#save a png of the discount curve
plt.plot(x,y,'bo')
plt.plot(xfit, f(xfit),'r-')
#plt.plot(xmax, f(xmax),'g*')
plt.legend(['data','fit'], loc='best', numpoints=1)
plt.xlabel('periods')
plt.ylabel('discount rate')
plt.title('Discount Curve')
plt.savefig('discountFactors.png')

#plot the discount curve
pylab.plot(x,y,'bo')
pylab.plot(xfit, f(xfit),'r-')
#pylab.plot(xmax, f(xmax),'g*')
pylab.legend(['data','fit'], loc='best', numpoints=1)
pylab.xlabel('periods')
pylab.ylabel('discount factor')
pylab.show()


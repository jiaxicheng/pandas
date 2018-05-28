#!/usr/bin/env python
"""
There are time when people want to slice data using datetime based Index based on the Business day offsets.
see a request from stackoverflow: 
REF:https://stackoverflow.com/questions/50528475/tricky-slicing-specifications-on-business-day-datetimeindex/50559402#50559402

Pandas's pandas.tseries.offsets library provides many helpful functions to manipulate such datetime
offset. 

Besides BDay() which identify business days as Monday through Friday which does not exclude holidays,
Pandas also provides CustomBusinessDay() to calculate offset based on user-defined list of holidays and
weekmask.

Useful parameters for CustomBusinessDay()
 + weekmask : str, Default 'Mon Tue Wed Thu Fri' is the weekmask of valid business days
 + holidays : list/array of dates to exclude from the set of valid business days
 + calendar : pd.HolidayCalendar or np.busdaycalendar

For example: 
  my_holidays = ['2018-01-01', pd.datetime(2018,5,28), np.datetime64('2018-07-04')]
  my_bday = CustomBusinessDay(holidays=my_holidays)
  
  today = pd.datetime(2018, 5, 24)   # Thursday
  dt = today + 3 * my_bday           # 2018-05-30 (Wednesday) 

You can also use weekmask to further adjust the business day setup. for an example
from Pandas website(https://pandas.pydata.org/pandas-docs/stable/timeseries.html)
in Egpyt:  weekmask_egypt = 'Sun Mon Tue Wed Thu'

This is a good example how far we can do with the Pandas APIs on complex business-day related dataFrames.
"""
import pandas as pd
from pandas.tseries.offsets import BDay 

M=2
N=4

start_date = pd.datetime(2015,4,1)
end_date = pd.datetime(2015,6,30)

# testing dataFrame
df = pd.DataFrame(
    list(range(91))
,   pd.date_range(start_date, end_date)
,   columns=['foo']
).resample('B').last()

# for month starts
marker_dates = pd.date_range(start=start_date, end=end_date, freq='BMS')

# create IntervalIndex
bins = pd.IntervalIndex.from_tuples(
    [ (d + (M-1)*BDay(), d + (N-1)*BDay()) for d in marker_dates ]
,   closed='both'
)

# show the result
df.groupby(pd.cut(df.index, bins)).mean()
#[2015-04-02, 2015-04-06]   3.333333
#[2015-05-04, 2015-05-06]  34.000000
#[2015-06-02, 2015-06-04]  63.000000

# any customize markers
marker_dates = [ df.index[12], df.index[33], df.index[57] ]

# M Bday before, and N Bday after 
bins = pd.IntervalIndex.from_tuples(
    [ (d - M*BDay(), d + N*BDay()) for d in marker_dates ]
,   closed='both'
)

# show result.
df.groupby(pd.cut(df.index, bins)).mean()
#[2015-04-15, 2015-04-23]  18.428571
#[2015-05-14, 2015-05-22]  48.000000
#[2015-06-17, 2015-06-25]  81.428571



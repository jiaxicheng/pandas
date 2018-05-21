## Time Intelligence for BI reports ##

There are many useful Pandas tools to calculate some frequently-used time-intelligent functions:

+ Use pandas.cut to aggregate on different date intervals
+ Manipulate the properties of datetime columns: i.e. df[date_col].dt.month
+ pandas.IntervalIndex is very useful when creating discontinuous date ranges

### Monthly Based ###

MTD for every month of a specific year.
```
import pandas as pd
import numpy as np

start_date = pd.datetime(2017,1,1)
end_date   = pd.datetime(2017,12,31)
this_day   = 21

df = pd.DataFrame({
   "date": pd.date_range(start=start_date, end=end_date, freq='D')
,  "value" : np.random.randn(365)
})

# (1) IntervalIndex available since Pandas 0.20.0
# MTD for each month, in this case this_day=14, to sum the value for the first 14 days of each month
# this supports closed on both ends (very useful for some math calculations)
bins = pd.IntervalIndex.from_tuples(
    [ (d, d.replace(day=this_day)) for d in pd.date_range(start=start_date,end=end_date, freq='MS') ]
,   closed = 'both'
)

# Note: Another option to calculate the day on the righr-end of the bins
# [ (d, d + pd.Timedelta(days=this_day-1)) for d in pd.date_range(start=start_date, end=end_date, freq='MS') ]

df.groupby(pd.cut(df.date, bins)).value.sum()
---
date
[2017-01-01, 2017-01-21]    -1.271171
[2017-02-01, 2017-02-21]   -10.471238
[2017-03-01, 2017-03-21]     2.057019
[2017-04-01, 2017-04-21]     7.520729
[2017-05-01, 2017-05-21]     2.375053
[2017-06-01, 2017-06-21]     3.244255
[2017-07-01, 2017-07-21]     2.432168
[2017-08-01, 2017-08-21]    -1.356200
[2017-09-01, 2017-09-21]     0.222814
[2017-10-01, 2017-10-21]    -0.580323
[2017-11-01, 2017-11-21]    -5.369181
[2017-12-01, 2017-12-21]    -8.001069

# (2) Use the properties of datetime columns:
this_year = 2017
df.query('date.dt.day <= @this_day & date.dt.year == @this_year').groupby(df.date.dt.month).value.sum()
---
date
1     -1.271171
2    -10.471238
3      2.057019
4      7.520729
5      2.375053
6      3.244255
7      2.432168
8     -1.356200
9      0.222814
10    -0.580323
11    -5.369181
12    -8.001069

# MTD in the same month but all previous years:
this_month = pd.datetime.today().month
df.query('date.dt.day <= @this_day & date.dt.month == @this_month').groupby(df.date.dt.year).value.sum()

```
**Note:** with pd.IntervalIndex, you can manually create any date ranges, for example, organize them
into list of tuples, and then create the bins with pd.IntervalIndex.

# Monthly, but the start/end date can be any day in a month.
```
bins = [ d.replace(day=this_day) for d in pd.date_range(start=start_date, end=end_date, freq='MS') ]

df.groupby(pd.cut(df.date, bins)).value.sum()
---
date
(2017-01-19, 2017-02-19]    -5.556378
(2017-02-19, 2017-03-19]    -3.043846
(2017-03-19, 2017-04-19]    10.738102
(2017-04-19, 2017-05-19]     3.328970
(2017-05-19, 2017-06-19]    12.423684
(2017-06-19, 2017-07-19]    -7.918700
(2017-07-19, 2017-08-19]     3.000952
(2017-08-19, 2017-09-19]     2.938815
(2017-09-19, 2017-10-19]    -6.533290
(2017-10-19, 2017-11-19]    -5.692990
(2017-11-19, 2017-12-19]    -4.689270
```

### Yearly and Quarterly Based ###
YTD comparison for the past few years
```
df1 = pd.DataFrame({
    'date': [ pd.datetime(np.random.randint(2010,2018),np.random.randint(1,13),np.random.randint(1,28)) for _ in range(365) ]
,   'value' : np.random.rand(365)
})

today      = pd.datetime.today()
this_month = today.month
this_day   = today.day


df1.query('date.dt.month < @this_month | (date.dt.month == @this_month & date.dt.day <= @this_day)')\
   .groupby(df1.date.dt.year).value.sum()
---
date
2010     8.405733
2011     9.937941
2012     4.915750
2013     8.525910
2014     9.456331
2015    10.331379
2016     6.878524
2017    10.525126
```

QTD (quarter to date) comparison with the previous years:
```
this_quarter = (today.month-1)//3 + 1
df1.query('date.dt.quarter == @this_quarter                                                           \
        & (date.dt.month < @this_month | (date.dt.month == @this_month & date.dt.day <= @this_day))') \
   .groupby(df1.date.dt.year).value.sum()
---
date
2010    4.848781
2011    2.412364
2012    1.745505
2013    4.773391
2014    2.587617
2015    2.722054
2016    1.945808
2017    3.270006

```

### Weekly Based ###

WTD in the past 3 weeks, the target is to compare the weekly-wise result horizontally
```
this_year = today.year  # using 2017 for testing
# Note: datetime.isocalendar() return dayofweek(this_week_day) is 1-based (1-7 Mon-Sun)
#       df.date.dt.dayofweek is 0-based (0-6 Mon-Sun)
(this_week, this_week_day) = today.isocalendar()[1:3]

df.query('date.dt.year == @this_year                          \
        & (@this_week - 3 < date.dt.weekofyear <= @this_week) \
        & date.dt.dayofweek <= this_week_day-1')              \
  .groupby(df.date.dt.weekofyear).value.sum()
---
date
19    1.067985
20    0.733026
21    0.259677
Name: value, dtype: float64
```

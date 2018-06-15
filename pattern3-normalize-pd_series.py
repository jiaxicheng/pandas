#/usr/bin/env python

"""
https://stackoverflow.com/questions/50844368/pandas-create-a-10-min-time-series-from-dataframe-of-events-with-start-and-end
Normalize a field with Python data structures, i.e. a list with arbitray items on each row:

   # if return lists[]
   df.col_name.apply(pd.Series).stack().reset_index(1, drop=True)

   # if return dicts{}
   df.col_name.apply(pd.Series).stack().reset_index(1)

When you have massive data set and need to use apply() on row direction, make sure
use simple data structure in apply(func, axis=1). i.e. return a list will be cheaper
than returning a pd.Series and cheaper than pd.DataFrame.

apply(pd.Series) on column will be better since it only run speficic rows. this is especially
important when number of rows are massive.


Benchmark shows:
Method-1: 31.2 ms ± 670 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
Method-2: 36.5 ms ± 1.97 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

Method-2 needs only one apply() function in row direction but took longer time to execute
than Method-1 which uses 3 apply() funciton, two of them are on the column direction.

For a dataset with massive amount of Rows, we should use a simple method for apply() with 
an argument axis=1. Using pd.Series() is more expensive than using a Python data structure
this will be more evident with the growing of the number of rows.

Using an extra pd.Series() on the column level for Method-1 can by offset by many pd.Series()
call on the row level in the first apply() alll in Method-2.

Conclusion: Make the funciont to calculate on row level as simple as possible when massive
            rows are involved. 

More to consider: cython might be useful when processing apply on row-level

"""
import pandas as pd
from timeit import timeit

str="""ID   EventID  Start                    End
G01  1001     2017-10-16 06:03:37.440  2017-10-16 06:24:24.440
G07  1001     2017-10-16 06:11:04.600  2017-10-16 07:28:43.520
G02  1001     2017-10-16 06:15:36.200  2017-10-16 06:23:36.200
G02  1001     2017-10-16 06:18:36.200  2017-10-16 07:03:36.200
G06  1001     2017-10-16 06:18:21.160  2017-10-16 06:23:36.120
G03  1001     2017-10-16 06:29:20.640  2017-10-16 06:47:20.640
G05  1001     2017-10-16 06:29:41.640  2017-10-16 06:36:26.640
"""

df = pd.read_table(pd.io.common.StringIO(str), sep='\s\s+', parse_dates=['Start', 'End'], engine='python')

# 10min interval
span = '10t'

delta = pd.Timedelta('{} minutes'.format(span[:-1]))

# Method-1: returning a Python Data Structure: dict of dicts
def explode_d_range_1(x, delta, span):
     arr = {}
     (t_lower, t_upper) = (x.Start.ceil(span), x.End.ceil(span))
     for t in pd.date_range(t_lower, t_upper, freq=span):
         t_Duration = t - x.Start if t == t_lower else delta - (t - x.End) if t == t_upper else delta
         arr.update({t:t_Duration})
     return arr

# will need to apply pd.Series on column level (3rd line, 2nd apply())
df1 = df.loc[:,['ID', 'EventID']].join(
        df.apply(explode_d_range_3, args=(delta, span), axis=1) \
          .apply(pd.Series) \
          .stack() \
          .reset_index(1) \
          .rename(columns={'level_1':'Start', 0:'Duration'})
)
print(df1)

# Method-2: Return a pd.Series
def explode_d_range_2(x, delta, span):
     arr = {}
     (t_lower, t_upper) = (x.Start.ceil(span), x.End.ceil(span))
     for t in pd.date_range(t_lower, t_upper, freq=span):
         t_Duration = t - x.Start if t == t_lower else delta - (t - x.End) if t == t_upper else delta
         arr.update({t:t_Duration})
     return pd.Series(arr)

# pd.Series directly applied in the Row level apply() function
df2 = df.loc[:,['ID', 'EventID']].join(
        df.apply(explode_d_range_2, args=(delta, span), axis=1) \
          .stack() \
          .reset_index(1) \
          .rename(columns={'level_1':'Start', 0:'Duration'})
)

print(df2)

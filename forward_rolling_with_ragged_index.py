#!/usr/bin/env python
"""Calculating Rolling Aggregations (Ragged DatetimeIndex)

This is a previous post from stackoverflow(May 4, 2018)[Link](https://stackoverflow.com/questions/50179241/forward-looking-rolling-window-in-pandas-ragged-index). As the monotonically decreasing rolling window is now
under development with the Pandas team [Link](https://github.com/pandas-dev/pandas/issues/19248). The same
approach might not be used in the near future. But it's still meaningful to fully understand the following 
two points:

1. How reindex() can reshape the dataset and help find the data points required in calculations.
2. Rolling window have different design default which depends on how window size is defined. 
   + For a window using an offset (i.e. a timedelta like '1d', '30m'), the default window will closed 
     at 'right'. If you use row-shifting to find forward-like rolling, the calculation will need to 
     set the colsed at 'left'. 
   + For fixed windows, default closed is 'both', thus not an issue.

**Note:** `closed` option had been added since Pandas 0.20.0

Some related posts:
1. [Using reindex() to reshape a dataframe](https://github.com/jiaxicheng/pandas/blob/master/pattern1-reindex.md)
2. [Calculate Forward-like rolling functions](https://github.com/jiaxicheng/stackoverflow/blob/master/pandas/calculate_forward_rolling.py)

See below for proposed Python code:
"""
import pandas as pd
from io import StringIO

str = """dtime          value
2018-04-23 06:45:16.920   -0.11
2018-04-23 06:45:16.919   -0.03
2018-04-23 06:45:16.918   -0.01
2018-04-23 06:45:16.917   -0.02
2018-04-23 06:45:16.916    0.03
2018-04-23 06:45:16.914    0.03
2018-04-23 06:45:16.911    0.03
2018-04-23 06:45:16.910    0.06
2018-04-23 06:45:16.909    0.09
2018-04-23 06:45:16.908    0.08
2018-04-23 06:45:16.907    0.18
2018-04-23 06:45:16.906    0.28
2018-04-23 06:45:16.905    0.28
2018-04-23 06:45:16.904    0.02
2018-04-23 06:45:16.903    0.09
2018-04-23 06:45:16.902    0.09
2018-04-23 06:45:16.901    0.09
2018-04-23 06:45:16.900    0.09
2018-04-23 06:45:16.899   -0.24
2018-04-23 06:45:16.898   -0.22
2018-04-23 06:45:16.894   -0.22
2018-04-23 06:45:16.799   -0.21
2018-04-23 06:45:16.798   -0.19
2018-04-23 06:45:16.797   -0.21
2018-04-23 06:45:15.057   -0.13
2018-04-23 06:45:15.056   -0.16
2018-04-23 06:45:13.382   -0.04
2018-04-23 06:45:13.381   -0.02
2018-04-23 06:45:13.380   -0.05
2018-04-23 06:45:13.379   -0.08
"""

## read the original data tmp[::-1]
df = pd.read_table(StringIO(str), sep="\s\s+", engine="python", index_col=["dtime"], parse_dates=['dtime'])

## reverse the data to its original order
df = df[::-1]   

## setup the offset:
offset = '10ms'

# create a new column with values as index datetime plus the window timedelta
# i.e. 10ms
df['dt_new'] = df.index + pd.Timedelta(offset)

# using df.index and this new column to form the new indexes (remove duplicate and sort the list)
idx = sorted(set([*df.index.tolist(), *df.dt_new.tolist()]))

# reindex the original dataframe and set NULL `value` to zero
# this is now in monotonically incresing order with all needed datetimes
# calculate the rolling (backward) sum with all the new data and save the result to a new dataframe df1
# make sure the rolling window has closed='left', default is 'right' for the backward rolling
df1 = df.reindex(idx).fillna(value={'value':0}).value.rolling(offset, closed='left').sum().to_frame()

# make a LEFT join with the original df and the new df1 using df.dt_new = df1.index
# value_y should be the 'forward' rolling sum()
df2 = df.merge(df1, left_on='dt_new', right_index=True, how='left')

print(df2)
#                         value_x                  dt_new  value_y
#dtime                                                            
#2018-04-23 06:45:13.379    -0.08 2018-04-23 06:45:13.389    -0.19
#2018-04-23 06:45:13.380    -0.05 2018-04-23 06:45:13.390    -0.11
#2018-04-23 06:45:13.381    -0.02 2018-04-23 06:45:13.391    -0.06
#2018-04-23 06:45:13.382    -0.04 2018-04-23 06:45:13.392    -0.04
#2018-04-23 06:45:15.056    -0.16 2018-04-23 06:45:15.066    -0.29
#2018-04-23 06:45:15.057    -0.13 2018-04-23 06:45:15.067    -0.13
#2018-04-23 06:45:16.797    -0.21 2018-04-23 06:45:16.807    -0.61
#2018-04-23 06:45:16.798    -0.19 2018-04-23 06:45:16.808    -0.40
#2018-04-23 06:45:16.799    -0.21 2018-04-23 06:45:16.809    -0.21
#2018-04-23 06:45:16.894    -0.22 2018-04-23 06:45:16.904    -0.32
#2018-04-23 06:45:16.898    -0.22 2018-04-23 06:45:16.908     0.66
#2018-04-23 06:45:16.899    -0.24 2018-04-23 06:45:16.909     0.96
#2018-04-23 06:45:16.900     0.09 2018-04-23 06:45:16.910     1.29
#2018-04-23 06:45:16.901     0.09 2018-04-23 06:45:16.911     1.26
#2018-04-23 06:45:16.902     0.09 2018-04-23 06:45:16.912     1.20
#2018-04-23 06:45:16.903     0.09 2018-04-23 06:45:16.913     1.11
#2018-04-23 06:45:16.904     0.02 2018-04-23 06:45:16.914     1.02
#2018-04-23 06:45:16.905     0.28 2018-04-23 06:45:16.915     1.03
#2018-04-23 06:45:16.906     0.28 2018-04-23 06:45:16.916     0.75
#2018-04-23 06:45:16.907     0.18 2018-04-23 06:45:16.917     0.50
#2018-04-23 06:45:16.908     0.08 2018-04-23 06:45:16.918     0.30
#2018-04-23 06:45:16.909     0.09 2018-04-23 06:45:16.919     0.21
#2018-04-23 06:45:16.910     0.06 2018-04-23 06:45:16.920     0.09
#2018-04-23 06:45:16.911     0.03 2018-04-23 06:45:16.921    -0.08
#2018-04-23 06:45:16.914     0.03 2018-04-23 06:45:16.924    -0.11
#2018-04-23 06:45:16.916     0.03 2018-04-23 06:45:16.926    -0.14
#2018-04-23 06:45:16.917    -0.02 2018-04-23 06:45:16.927    -0.17
#2018-04-23 06:45:16.918    -0.01 2018-04-23 06:45:16.928    -0.15
#2018-04-23 06:45:16.919    -0.03 2018-04-23 06:45:16.929    -0.14
#2018-04-23 06:45:16.920    -0.11 2018-04-23 06:45:16.930    -0.11

# If you are questioning the pd.join() based on datetime fields (i.e. floating number issues)
# you can also use the pd.merge_asof() function which make a left join based on the keys
# with direction='nearest' values (can also be forward, backward etc)
# Note: left key must be in monotonically incresing order. 
df3 = pd.merge_asof(df, df1, left_on='dt_new', right_index=True, direction='nearest')


"""
**Some Notes:**

+ The results might vary based on how you define and select the closed option when the size 
  of the rolling window is an offset. By default closed is set to right. If shifting 'offset' 
  is the method applied(as in this example), the rolling aggregation must be calculated with 
  closed = left. (you might have different design though). When the window size is a fixed 
  number, the deault closed is 'both'.

+ The index (dtime field) should not contain duplicates, if not, idx should be de-duplicated 
  based on two fields (dtime, value) <-- [UPDATE]: this is not enough if `value` also the same
  you will need extra logic to prevent the original rows discarded by accident.

**Potential issues:**

+ The reindex() could potentially double the number of rows at the worst scenario.
+ Join dataframes by using a datetime field, this might not work on every system if the datetimes 
  are saved as floating number. **Note:** this issue can be resolved by using pd.merge_asof() 
  with the option direction='nearest'
"""


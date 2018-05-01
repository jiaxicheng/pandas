"""Pandas's rolling() function works only backwards, you can set the right end (or the center) of the windows, 
but not the left end. If you want to calculate a forward rolling() statistics i.e. the sum(), you will need 
to do some tricks. 

Method-1: 
    Calculate the rolling in the regular backward way and then assign the values to .shift(1-d) where 
    'd' is the window size. the problem for this approach is the last (d-1) rows will have NaN values 
    since the dates required for calculation cross the existing date range boundary. 

    One solution for this is to reindex() the dataframe by extending the existing date_range (as index) to 
    include the extra d-size window using the pd_date_range function and fill the NaNs which best fit the 
    application's logic. Using reindex() has another benefit in solving the potential missing date issues 
    which shift() function can not identify.

Method-2: 
    Reverse the date field and calculate the regular backward rolling and then flip it back. 
    The problems is that rolling only support a window based on number of records, not a datetime delta. 
    you will have to make sure the dates are continue and without gap. 

In the following stackoverflow case, OP wanted to check visiting status (True/False) in the next `d` days' window. 

REF: https://stackoverflow.com/questions/49973183/creating-new-columns-given-if-an-event-happen-in-a-window-of-time-future-or-pas/50107431#50107431

XiCheng Jia Apr 30, 2018 @ New York
Platform: Pandas 0.22.0, Python 3.6.4
"""

import pandas as pd
from io import StringIO

# sample texts
sample_txt="""ID     date           e_1
1      2016-02-01     False
1      2016-02-02     False
1      2016-02-03     True
1      2016-02-04     False
1      2016-02-05     False
1      2016-02-06     False
1      2016-02-07     False
1      2016-02-08     False
1      2016-02-09     False
1      2016-02-10     False
2      2016-02-01     False
2      2016-02-02     True
2      2016-02-03     True
2      2016-02-04     False
"""

# read sample text into Pandas dataframe
mydf = pd.read_table(StringIO(sample_txt), sep='\s+')

# make sure date is in valid Pandas datetime format
mydf['date'] = pd.to_datetime(mydf['date'], format='%Y-%m-%d')

# use date as index to make it easier in date manipulations
mydf.set_index('date', inplace=True)

# Method-1:
def flag_visits_1(grps, d, d_name):
    """Loop through each group and extend the index to 'd' more days from
       df_grp.index.max(). fill the NaN values with *False*
       this is needed to retrieve the forward rolling stats when running shift(1-d)
       reindex() can also fix potential missing date issues which shift() can't cover
    """
    for id, df_grp in grps:
        # create the new index to cover all days required in calculation
        idx = pd.date_range(
              start = df_grp.index.min()
            , end   = df_grp.index.max() + pd.DateOffset(days=d)
            , freq  = 'D'
        )

        # set up the new column 'd_name' for the current group
        mydf.loc[mydf.ID == id, 'e1_'+d_name] = (df_grp.reindex(idx, fill_value=False)
                                                       .e_1.rolling(str(d)+'d', min_periods=0)
                                                       .sum().gt(0)
                                                       .shift(1-d)
        )

# Method-2:
def flag_visits_2(grps, d, d_name):
    """If you know the dates are continue without gap, then you might also reverse the dates, 
        do the regular backward rolling(), and then flip it back. However, you can not do the rolling() 
        by the number of day, only by the number of records. 
    """
    for id, df_grp in grps:
        mydf.loc[mydf.ID == id, 'e1_'+d_name] = (df_grp.sort_index(ascending=False)
                                                       .e_1.rolling(d, min_periods=0)
                                                       .sum().gt(0).sort_index()
        )

# d is the actual number of days used in Series.rolling(), d_name used in the column name
# below applies Method-1, to switch to Method-2, change: flag_visits_1 to flag_visits_2
for d, d_name in [ (2, '1d') , (3, '2d'), (7, '6d'), (30, '1m') ]:
    mydf.groupby('ID').pipe(flag_visits_1, d, d_name)

# remove date from the index
mydf.reset_index(inplace=True)

print(mydf)

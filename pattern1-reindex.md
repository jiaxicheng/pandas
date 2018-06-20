## Pattern-1: Using reindex() to reshape a dataframe

Reshaping a dataframe that requires a fix list of indexes with missing items shown.

**Note:** do *NOT* rely on pivot-like functions (pivot, pivot_table, crosstab, stack, unstack etc)
They are creating list dynamically and the result are highly relied on the existing data in
the dataframe, some indexes will not show no matter how you `pivot/unstack` your data
unless the column is a pre-defined `CategoricalDType`

This is where reindex() really shines:

- if you want level-1 index follow a fixed list ['M', 'F']
```
  mdx1 = pd.MultiIndex.from_product([df.index.levels[0], ['M', 'F']])
  df.reindex(mdx1).fillna(0, downcast='infer')
```
-  If you want all possible level-1 values to be shown in all level-0

```
    mdx1 = pd.MultiIndex.from_product(df.index.levels)
    df.reindex(mdx1).fillna(0, downcast='infer')
```
This can be easily extended to more than 2-level indexes

**rindex()** also work perfectly to find missing dates in a datetime series.
```
drange = pd.date_range(start = '2017-01-01', end = '207-12-31', freq='D')
df.set_index('date_field').reindex(drange)
```
All missing data will have NaN in the output.

**Note:** For pivot-like function to work, you will need to convert the column to
a user-predefined `category` type, for example:
```
    ctype = pd.api.types.CategoricalDType(categories=["M", "F"], ordered=True)
    df['field'] = df['field'].astype(ctype)
```

## Partial Indices realignment 

For a data frame like the following, to expand level-2 index(year) to include all
covered years while keeping level-1 untouched.
```
print(df)
                index  qty
city code year            
hyd  1    2016  0      10 
          2017  4      10 
     2    2016  1      12 
          2018  8      10 
     3    2017  5      12 
     4    2018  9      10 
     6    2018  10     12 
pune 1    2017  6      15 
          2018  11     15 
     2    2016  2      15 
          2017  7      25 
     4    2016  3      25 
          2018  12     25 

# expand indices only on the level-2(year), to create multi-Index:
# pd.unique can be used to remove duplicated level-3 entries
midx = pd.MultiIndex.from_tuples(pd.unique([ (z[0], z[1], k) for z in df.index for k in df.index.levels[2] ]))

# below a little better than the above one
#midx = pd.MultiIndex.from_tuples([ 
#    (*i, j) for i in pd.unique([(z[0], z[1]) for z in df.index]) for j in df.index.levels[2] 
#])

df1 = df.reindex(midx)
```

Some useful information:
+ df.index return a list of tuples on all levels of indices, we can use this
  to rebuild the new indices.
+ use pd.MultiIndex.from_tuples() to create multi-index
+ check Ref-[3] where we can use the same notation to filter out rows. for example we want to
  get rows with city and code in the lst = [ ('hyd', 2), ('pune', 4) ], then we can do the following:
```
    df.loc(0)[[ z for z in df.index if (z[0], z[1]) in lst ]]
```
+ to get all level-1 and level2 combos:
```
  lst = { (z[0], z[1]) for z in df.index }
```


**Limitations:**

+ index could not contain duplicate values, otherwise, a ValueError will be raised!
  This applies also to its sibling function: `asfreq()`
```
ValueError: cannot reindex from a duplicate axis
```

## reindex() on the column level ##

Below is an example adding calculated fields into a pivot_table using reindex() and multiIndex
referencing:

```
import pandas as pd
from io import StringIO

str="""card    auth   trans_month   order_number
Amex     A        2017-11       1234
Visa     A        2017-12       2345
Amex     D        2017-12       3416
MC       A        2017-12       3426
Visa     A        2017-11       3436
Amex     D        2017-12       3446
Visa     A        2017-11       3466
Amex     D        2017-12       3476
Visa     D        2017-11       3486
"""

# read sample data into a dataframe
df = pd.read_table(StringIO(str), sep='\s+')

# create a pivot table
df1 = df.pivot_table(index='card', columns=['trans_month', 'auth'],values='order_number', aggfunc='count')
print(df1)

trans_month 2017-11      2017-12     
auth              A    D       A    D
card                                 
Amex            1.0  NaN     NaN  3.0
MC              NaN  NaN     1.0  NaN
Visa            2.0  1.0     1.0  NaN

# add two more columns to level-1 on columns for each level-0 entry
midx = pd.MultiIndex.from_product([df1.columns.levels[0], [*df1.columns.levels[1], 'total', 'pct']])
print(midx)

MultiIndex(levels=[['2017-11', '2017-12'], ['A', 'D', 'pct', 'total']],
           labels=[[0, 0, 0, 0, 1, 1, 1, 1], [0, 1, 3, 2, 0, 1, 3, 2]])

# reindex on the column level
df1 = df1.reindex(midx, axis=1)
print(df1)

     2017-11                2017-12               
           A    D total pct       A    D total pct
card                                              
Amex     1.0  NaN   NaN NaN     NaN  3.0   NaN NaN
MC       NaN  NaN   NaN NaN     1.0  NaN   NaN NaN
Visa     2.0  1.0   NaN NaN     1.0  NaN   NaN NaN

# adding calculated field-1: 'total'
#df1.loc[:,(slice(None),'total')] = df1.groupby(level=[0], axis=1).sum().values
df1.loc(1)[:,'total'] = df1.groupby(level=0, axis=1).sum().values

# adding calculated field-2: auth-rate(A / total)
df1.loc(1)[:,'pct'] = df1.groupby(level=0, axis=1) \
                         .apply(lambda x: x.loc(1)[:,'A'].values / x.loc(1)[:,'total'].values)\
                         .values

# print the resultset
print(df1)

     2017-11                      2017-12                
           A    D total       pct       A    D total  pct
card                                                     
Amex     1.0  NaN   1.0  1.000000     NaN  3.0   3.0  NaN
MC       NaN  NaN   0.0       NaN     1.0  NaN   1.0  1.0
Visa     2.0  1.0   3.0  0.666667     1.0  NaN   1.0  1.0
```
**Note:** There are issues on multiIndex alignment to assign calculated fields after running groupby(). 
Using `values` attribute to convert dataframe into numpy.ndarray can bypass this issue.

### Improvement: ###

Calculating the common descriptive stats directly on `df1` will have issue when you need
'subtotal', 'mean', 'size', 'std' etc. in the same reports, in such case, you will need a separate 
dataframe to save these intermediate values:

(1) create a new EMPTY dataframe containing all new columns and the same row index with `df1`
```
idx = pd.MultiIndex.from_product([df1.columns.levels[0], ['subtotal', 'avg', 'count', 'pct']], names=df1.columns.names)
df2 = pd.DataFrame(columns=idx, index=df1.index)
print(df2)
trans_month  2017-11                  2017-12                
auth        subtotal  avg count  pct subtotal  avg count  pct
card                                                         
Amex             NaN  NaN   NaN  NaN      NaN  NaN   NaN  NaN
MC               NaN  NaN   NaN  NaN      NaN  NaN   NaN  NaN
Visa             NaN  NaN   NaN  NaN      NaN  NaN   NaN  NaN
```

(2) calculate the descriptive stats from `df1`
```
df2.loc(1)[:,'subtotal'] = df1.groupby(level=0, axis=1).agg('sum').values
df2.loc(1)[:,'avg']      = df1.groupby(level=0, axis=1).agg('mean').values
df2.loc(1)[:,'count']    = df1.groupby(level=0, axis=1).agg('size').values
```

(3) join `df2` with `df1` and assign the result to `df3`: (sort the result on columns)
```
df3 = df1.join(df2).sort_index(1)
```

(4) calculate `pct` which needs values from both original `df1` and calculated `df2`
```
df3.loc(1)[:,'pct'] = df3.groupby(level=0, axis=1)\
                         .apply(lambda x: x.loc(1)[:,'A'].values/x.loc(1)[:,'subtotal'].values) \
                         .values
print(df3)
trans_month 2017-11                                    2017-12                              
auth              A    D  avg count       pct subtotal       A    D  avg count  pct subtotal
card                                                                                        
Amex            1.0  NaN  1.0     2  1.000000      1.0     NaN  3.0  3.0     2  NaN      3.0
MC              NaN  NaN  NaN     2       NaN      0.0     1.0  NaN  1.0     2  1.0      1.0
Visa            2.0  1.0  1.5     2  0.666667      3.0     1.0  NaN  1.0     2  1.0      1.0
```

**Note:** if you need the level-1 columns to be sorted in a specific order, then use reindex, for example:
```
midx = pd.MultiIndex.from_product([df1.columns.levels[0], [*df1.columns.levels[1], 'subtotal', 'pct', 'avg', 'count']])
df3.reindex(midx)
```

Reference: 

1. [Pandas groupby 0 value if does not exist](https://stackoverflow.com/questions/50078524/pandas-groupby-0-value-if-does-not-exist/50080885#50080885)
2. [Calculated Columns in Multiindex](https://stackoverflow.com/questions/50750189/calculated-columns-in-multiindex/50753435#50753435)

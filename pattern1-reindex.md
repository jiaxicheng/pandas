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

** Note:** For pivot-like function to work, you will need to convert the column to
a user-predefined `category` type, for example:
```
    ctype = pd.api.types.CategoricalDType(categories=["M", "F"], ordered=True)
    df['field'] = df['field'].astype(ctype)
```

REF: [https://stackoverflow.com/questions/50078524/pandas-groupby-0-value-if-does-not-exist/50080885#50080885](https://stackoverflow.com/questions/50078524/pandas-groupby-0-value-if-does-not-exist/50080885#50080885)

## Pattern-2: Dataframe reshaping -1 ##

**Note:** This is almost a FAQ in pandas/python topics on stackoverflow

Problem: One or two columns of the user's dataframe contain a data structure or delimited-texts which can be 
split into arrayis. The user wants to normalize such fields and put each array items or dict key/value 
pairs into new rows or new columns.

REF: [A post by piRSquared @ stackoverflow](https://stackoverflow.com/questions/49923145/pandas-records-with-lists-to-separate-rows/49923384#49923384)

The solution from piRSquared can be extended into more use cases:

### Convert Python dictionary into columns ###
[An example from stackoverflow](https://stackoverflow.com/questions/50161070/convert-list-of-dicts-of-dict-into-dataframe)
, see below data frame where column-b contains a Python dictionary, user wanted to convert them into 
columns
```
In [110]: df
Out[110]: 
     a    b                           f
0    1    {'c': 1, 'd': 2, 'e': 3}    4
1    2    {'c': 2, 'd': 3, 'e': 4}    3
2    3    {'c': 3, 'd': 4, 'e': 5}    2
3    4    {'c': 4, 'd': 5, 'e': 6}    1

In [111]: pd.DataFrame([ [A, B['c'], B['d'], B['e'], F ] for A, B, F in df.values ], columns=list('abcde'))
Out[111]: 
   a  b  c  d  e
0  1  1  2  3  4
1  2  2  3  4  3
2  3  3  4  5  2
3  4  4  5  6  1

```

### Convert string of dictionary into columns ###
If the above json code is a string, not a Python data structure
```
In [112]: df
Out[112]: 
   a                         b  f
0  1  {"c": 1, "d": 2, "e": 3}  4
1  2  {"c": 2, "d": 3, "e": 4}  3
2  3  {"c": 3, "d": 4, "e": 5}  2
3  4  {"c": 4, "d": 5, "e": 6}  1

In [113]: import json
In [114]: pd.DataFrame([ [A, B['c'], B['d'], B['e'], F ] for A, b, F in df.values for B in [json.loads(b)] ],
      ...: columns=list('abcde'))
Out[114]: 
   a  b  c  d  e
0  1  1  2  3  4
1  2  2  3  4  3
2  3  3  4  5  2
3  4  4  5  6  1
```

**Note:** 
* need json.loads or otjer json parser or your own parser to convert string into a Python data structure
* the outside bracket in `[ json.loads(b) ]` is to make all dict key/value pairs in one record 'B'
thus they wont sent to the next rows.

### Split text into rows ###
below user wanted to convert `AL;LO` into two separated rows
```
In [115]: df 
Out[115]:
   A    B      C
0  b1a  kxl     Ak
1  b1b  txl     Ak
2  b1c  uxl  Ak;Lo
3  b1d  ixl     Lo

In [116]: pd.DataFrame([[ A, B, c ] for A,B,C in df.values for c in C.split(';')], columns=df.columns)
Out[116]:
     A    B   C
0  b1a  kxl  Ak
1  b1b  txl  Ak
2  b1c  uxl  Ak
3  b1c  uxl  Lo
4  b1d  ixl  Lo
```

### Split text into columns: ###
Simliar to Series.str.split('|', expand=True), users want to split one column text and put them 
into separate columns
```
In [117]: df
Out[117]: 
      col1  col2 col3
0  ABC|EFG     1    a
1  ABC|EFG     1   bb
2  ABC|EFG     2    c

In [118]: pd.DataFrame([ [c1,c2,C2,C3] for C1,C2,C3 in df.values for c1,c2 in [ C1.split('|') ] ],
      ...: columns=['c1','c2','col2','col3'])
Out[118]: 
    c1   c2  col2 col3
0  ABC  EFG     1    a
1  ABC  EFG     1   bb
2  ABC  EFG     2    c

```
**Note:** 

1. the square-bracket arount C1.split('|') is important so that all split values will show
   in the same row, otherwise it's a new row.
2. The last example can be handled by `df[['c1', 'c2']] = df.col1.str.split('|', expand=True)`
   and then drop the original column `col1`. Just a different approach to describe how to use the 
   same pattern to resolve different issues.


### Potential issues of this method ###

This method only applies when row index is simple or no row alignment is involved. 
If you have a complex row indexes and converted some text/Python data structures into new
rows, you will also have to build the index separately. 

One workaround is to reset these indexes onto columns before reshaping, and then set_index() 
after the change.



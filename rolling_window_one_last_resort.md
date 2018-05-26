## More complexed Rolling Windows ##

There are people who are looking for a window which contains forward/backward windows at the same 
time: for example, on day 11, they want to calculate the mean, standard deviation etc. on the range
1-10 and 12-21. Thus if we use a window of size=21 and center=`True`, we will need to 
remove the center point at day=11.

For mean value, this is simple. We can calculate the rolling_sum for all 21 points and then subtract the
value at center point at day-11. The rolling_mean will be this value divided by window_size (20 in this example).
For example:
```
df = pd.DataFrame({ 
        'date': pd.date_range(start='1/1/2017', end='12/31/2017'),
        'value': np.random.rand(365)}
)

df.set_index('date', inplace=True)

win_size=20

df['rolling_sum'] = df.value.rolling(window=win_size+1, center=True).sum()
df['rolling_mean'] = df.apply(lambda x: (x.rolling_sum - x.value)/win_size, axis = 1)
```

However for standard deviation, the similar method does not apply. 

Using the itertuples() method could be one last resort which can be used to calculate more complex situations
including ragged timestamp windows.

```
# window size (offset)
window = pd.Timedelta(days=10)

# initialize two columns
df['rolling_std'] = df['rolling_mean'] = np.nan

# calculate std, mean based on a slice of df containing only required indies, see below idx
for row in df.itertuples():
    idx = (df.index != row.Index) & (df.index - row.Index <= window) & (row.Index - df.index <= window)
    df.loc[row.Index, ["rolling_std", "rolling_mean"]] = df.loc[idx, "value"].agg(['std', 'mean']).values
```

df.itertuples() is much slower than df.apply() and vectorization methods with Pandas like rolling() etc. 
But it provides a way to handle more complex logic and calculations.

Bottom Line: don't iterate rows until you have to.

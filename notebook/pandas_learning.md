---
# Pandas Grouping, Window & Apply — Quick Reference

## Summary
- Aggregation vs transform vs element-wise: `agg`/`apply` can reduce groups; `transform`/window ops return results aligned to the original shape.  
- Time vs sample windows: `resample` bins by calendar time; `rolling` uses fixed-size (or time) moving windows; `expanding` grows the window from the start.

## DataFrame.apply
**Purpose:** General-purpose apply along an axis.  
**Behavior:** Applies a function to each row (`axis=1`) or column (`axis=0`). Can return scalars, Series, or DataFrames. Not shape-preserving by default. Slower for large frames.  
**Use when:** Complex per-row/column computations not covered by built-ins.  
**Example:**
```python
# row-wise: sum of A and B per row
df['A_plus_B'] = df.apply(lambda r: r['A'] + r['B'], axis=1)
```
**Notes:** Avoid for large data if vectorized alternatives exist.

## DataFrame.transform
**Purpose:** Shape-preserving transformations (returns same-length result).  
**Behavior:** Must return scalar-per-input or sequence of same length; index-aligned. Works standalone or after `groupby(...).transform`.  
**Use when:** Need per-row/per-element results or broadcast group-level stats to rows.  
**Example:**
```python
# z-score normalization for columns A,B
df[['A','B']] = df[['A','B']].transform(lambda s: (s - s.mean()) / s.std())

# group-level mean broadcasted to rows
df['symbol_mean_return'] = clean_df.groupby('Symbol')['Return'].transform('mean')
```
**Notes:** Output shape equals input shape.

## DataFrame.groupby
**Purpose:** Split-apply-combine by key(s). Produces a GroupBy object for aggregation, transform, apply, or filter.  
**Key behaviors:**
- `.agg()` reduces groups into single-row summaries.
- `.transform()` returns per-row results (same length).
- `.apply()` runs a function on each group; flexible output shapes.
**Examples:**
```python
# reduce: one row per symbol
agg = clean_df.groupby('Symbol')['Return'].agg(['mean','std'])

# named aggregation
named = clean_df.groupby('Symbol').agg(mean_close=('Close','mean'), tot_vol=('Volume','sum'))

# flexible apply
def top_n(group, n=3):
    return group.sort_values('Return', ascending=False).head(n)
top3 = clean_df.groupby('Symbol').apply(top_n)
```
**Notes:** Use vectorized `.agg` methods for performance.

## DataFrame.resample
**Purpose:** Time-based grouping into frequency bins (requires `DatetimeIndex` or `on=`).  
**Behavior:** Aggregates into time bins (e.g., monthly), returns one row per time bin. Controlled by `label`, `closed`.  
**Use when:** Convert series to coarser time frequency (daily → monthly).  
**Example:**
```python
# monthly mean close per symbol (method: set_index then group)
monthly = clean_df.set_index('Date').groupby('Symbol')['Close'].resample('M').mean().reset_index()
```
**Notes:** Use `on='Date'` or set index to `Date` first.

## DataFrame.rolling
**Purpose:** Fixed-size (or time-based) moving-window calculations.  
**Behavior:** Returns aligned results (same length); first rows are NaN until window fills. Sliding window moves row-by-row.  
**Use when:** Moving averages, rolling std, rolling sums.  
**Example:**
```python
# 20-period moving average of Close
clean_df['ma20'] = clean_df.groupby('Symbol')['Close'].rolling(20).mean().reset_index(level=0, drop=True)
```
**Notes:** Per-group rolling uses `groupby(...).rolling` or group+apply depending on pandas version.

## DataFrame.expanding
**Purpose:** Cumulative (growing) window from the start to current row.  
**Behavior:** Produces one value per row; window increases each step (no reduction).  
**Use when:** Cumulative mean, cumulative sum, running statistics.  
**Example:**
```python
# expanding mean of Return with minimum 2 rows
clean_df['expanding_mean'] = clean_df.groupby('Symbol')['Return'].expanding(2).mean().reset_index(level=0, drop=True)
```

## Key Differences (short)
- Reduce vs preserve shape:
  - Reduce: `groupby().agg()`, `resample().agg()` → fewer rows.
  - Preserve: `transform`, `rolling`, `expanding` → same number of rows as input.
  - `apply`: flexible — can reduce or preserve.
- Indexing:
  - `resample` needs time index or `on=`.
  - `groupby` groups by column keys.
  - `rolling`/`expanding` operate along rows/index.
- Use in groups:
  - Reduction: `df.groupby('Symbol').agg(...)`
  - Broadcast: `df.groupby('Symbol').transform(...)`
  - Per-group windows: `df.groupby('Symbol')['Close'].rolling(...)`
- Performance:
  - Built-in vectorized functions (`mean`, `std`, `sum`) are fastest.
  - Avoid Python-level `apply` for large datasets.

## Common built-in aggregations
- `mean`, `std`, `sum`, `min`, `max`, `count`, `nunique`, `median`  
**Usage examples:**
```python
# list-style
clean_df.groupby('Symbol')['Return'].agg(['mean','std','min','max'])

# dict-style named aggregation
clean_df.groupby('Symbol').agg(mean_return=('Return','mean'), volatility=('Return','std'))

# custom metric (lambda)
import numpy as np
clean_df.groupby('Symbol')['Return'].agg(
    sharpe_like=lambda s: (s.mean() / s.std(ddof=1)) * np.sqrt(252) if s.std(ddof=1) != 0 else np.nan
)
```
**Note:** `std` uses sample std (`ddof=1`) by default in many pandas ops; confirm behavior for your pandas version.

## Quick examples using `clean_df`
```python
# 1) group agg summary
summary = clean_df.groupby('Symbol')['Return'].agg(['mean','std','min','max']).reset_index()

# 2) broadcast group mean
clean_df['symbol_mean'] = clean_df.groupby('Symbol')['Return'].transform('mean')

# 3) monthly close (time resample)
monthly_close = clean_df.set_index('Date').groupby('Symbol')['Close'].resample('M').last().reset_index()

# 4) per-symbol 20-day rolling mean
clean_df['ma20'] = clean_df.groupby('Symbol')['Close'].rolling(20).mean().reset_index(level=0, drop=True)

# 5) expanding mean per symbol
clean_df['expanding_mean'] = clean_df.groupby('Symbol')['Return'].expanding(2).mean().reset_index(level=0, drop=True)
```

## Suggested filename
Save this content as `pandas_learning.md`.

---

## Additional Useful Functions

### merge / join  
Purpose: SQL-style joins between DataFrames. Use `how` to control join type.  
Example:
```python
# left join on Symbol
merged = pd.merge(df1, df2, on='Symbol', how='left')
```

### concat  
Purpose: Concatenate DataFrames along rows or columns. Good for stacking partitions.  
Example:
```python
combined = pd.concat([df_a, df_b], axis=0, ignore_index=True)
```

### pivot_table  
Purpose: Aggregated pivot table with flexible `aggfunc`. Handles duplicates.  
Example:
```python
pivot = clean_df.pivot_table(values='Close', index='Date', columns='Symbol', aggfunc='mean')
```

### melt / pivot  
Purpose: Reshape wide→long (`melt`) and long→wide (`pivot`).  
Example:
```python
long = df.melt(id_vars=['Date','Symbol'], value_vars=['Close','Volume'])
wide = long.pivot(index='Date', columns='Symbol', values='Close')
```

### stack / unstack  
Purpose: Move levels between columns and index (multi-index reshaping).  
Example:
```python
s = df.set_index(['Symbol','Date'])['Close']
wide = s.unstack(level=0)  # symbols as columns
```

### explode  
Purpose: Expand list-like column values into separate rows.  
Example:
```python
df = df.explode('tags')  # one row per tag
```

### drop_duplicates  
Purpose: Remove duplicate rows by subset of columns.  
Example:
```python
df = df.drop_duplicates(subset=['Symbol','Date'], keep='first')
```

### dropna / fillna / interpolate  
Purpose: Handle missing values: drop, fill with value/method, or interpolate.  
Example:
```python
df['Close'] = df['Close'].fillna(method='ffill')
df['Close'] = df['Close'].interpolate()
```

### astype / to_datetime  
Purpose: Convert dtypes; parse strings to datetimes.  
Example:
```python
df['Symbol'] = df['Symbol'].astype('category')
df['Date'] = pd.to_datetime(df['Date'])
```

### set_index / reset_index / reindex  
Purpose: Manage DataFrame index and align to new index.  
Example:
```python
df = df.set_index('Date')
df = df.reset_index()
df = df.reindex(pd.date_range(start, end, freq='D'))
```

### sort_values  
Purpose: Sort rows by one or more columns.  
Example:
```python
df = df.sort_values(['Symbol','Date'])
```

### query  
Purpose: Filter rows using a boolean expression string (clean and readable).  
Example:
```python
subset = df.query("Symbol == 'AAPL' and Return > 0.01")
```

### assign / pipe  
Purpose: `assign` adds columns functionally; `pipe` chains DataFrame transforms.  
Example:
```python
df = df.assign(log_close=lambda d: np.log(d['Close']))
df = df.pipe(cleaning_fn).pipe(feature_fn)
```

### applymap / map  
Purpose: Elementwise function on DataFrame (`applymap`) or Series mapping (`map`).  
Example:
```python
df[['A','B']] = df[['A','B']].applymap(abs)
df['Symbol_upper'] = df['Symbol'].map(str.upper)
```

### shift / diff / pct_change  
Purpose: Lags and differences useful for returns and features.  
Example:
```python
df['prev_close'] = df.groupby('Symbol')['Close'].shift(1)
df['return'] = df['Close'].pct_change()
```

### ewm (exponentially-weighted)  
Purpose: Exponentially-weighted moving statistics (responsive to recent data).  
Example:
```python
df['ewm20'] = df.groupby('Symbol')['Close'].apply(lambda s: s.ewm(span=20).mean())
```

### cumsum / cumprod / cummax / cummin  
Purpose: Cumulative statistics across rows (per group if grouped).  
Example:
```python
df['cum_return'] = df.groupby('Symbol')['Return'].cumsum()
```

### corr / cov / quantile / rank  
Purpose: Statistical helpers for relationships, dispersion and ranking.  
Example:
```python
returns_wide = clean_df.pivot_table(values='Return', index='Date', columns='Symbol')
corr_matrix = returns_wide.corr()
top_quantile = df.groupby('Symbol')['Return'].quantile(0.75)
df['rank'] = df.groupby('Date')['Return'].rank(ascending=False)
```

### value_counts / nunique / size  
Purpose: Counts and cardinality for Series or group sizes.  
Example:
```python
counts = df['Symbol'].value_counts()
unique_symbols = df['Symbol'].nunique()
group_sizes = df.groupby('Symbol').size()
```

### sample / clip  
Purpose: Random sampling and clipping numeric values to bounds.  
Example:
```python
sample = df.sample(frac=0.1, random_state=42)
df['Return_clipped'] = df['Return'].clip(-0.2, 0.2)
```

### I/O helpers (to_parquet / to_csv / read_parquet / read_csv)  
Purpose: Read/write DataFrames to persistent formats.  
Example:
```python
clean_df.to_parquet('modules/asset_research/data/clean_data/cleaned_equity_data.parquet', index=False)
df = pd.read_parquet('path/to/file.parquet')
```

### Performance helpers (`astype('category')`, `memory_usage`)  
Purpose: Reduce memory and profile usage on large datasets.  
Example:
```python
df['Symbol'] = df['Symbol'].astype('category')
df.memory_usage(deep=True)
```

---

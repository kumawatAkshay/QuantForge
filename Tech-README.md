# Technical Notes

## Python Packages Used

### yfinance
- **Purpose:** Download market data such as stock prices, dividends, and financial statements from Yahoo Finance.
- **Example:**
  ```python
  import yfinance as yf

  data = yf.download("AAPL", start="2024-01-01", end="2024-12-31")
  print(data.head())
  ```
- **Explanation:** This is useful for collecting historical price data for analysis, backtesting, or research.

### pandas
- **Purpose:** Process and manipulate tabular data efficiently.
- **Example:**
  ```python
  import pandas as pd

  df = pd.DataFrame({"Date": ["2024-01-02", "2024-01-03"], "Close": [190.5, 191.2]})
  df["Date"] = pd.to_datetime(df["Date"])
  print(df)
  ```
- **Explanation:** Pandas helps with cleaning, filtering, grouping, and transforming data before analysis.

### pyarrow
- **Purpose:** Save data in Parquet format for fast and efficient storage.
- **Example:**
  ```python
  import pandas as pd
  import pyarrow as pa
  import pyarrow.parquet as pq

  df = pd.DataFrame({"symbol": ["AAPL"], "price": [190.5]})
  table = pa.Table.from_pandas(df)
  pq.write_table(table, "data.parquet")
  ```
- **Explanation:** Parquet is a columnar file format that is compact and works well for large datasets.

### tqdm
- **Purpose:** Show progress bars for loops and long-running tasks.
- **Example:**
  ```python
  from tqdm import tqdm

  for i in tqdm(range(100)):
      pass
  ```
- **Explanation:** Tqdm makes it easier to monitor the progress of data collection or processing tasks.

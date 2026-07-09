from pathlib import Path

import pandas as pd
import yfinance as yf
from tqdm import tqdm


class EquityCollector:
    def __init__(self):
        base_dir = Path(__file__).resolve().parents[3]
        config_path = base_dir / "modules" / "asset_research" / "config" / "equity_symbols.csv"
        self.symbols = pd.read_csv(config_path)["symbol"].tolist()

        self.output_dir = base_dir / "modules" / "asset_research" / "data" / "raw_data" / "equity"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect(self):

        all_data = []

        for symbol in tqdm(self.symbols):

            try:

                ticker = yf.Ticker(symbol)

                df = ticker.history(
                    period="max",
                    auto_adjust=False
                )

                if df.empty:
                    continue

                df = df.reset_index()

                df["Symbol"] = symbol

                all_data.append(df)

            except Exception as e:

                print(f"{symbol}: {e}")

        final_df = pd.concat(
            all_data,
            ignore_index=True
        )

        final_df.to_parquet(
            self.output_dir / "equity_daily.parquet",
            index=False
        )

        print(final_df.head())

        print(f"\nRows: {len(final_df):,}")


if __name__ == "__main__":

    EquityCollector().collect()
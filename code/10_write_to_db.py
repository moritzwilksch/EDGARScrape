#%%
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData, Date, Float, Integer


db = create_engine("postgresql://postgres:ThisIsSecretAF@localhost:5432")

TICKER = "AAPL"
# EDGAR_CODE = "0000320193"

ticker_cik_lookup = pd.read_csv(
    "https://www.sec.gov/include/ticker.txt",
    sep="\t",
    header=None,
    names=["ticker", "cik"],
)
EDGAR_CODE = (
    f"{ticker_cik_lookup.query('ticker == @TICKER.lower()')['cik'].values[0]:0>10}"
)
print(f"Using {EDGAR_CODE = }")


#%%
db_cols = ["ticker", "accn", "period_end", "value", "fy", "fp", "form", "filed", "item"]
df_cols = ["ticker", "accn", "end", "val", "fy", "fp", "form", "filed", "item"]

#%%
# Create Table
meta = MetaData(db)
stat_table = Table(
    "stats",
    meta,
    Column("accn", String),
    Column("ticker", String, primary_key=True),
    Column("period_end", Date, primary_key=True),
    Column("value", Float),
    Column("fy", Integer),
    Column("fp", String),
    Column("form", String),
    Column("filed", Date),
    Column("item", String, primary_key=True),
)

stat_table.create(db, checkfirst=True)

#%%
import crawler
import pandas as pd

spider = crawler.Crawler(EDGAR_CODE)
spider.populate_facts()

subset = {
    k: v for k, v in spider.facts["usGaap"].items() if k in crawler.keys_to_extract
}

ITEM = "EarningsPerShareDiluted"

for item in crawler.keys_to_extract:

    try:
        eps = (
            pd.DataFrame(subset[item]["units"]["USD"])[df_cols[1:-1]]
            .assign(item=item)
            .assign(ticker=TICKER)
            .rename({dfcol: dbcol for dfcol, dbcol in zip(df_cols, db_cols)}, axis=1)
        )

        try:
            with db.connect() as connection:
                existing_pks = [
                    x[0]
                    for x in connection.execute(
                        "SELECT DISTINCT ticker, period_end, item FROM stats;"
                    )
                ]
        except:
            existing_pks = []

        eps = eps.query("not accn.isin(@existing_pks)").drop_duplicates(
            ["ticker", "period_end", "item"]
        )

        eps.to_sql("stats", con=db, if_exists="append", index=False)

    except KeyError:
        print(f"[WARN] {item} not found. Skipping it.")


#%%
stmt = stat_table.select()

with db.connect() as conn:
    for x in conn.execute("SELECT * FROM stats;"):
        print(x)

#%%
import seaborn as sns

dfx = pd.read_sql(
    """ 
        SELECT period_end, extract(year from period_end) as year, fp, value as value
        FROM stats
        WHERE ticker = 'AAPL' AND item = 'Revenues'; 
    """,
    db,
)

sns.lineplot(data=dfx, x="period_end", y="value")

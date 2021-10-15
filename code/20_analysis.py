#%%
import pandas as pd
from sqlalchemy import create_engine

db = create_engine("postgresql://postgres:ThisIsSecretAF@localhost:5432")

#%%
query = """ 
    SELECT extract(year from period_end) as year, SUM(value) as value
    FROM stats
    WHERE ticker = 'GME' AND item = 'Revenues'
    GROUP BY year;
 """

df = pd.read_sql(query, db)
df

#%%
import matplotlib.pyplot as plt
import seaborn as sns

sns.lineplot(data=df, x="year", y="value")

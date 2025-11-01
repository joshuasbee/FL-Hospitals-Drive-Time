import pandas as pd
import paths

data = paths.data
kaggle = paths.kaggle
hospitals = paths.hospitals

df = pd.read_csv(f"{data}/{kaggle}")

# Counties to keep
keep = ['ALACHUA', 'ORANGE', 'SEMINOLE', 'OSCEOLA', 'SAINT JOHNS', 'DUVAL', 'HILLSBOROUGH']

# Drop various columns
df = df.drop(['index','ZIP4','VAL_METHOD','TTL_STAFF','ALT_NAME','TELEPHONE','X','Y','OBJECTID','ID'], axis=1)

# Drop hospitals outside of Florida
df_fl = df.query("STATE == 'FL'")
# Drop hospitals with owner not available
df_fl = df_fl.query('OWNER != "NOT AVAILABLE"')
# Drop hospitals by county (to get dataset a little smaller for API calls)
df_fl = df_fl[df_fl["COUNTY"].isin(keep)]

print(df_fl.head)

df_fl.to_csv(f"{data}/{hospitals}", index=False)
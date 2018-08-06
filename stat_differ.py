import requests
import pandas as pd
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pygsheets

start_week = sys.argv[1]
end_week = sys.argv[2]
season = sys.argv[3]
url = 'http://localhost:3000/api/Stats?filter={"where": {"and": [{"week": {"inq": [%s, %s]}}, {"season": %s}]}}' % (
    start_week, end_week, season)
r = requests.get(url)
print("Stats pulled successfully!")
df = pd.DataFrame(r.json())

# get list of list of all duplicate indexes
duplicates = []
for index, row in df.iterrows():
    dups = df.index[df["name"] == row["name"]].tolist()
    if (len(dups) > 1 and all(i <= index for i in dups)):
        duplicates.append(dups)

# get df of difference of all dups
diff_df = pd.DataFrame(columns=list(df.columns.values))
for pair in duplicates:
    pair_diff = pd.concat(
        [df.iloc[pair[0]], df.iloc[pair[1]]], axis=1).transpose()
    diffed_vals = {}
    for column in pair_diff:
        if (column == "name" or column == "position" or column == "team" or column == "season" or column == "week" or column == "id"):
            diffed_vals[column] = pair_diff[column].iloc[0]
        else:
            diffed_vals[column] = pair_diff[column].diff().iloc[1]
    diff_df = diff_df.append(diffed_vals, ignore_index=True)

# delete diffed rows and append diffed df
flat_list = [item for sublist in duplicates for item in sublist]
df = df.drop(flat_list)
df = df.append(diff_df)

gc = pygsheets.authorize(service_file='client_secret.json')
sh = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1wY0_kWmvuoFUnVHxOKpkgd18ELMq5wSlaEWoBLe8Cr4/edit?usp=drive_web&ouid=111606700085319731674')
wks = sh[0]
wks.set_dataframe(df, "A1")
print("Sheet updated successfully!")


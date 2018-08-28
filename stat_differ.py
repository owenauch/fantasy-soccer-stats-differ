import requests
import pandas as pd
import sys
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
    dups = df.index[(df["name"] + df["team"]) == (row["name"] + row["team"])].tolist()
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

# drop all rows with all 0s
df = df[(df.accurateCrosses > 0) | (df.accurateKeeperSweeper > 0) | (df.assists > 0) | (df.chancesCreated > 0) | (df.cleanSheets > 0) | (df.crosses > 0) | (df.effectiveClearances > 0) | (df.goals > 0) | (df.goalsConceded > 0) |
        (df.interceptions > 0) | (df.passes > 0) | (df.penaltyConceded > 0) | (df.penaltyKickGoals > 0) | (df.redCards > 0) | (df.saves > 0) | (df.shots > 0) | (df.shotsOnGoal > 0) | (df.tacklesWon > 0) | (df.yellowCards > 0) | (df.yellowRedCards > 0)]

# modify google sheet
gc = pygsheets.authorize(
    service_file='/Users/owenauch/git/personal_projects/fs_stat_differ/client_secret.json')
if (len(sys.argv) > 4):
    sh = gc.open_by_url(sys.argv[4])
else:
    sh = gc.open_by_url(
        'https://docs.google.com/spreadsheets/d/1nZT3o6FA2_FvG_gJ07O_akQjb1QNDhCKKZvLEwT0-9k/edit#gid=0')
wks = sh[0]
wks.rows = df.shape[0]
wks.set_dataframe(df, "A1")
print("Sheet updated successfully!")

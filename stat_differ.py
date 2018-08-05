import requests
import pandas as pd
import sys

start_week = sys.argv[1]
end_week = sys.argv[2]
url = 'http://localhost:3000/api/Stats?filter={"where": {"week": {"inq": [%s, %s]}}}' % (start_week, end_week)
r = requests.get(url)
df = pd.DataFrame(r.json())

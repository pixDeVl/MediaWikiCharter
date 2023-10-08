import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import datetime
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="Goofy program to chart edits and stuff on MW wikis",
    epilog="Copyright pixlDeV now and til the end of time",
)
parser.add_argument(
    "-S",
    "--site",
    help="URL of the Wiki(in format of https://domain,com/w/api.php, see Special:Version for API Path)",
)
parser.add_argument("-U", "--username", help="Account Username on Target Wiki")
parser.add_argument("-P", "--password", help="Password for Target Account")
parser.add_argument("-F", "--file", help="login.json file path")

args = parser.parse_args()

site_url = args.site or "https://minecraft.wiki/api.php"
S = requests.Session()
siteName = S.get(
    url=site_url, params={"action": "query", "meta": "siteinfo", "format": "json"}
).json()["query"]["general"]["sitename"]


# Get Login Creds from login.json
try:
    with open(args.file or "loin.json", "r") as f:
        auth = json.load(f)
    password = args.password or auth["password"]
    username = args.username or auth["username"]
except FileNotFoundError:
    print("Login File not Found")
    password = args.password
    username = args.username
except KeyError as error:
    print("Insuffient Login Details Provided")


if password is None or username is None:
    print("Insuffient Login Details Provided; Login Aborted")
else:
    # Get login token
    authCall = S.get(
        url=site_url,
        params={"action": "query", "meta": "tokens", "type": "login", "format": "json"},
    )
    # Login
    login = S.post(
        url=site_url,
        data={
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": authCall.json()["query"]["tokens"]["logintoken"],
            "format": "json",
        },
    )
    print("Token: " + authCall.json()["query"]["tokens"]["logintoken"])
    print("Login Status: " + login.json()["login"]["result"])
    if "reason" in login.json()["login"]:
        print(login.json()["login"]["reason"])
    print(
        f"Logged into {siteName} as: "
        + S.get(
            url=site_url,
            params={"action": "query", "meta": "userinfo", "format": "json"},
        ).json()["query"]["userinfo"]["name"]
    )


farBack = 31
interval = 86400
now = int(
    datetime.datetime.combine(
        datetime.datetime.today(), datetime.datetime.min.time()
    ).timestamp()
)
dayago = now - interval


def call(rcstart: int, rcend: int):
    responce = S.get(
        url=site_url,
        params={
            "action": "query",
            "list": "recentchanges",
            "rclimit": "5000",
            "rcstart": rcstart,
            "rcend": rcend,
            "format": "json",
        },
    ).json()
    # print(len(responce['query']['recentchanges']))
    return responce


editcount = []
timesforstamps = []
for x in range(farBack):
    requested = call(now, dayago)
    count = len(requested["query"]["recentchanges"])
    editcount.append(count)
    timesforstamps.append(datetime.datetime.fromtimestamp(dayago))
    now -= interval
    dayago -= interval


def mplotedits(time, count):
    plt.plot(time, count)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()
    # # # Add labels and title
    plt.xlabel("Date")
    plt.ylabel("Edit Count")
    plt.title(f"Graph of Edits per day on {siteName}")

    # # Show the plot
    plt.show()


mplotedits(timesforstamps, editcount)

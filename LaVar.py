from yahoofantasy import Context, League
import streamlit as st
import pandas as pd
import numpy as np
import requests,base64

def refreshAuthorizationToken(refreshToken:str) -> dict:
    """Uses existing refresh token to get the new access token"""

    headers: dict = {
        'Authorization': f"Basic {AUTH_HEADER}",
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    }

    data: dict = {
        "redirect_uri": 'oob',
        "grant_type": 'refresh_token',
        "refresh_token": refreshToken
    }

    req = requests.post("https://api.login.yahoo.com/oauth2/get_token",headers=headers,data=data,timeout=100)

    if req.status_code == 200: 

        dobj: dict = req.json()

        return dobj
    
    print("Something went wrong when getting refresh token...try getting the initial access token again!")

    return None

st.title('Fantasy Basketball Playoff Scoreboard')

# Plug in your ID & SECRET here from yahoo when you create your app. Make sure you have the correct scope set for fantasy API ex: "read" or "read/write"
CLIENT_ID = "dj0yJmk9VEtpWVNNQzd1TVRtJmQ9WVdrOVRUQkpObXRuTjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTcy"
CLIENT_SECRET = "23f4d294641cc580d381c647f8932711f19a50e8"

# Special auth header for yahoo.
AUTH_HEADER = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8"))).decode("utf-8")

auth = {
    "access_token": "8gfVehyeulCD48_aK7qLhygosdbMyEFW1fsuuBq32QN8MoZKi4GbTUYkQBnKKCseyQ8u8T65VS74GEVxR_bzbLyZ8O1HCtZz8IVuqwXDLBsJsQFjF.72heACadoNck5sjDKrNGpY.VwqFAoKJFHWoRdhF8Nz_B4Wrr.LWV3WFQunULvnS6A39UF_eHq60H4s7DoZUypxkUp7lqfy7osuZalM1kQASkKWNFlsNogWmJlO6aDU6Ujoo9ZhggvEsY90heL3GsLWSAqjONHcSA6W_6vT4BzTPeFA0M3Se5u0PV6O5LQz8DUxxFeGmBoJ7k8LAxFk0KfVc901fBftS4_ZmMwZtwJUyAsCEnqmjWDsapbAy5eIaiz9LAKAUi_m8S6P2xAhHwqcG2NfDHmGY8pdD7j3KkWerQStNVB6iWDPzjXSpQI18XgVL35oB34GV4n6pWY0di_WMF8v1rFhCJOrMu8afTYnuO6zmD7_G_hJllZDbIT.tXCYOx1p2_A8.HHb.cyOw6Q3qpVOl1Xy33mQmfwVfTxGfDwtuQ5z.85Ka1GUur4kok0laQ6y4kF2qsc4PUMFdhn.p531QtGQToqDsX_1ILeBfCk1FiCe1zNoqfQqn6vBlkVEiJdSjQHR4Ba0spbMzVWIZiKA7mc9vddxf0su6Ho4HwzKQU8.BO0fk2jr3CYLx3Tu4baYReKUTTXBV9oqps6Wn1QBbVUXGjaIe.uFZMsw3DllMnka5I9O74tob3XUA2u8S.kNcIoV4UYn.6jkwKkSw577dOTce.QfWXkWc.rnRvKPX3Q1JRglK7SFfuiVFOuy8Xvu6kFrdjT3SSAwClgmXUcacbocp3zQP8vHSyV9oojCMr_bdXzZC9KRQKZwAUbsbzzf._1RdDYepaP_83dyczYnSPqEHeiY",
    "refresh_token": "AMooCWXYBYMcjT_AzcfJWIeedRC4~000~nJZ43mNIt2q7pdxBi3U-",
    "expires_in": 3600,
    "token_type": "bearer",
}


# Anytime the context is used, I would wrap it in a try except block in case it needs to get a new token.
try:

    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    #league = League(ctx,'428.l.41620')
    league: list = ctx.get_leagues("nba", 2023)[0]

except Exception:

    # Get refresh token
    auth = refreshAuthorizationToken(auth["refresh_token"])
    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    league: list = ctx.get_leagues("nba", 2023)[0]




# Print the name of the league and whether it was private/public
print(league.name + " -- " + league.league_type)

# Iterate through standings and show every team's win/loss record
for team in league.standings():
    outcomes = team.team_standings.outcome_totals
    print(
        f"  #{team.team_standings.rank}\t{team.name}\t"
        f"({outcomes.wins}-{outcomes.losses}-{outcomes.ties})"
    )

print("~~~~~~~~ WEEK 14 ~~~~~~~~")

df = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
df2 = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
week_14 = league.weeks()[13]
for matchup in week_14.matchups:
    for team1_stat, team2_stat in zip(matchup.team1_stats, matchup.team2_stats):
        df.loc[len(df)] = [matchup.team1.name, team1_stat.display, team1_stat.value]
        df2.loc[len(df2)] = [matchup.team2.name, team2_stat.display, team2_stat.value]

df_combined = pd.concat([df,df2])
df_wide = pd.pivot(df_combined, index='team', columns='cat', values='stat')

st.write(df_wide)

cols = ['FGM/FGA', 'FG%', 'FTM/FTA', 'FT%', '3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK', 'TO']
df_new = df_wide[cols]

st.write(df_new)
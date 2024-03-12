from yahoofantasy import Context, League
import streamlit as st
import pandas as pd
import numpy as np
import requests,base64

st.set_page_config(layout="wide",page_title="LaVar Ball Academy")
st.title(":blue[LaVar Ball Academy]")

tab1, tab2 = st.tabs(["Semifinals", "Individual Weeks"])

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
    league: list = ctx.get_leagues("nba", 2023)[0]

except Exception:

    # Get refresh token
    auth = refreshAuthorizationToken(auth["refresh_token"])
    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    league: list = ctx.get_leagues("nba", 2023)[0]


## separate the table into 6 matchups
## totals column for score

##### WEEK 19 #####

df = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
df2 = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
week_19 = league.weeks()[18]
for matchup in week_19.matchups:
    for team1_stat, team2_stat in zip(matchup.team1_stats, matchup.team2_stats):
        df.loc[len(df)] = [matchup.team1.name, team1_stat.display, team1_stat.value]
        df2.loc[len(df2)] = [matchup.team2.name, team2_stat.display, team2_stat.value]

df_combined = pd.concat([df,df2])
df_wide = pd.pivot(df_combined, index='team', columns='cat', values='stat')
df_wide['Week'] = 19

df_wide[['FGM', 'FGA']] = df_wide['FGM/FGA'].str.split('/', expand=True)
df_wide[['FTM', 'FTA']] = df_wide['FTM/FTA'].str.split('/', expand=True)

cols = ['Week','FGM/FGA','FGM','FGA', 'FG%', 'FTM/FTA','FTM','FTA', 'FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK', 'TO']
df_19 = df_wide[cols]


##### WEEK 20 #####

df = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
df2 = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
week_20 = league.weeks()[19] ###figure out how to pull when it is not yet populated
for matchup in week_20.matchups:
    for team1_stat, team2_stat in zip(matchup.team1_stats, matchup.team2_stats):
        df.loc[len(df)] = [matchup.team1.name, team1_stat.display, team1_stat.value]
        df2.loc[len(df2)] = [matchup.team2.name, team2_stat.display, team2_stat.value]

df_combined = pd.concat([df,df2])

#df_combined['stat']= df_combined['stat'].str[0]
#for col in df_wide[['3PTM','AST','BLK','FG%','FT%','PTS','REB','ST','TO']]:
#    df_wide[col]= df_wide[col].str[0]

df_wide = pd.pivot(df_combined, index='team', columns='cat', values='stat')
df_wide['Week'] = 20

#df_wide.fillna(0, inplace = True)

#if df_wide['FGM/FGA'].empty:
#    df_wide[['FGM/FGA']] == '0/0'

#else:
#    df_wide[['FGM', 'FGA']] = df_wide['FGM/FGA'].str.split('/', expand=True)


#if df_wide[['FTM/FTA']].empty:
#    df_wide[['FTM/FTA']] == '0/0'

#else:
#    df_wide[['FTM', 'FTA']] = df_wide['FTM/FTA'].str.split('/', expand=True)

df_wide[['FGM', 'FGA']] = df_wide['FGM/FGA'].str.split('/', expand=True)
df_wide[['FTM', 'FTA']] = df_wide['FTM/FTA'].str.split('/', expand=True)


cols = ['Week','FGM/FGA','FGM','FGA', 'FG%', 'FTM/FTA','FTM','FTA', 'FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK', 'TO']
df_20 = df_wide[cols]

##### Semis Combined #####

df_combined = pd.concat([df_19,df_20])
df_combined.drop(columns=['FGM/FGA', 'FG%','FTM/FTA','FT%'])

df_matchups = df_combined.groupby(['team'])[["FGM", "FGA","FTM","FTA","3PTM","PTS","REB","AST","ST","BLK","TO"]].apply(lambda x : x.astype(int).sum())
df_matchups['FG%'] = df_matchups['FGM']/df_matchups['FGA']
df_matchups['FT%'] = df_matchups['FTM']/df_matchups['FTA']
df_matchups['FGM/FGA'] = df_matchups['FGM'].astype(str)+"/"+ df_matchups['FGA'].astype(str)
df_matchups['FTM/FTA'] = df_matchups['FTM'].astype(str)+"/"+ df_matchups['FTA'].astype(str)

cols = ['FGM/FGA','FG%','FTM/FTA','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK', 'TO']
df_matchups = df_matchups[cols]

##### Semis Matchups #####

##### set up all matchups
matchup1 = df_matchups[df_matchups.index.isin(['Big Ballers','Young Bloods'])]
matchup2 = df_matchups[df_matchups.index.isin(['Blue Checkmarks','House Markkanen'])]
matchup3 = df_matchups[df_matchups.index.isin(['Oliver James First of His Name',"Dray's Iron Fist"])]
matchup4 = df_matchups[df_matchups.index.isin(['Stepback to Freedom',"Shawn's Team"])]
matchup5 = df_matchups[df_matchups.index.isin(['Arizona Capybaras','Jamal Crossover'])]
matchup6 = df_matchups[df_matchups.index.isin(['There Goes My Herro','Dwight for MVP'])]


##### matchup 1
max_val = matchup1.drop(columns=['TO']).select_dtypes(np.number).max(axis=0)
count_max = matchup1.eq(max_val, axis=1).sum(axis=1).reset_index(name ='Total')

min_val = matchup1[['TO']].min(axis=0)
count_min = matchup1.eq(min_val, axis=1).sum(axis=1).reset_index(name ='Total')

total_1 = pd.concat([count_max,count_min])
total_1 = total_1.groupby(['team'])[["Total"]].apply(lambda x : x.astype(int).sum())

matchup1_final = matchup1.merge(total_1, left_on='team', right_on='team')

##### matchup 2
max_val = matchup2.drop(columns=['TO']).select_dtypes(np.number).max(axis=0)
count_max = matchup2.eq(max_val, axis=1).sum(axis=1).reset_index(name ='Total')

min_val = matchup2[['TO']].min(axis=0)
count_min = matchup2.eq(min_val, axis=1).sum(axis=1).reset_index(name ='Total')

total_2 = pd.concat([count_max,count_min])
total_2 = total_2.groupby(['team'])[["Total"]].apply(lambda x : x.astype(int).sum())

matchup2_final = matchup2.merge(total_2, left_on='team', right_on='team')

##### matchup 3
max_val = matchup3.drop(columns=['TO']).select_dtypes(np.number).max(axis=0)
count_max = matchup3.eq(max_val, axis=1).sum(axis=1).reset_index(name ='Total')

min_val = matchup3[['TO']].min(axis=0)
count_min = matchup3.eq(min_val, axis=1).sum(axis=1).reset_index(name ='Total')

total_3 = pd.concat([count_max,count_min])
total_3 = total_3.groupby(['team'])[["Total"]].apply(lambda x : x.astype(int).sum())

matchup3_final = matchup3.merge(total_3, left_on='team', right_on='team')

##### matchup 4
max_val = matchup4.drop(columns=['TO']).select_dtypes(np.number).max(axis=0)
count_max = matchup4.eq(max_val, axis=1).sum(axis=1).reset_index(name ='Total')

min_val = matchup4[['TO']].min(axis=0)
count_min = matchup4.eq(min_val, axis=1).sum(axis=1).reset_index(name ='Total')

total_4 = pd.concat([count_max,count_min])
total_4 = total_4.groupby(['team'])[["Total"]].apply(lambda x : x.astype(int).sum())

matchup4_final = matchup4.merge(total_4, left_on='team', right_on='team')

##### matchup 5
max_val = matchup5.drop(columns=['TO']).select_dtypes(np.number).max(axis=0)
count_max = matchup5.eq(max_val, axis=1).sum(axis=1).reset_index(name ='Total')

min_val = matchup5[['TO']].min(axis=0)
count_min = matchup5.eq(min_val, axis=1).sum(axis=1).reset_index(name ='Total')

total_5 = pd.concat([count_max,count_min])
total_5 = total_5.groupby(['team'])[["Total"]].apply(lambda x : x.astype(int).sum())

matchup5_final = matchup5.merge(total_5, left_on='team', right_on='team')

##### matchup 6
max_val = matchup6.drop(columns=['TO']).select_dtypes(np.number).max(axis=0)
count_max = matchup6.eq(max_val, axis=1).sum(axis=1).reset_index(name ='Total')

min_val = matchup6[['TO']].min(axis=0)
count_min = matchup6.eq(min_val, axis=1).sum(axis=1).reset_index(name ='Total')

total_6 = pd.concat([count_max,count_min])
total_6 = total_6.groupby(['team'])[["Total"]].apply(lambda x : x.astype(int).sum())

matchup6_final = matchup6.merge(total_6, left_on='team', right_on='team')

#################### PRINTING TO SITE #####################

with tab1:
    st.header("~~~~~~~~ Championship Bracket ~~~~~~~~")
    st.write(matchup1_final.style.highlight_max(subset = ['Total','FG%','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK'], color = 'lightgreen', axis = 0)
         .highlight_min(subset = ['TO',], color = 'lightgreen', axis = 0))
    st.write(matchup2_final.style.highlight_max(subset = ['Total','FG%','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK'], color = 'lightgreen', axis = 0)
         .highlight_min(subset = ['TO',], color = 'lightgreen', axis = 0))
    st.write(matchup3_final.style.highlight_max(subset = ['Total','FG%','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK'], color = 'lightgreen', axis = 0)
         .highlight_min(subset = ['TO',], color = 'lightgreen', axis = 0))
    st.header("~~~~~~~~ Consoloation Bracket ~~~~~~~~")
    st.write(matchup4_final.style.highlight_max(subset = ['Total','FG%','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK'], color = 'lightgreen', axis = 0)
         .highlight_min(subset = ['TO',], color = 'lightgreen', axis = 0))

    st.write(matchup5_final.style.highlight_max(subset = ['Total','FG%','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK'], color = 'lightgreen', axis = 0)
         .highlight_min(subset = ['TO',], color = 'lightgreen', axis = 0))

    st.write(matchup6_final.style.highlight_max(subset = ['Total','FG%','FT%','3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK'], color = 'lightgreen', axis = 0)
         .highlight_min(subset = ['TO',], color = 'lightgreen', axis = 0))

with tab2:
    st.header("~~~~~~~~ Week 20 (Week 2 of Semis) ~~~~~~~~")
    st.write(df_20)
    st.header("~~~~~~~~ Week 19 (Week 1 of Semis) ~~~~~~~~")
    st.write(df_19)

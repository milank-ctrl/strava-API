import datetime
import time 
import requests
import json
import pandas as pd
import os 


#kiszedem a validációs kódot
#https://www.strava.com/oauth/authorize?client_id=36054&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all

#authentikáció

json_path = "/Users/milankocza/Desktop/python/strava/keys.json"

try:
    with open(json_path, "r") as f:
        auth_keys = json.load(f)

    PARAMS = {"client_id" : auth_keys["client_id"], "client_secret" : auth_keys["client_secret"], "refresh_token" : auth_keys["refresh_token"], "grant_type" : "refresh_token"}   
    auth_url = "https://www.strava.com/oauth/token"

    auth_resp = requests.post(url = auth_url, params = PARAMS)
    request_data = auth_resp.json()
    print(request_data)

    access_token = request_data["access_token"]
    refress_token = request_data["refresh_token"]
    auth_keys["refress_token"] = refress_token

    print(access_token)

    #kimásolom a refresh tokent és lementem a következő futáshoz
    with open(json_path, 'w') as f:
        f.write(json.dumps(auth_keys))   

    activity_id = "5954886243"

    activity_url = "https://www.strava.com/api/v3/activities/" + activity_id
    activity_param = {"access_token" : access_token, "include_all_efforts" : False}

    activity_res = requests.get(url = activity_url, params = activity_param)
    print(activity_res)

    activity = activity_res.json()
    start_date = activity["start_date_local"].replace('Z', '')
    st = datetime.datetime.fromisoformat(start_date)

    start_latlng = activity["start_latlng"]
    end_latlng = activity["end_latlng"]

    stream_url = "https://www.strava.com/api/v3/activities/" + activity_id + "/streams"
    stream_param = {"keys" : "distance,time,latlng", "key_by_type" : True, "access_token" : access_token}
    

    stream_res = requests.get(url = stream_url, params = stream_param)
    print(stream_res)

    stream = stream_res.json()
    latlng = stream["latlng"]["data"]
    times = stream["time"]["data"]

    data = {"latlng" : latlng, "time" : times}
    df = pd.DataFrame(data)

    #split lat long data into 2 columns
    df[["latitude", "longitude"]] = pd.DataFrame(df.latlng.tolist())

    df["start_date"] = start_date
    df["start_date_unix"] = st.timestamp()
    df["start_latlng"] = str(start_latlng)
    df["end_latlng"] = str(end_latlng)
    
    def add_time(row):
        return row["start_date_unix"] + row["time"]

    df["actual_time"] = df.apply(add_time, axis = 1)
    df = df.drop("latlng", axis = 1)
    print(df)
    df.to_csv("test.csv")

 
except:
    print("An error happened!")



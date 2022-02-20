import requests
import json
from time import sleep
import os
try:
    from hidden import token
except:
    token = ""

s = requests.session()
cwd = os.getcwd()
delayed = False

headersDict = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Authorization": token
}

def getFriends(logs):
    friendsList = s.get("https://discordapp.com/api/v6/users/@me/relationships", headers = headersDict).json()

    finalFriendsList = friendsList[:]
    if logs != []:
        for f in friendsList:
            username = f["user"]["username"]
            if f"{username}.txt" in logs:
                finalFriendsList.remove(f)

    return finalFriendsList

def checkLogs():
    if os.path.isdir(f"{cwd}/logs") != True:
        os.mkdir(f"{cwd}/logs")
        return []
    
    logs = next(os.walk(f"{cwd}/logs"), (None, None, []))[2]
    return logs

def getMessages(friend):
    global delayed
    username = friend["user"]["username"]
    print(username)

    #Get Channel ID
    response = s.post("https://discordapp.com/api/v6/users/@me/channels", headers=headersDict, data=json.dumps({"recipient_id": friend["id"]})).json()
    dmChannelId = response["id"]
    payload = {"limit": "100"}

    #Check If Channel Has Any Messages
    response = s.get(f"https://discordapp.com/api/v6/channels/{dmChannelId}/messages", headers = headersDict, params=payload).json()
    try:
        id = response[-1]["id"]
    except:
        print("No Messages")
        return
    
    payload["before"] = id
    print(f"{username} : {id}")

    outfile = open(f"{username}.txt", 'w')
    outfile.write(str(friend) + "\n\n")

    for message in response:
        outfile.write(json.dumps(message) + "\n")

    while len(response) == 100 or delayed == True:
        response = s.get(f"https://discordapp.com/api/v6/channels/{dmChannelId}/messages", headers = headersDict, params=payload)

        if response.status_code == 429:
            delay = int(response.json()["retry_after"]) / 1000
            sleep(delay)

            delayed = True
            response = response.json()
            continue

        response = response.json()
        for message in response:
            outfile.write(json.dumps(message) + "\n")

        delayed = False
        if len(response) != 0:
            id = response[-1]["id"]
            payload["before"] = id
            print(f"{username} : {id}")

    outfile.close()
    os.rename(f"{cwd}/{username}.txt", f"{cwd}/logs/{username}.txt")

logs = checkLogs()
friendsList = getFriends(logs)

for friend in friendsList:
    getMessages(friend)

print("Done")

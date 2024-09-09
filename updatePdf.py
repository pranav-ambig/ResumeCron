import requests
import json
import os
import sys
import shutil
from win10toast_click import ToastNotifier

# Constants
LEETCODE_API_URL = 'https://alfa-leetcode-api.onrender.com/' 
USERNAME = sys.argv[1]
COMPILATION_NAME = 'Resume' if len(sys.argv) < 3 else sys.argv[2]
DESTINATION_PATH = '' if len(sys.argv) < 4 else sys.argv[3]
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

os.chdir(SCRIPT_PATH)

ProfileStats = {}

def readProfileStats():
    global ProfileStats
    with open('./ProfileStats.json') as f:
        ProfileStats = json.load(f)

def getRatingDetails():
    url = LEETCODE_API_URL + "/userContestRankingInfo/" + USERNAME
    response = requests.get(url)
    rating = round(response.json()['data']['userContestRanking']['rating'])
    topPercentage = response.json()['data']['userContestRanking']['topPercentage']
    return rating, topPercentage

def getProblemCount():
    url = LEETCODE_API_URL + USERNAME + '/solved'
    response = requests.get(url)
    solved = response.json()['solvedProblem']
    return solved

def updateProfileStats():
    # previous ProfileStats
    prevRating = ProfileStats['rating']
    prevTopPercentage = ProfileStats['topPercentage']
    prevSolved = ProfileStats['solved']

    currentRating, currentTopPercentage = getRatingDetails()
    currentSolved = getProblemCount()

    currentRating = max(prevRating, currentRating)
    currentTopPercentage = max(prevTopPercentage, currentTopPercentage)

    if (currentRating == prevRating 
        and currentTopPercentage == prevTopPercentage 
        and currentSolved == prevSolved):
        print('No Updates')
        return False

    print("Detected Updates")
    ProfileStats['rating'] = currentRating
    ProfileStats['topPercentage'] = currentTopPercentage
    ProfileStats['solved'] = currentSolved

    return True

def writeProfileStats():
    print('Updated JSON', ProfileStats)
    with open('./ProfileStats.json', 'w') as f:
        json.dump(ProfileStats, f)
    
def updateTex():
    rating = str(ProfileStats['rating'])
    topPercentage = str(ProfileStats['topPercentage'])
    solved = str(ProfileStats['solved'])

    replacements = {
        "{{LCRating}}": rating,
        "{{LCTopPercentage}}": topPercentage,
        "{{LCProblemCount}}": solved,
    }

    with open("./Resume.tex", "r") as file:
        resumeTex = file.read()

    for placeholder, value in replacements.items():
        resumeTex = resumeTex.replace(placeholder, value)
    
    with open('./' + COMPILATION_NAME + ".tex", "w") as file:
        file.write(resumeTex)


def compileAndMovePdf():
    os.system("lualatex "+ COMPILATION_NAME + ".tex")
    print("Updated Resume PDF")

    if DESTINATION_PATH:
        if os.path.exists(DESTINATION_PATH + COMPILATION_NAME + ".pdf"):
            os.remove(DESTINATION_PATH + COMPILATION_NAME + ".pdf")
        
        shutil.copy2(COMPILATION_NAME + ".pdf", DESTINATION_PATH)
    print("Done!")

def notify():
    toaster = ToastNotifier()
    toaster.show_toast(
        "Resume Updater",
        "Successfully updated Resume!", 
        duration=5,
        threaded=True,
        callback_on_click=lambda: os.startfile(DESTINATION_PATH+COMPILATION_NAME+".pdf")
    )

def main():
    readProfileStats()
    if updateProfileStats():
        updateTex()
        compileAndMovePdf()
        writeProfileStats()
        notify()
    sys.exit(0)

if __name__ == '__main__':
    main()

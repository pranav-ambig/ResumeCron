import requests
import json
import os
import sys
import shutil
from win10toast_click import ToastNotifier
import subprocess
import logging

# Constants
LEETCODE_API_URL = 'https://alfa-leetcode-api.onrender.com/' 
USERNAME = sys.argv[1]
COMPILATION_NAME = 'Resume' if len(sys.argv) < 3 else sys.argv[2]
DESTINATION_PATH = '' if len(sys.argv) < 4 else sys.argv[3]
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


# Setup
os.chdir(SCRIPT_PATH)
ProfileStats = {}

# Logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Functions
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
    currentTopPercentage = min(prevTopPercentage, currentTopPercentage)

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

    shutil.copy2("./Resume.tex", "./" + COMPILATION_NAME + ".tex")

    with open("./" + COMPILATION_NAME + ".tex", "r") as file:
        resumeTex = file.read()

    for placeholder, value in replacements.items():
        resumeTex = resumeTex.replace(placeholder, value)
    
    with open('./' + COMPILATION_NAME + ".tex", "w") as file:
        file.write(resumeTex)


def compileAndMovePdf():
    subprocess.run(
        ["lualatex", COMPILATION_NAME + ".tex"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        shell=True
    )
    print("Updated Resume PDF")

    if DESTINATION_PATH:
        if os.path.exists(DESTINATION_PATH + COMPILATION_NAME + ".pdf"):
            os.remove(DESTINATION_PATH + COMPILATION_NAME + ".pdf")
        
        shutil.copy2(COMPILATION_NAME + ".pdf", DESTINATION_PATH)
    print("Done!")

def notify(error=False):
    toaster = ToastNotifier()

    if error:
        toaster.show_toast(
            "Resume Updater",
            "Error in updating Resume...", 
            duration=5,
            threaded=True
        )
        return
    toaster.show_toast(
        "Resume Updater",
        "Successfully updated Resume!", 
        duration=5,
        threaded=True,
        callback_on_click=lambda: os.startfile(DESTINATION_PATH+COMPILATION_NAME+".pdf")
    )

def main():
    try:
        readProfileStats()
        if updateProfileStats():
            updateTex()
            compileAndMovePdf()
            writeProfileStats()
            notify()
            logging.info(f"Successfully updated Resume! {ProfileStats}", )
        else:
            logging.info("No Updates")
    except Exception as e:
        notify(error=True)
        logging.error(e)


if __name__ == '__main__':
    main()
    sys.exit(0)

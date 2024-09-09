# ResumeCron

## Description
This is a simple cron job that automatically updates your coding stats in your resume PDF.

## How to use
1. Clone this repository
2. Download your .tex and .cls files of your resume and place it in the same directory as updatePdf.py. Download the fonts folder too if you are using custom fonts.
4. Add placeholders in your .tex file where you want your stats to be updated. Supported ones are:
`{{LCRating}}`, `{{LCTopPercentage}}` and `{{LCProblemCount}}`.
3. Make sure to install a suitable LaTeX compiler. This project used MiKTeX on Windows. First run of the script might require a lot of LaTeX packages to be installed. Make sure to install them.
4. Install the required Python packages using `pip install -r requirements.txt`
4. Run the script using `python updatePdf.py username comp_name dest_path`
    - `username` is your LeetCode Username.
    - `comp_name` (Optional) is the name of the compiled PDF. Default is `Resume.pdf`.
    - `dest_path` (Optional) is the path to the directory where the compiled PDF will be saved. A copy of the PDF will always be saved in the same directory as the script.
5. Optionally set up a cron job using Task Scheduler on Windows or crontab on Linux to run the script at regular intervals.

# Azure AD Password Checker

In an Azure AD environment, it's possible to determine whether a user has Multi-Factor Authentication (MFA) disabled without requiring any special privileges. This can be accomplished by analyzing the account's creation date and last password change date. 

If an account's creation date and time match its last password change date and time, it may indicate that no human interaction has occurred since the account was created, and the user has not been able to enable Multi-Factor Authentication (MFA) or change their password. And there are other 'anomalies' such as the password change date being older than the creation date. This suggests also that Multi-Factor Authentication (MFA) couldn't be enabled because the User wasn't created yet!


This information can be useful for identifying potential security risks designed for use by both red and blue teams.

The roadrecon database file is needed for this tool. 
Roadrecon tool is developed by dirkjanm and can be download on github https://github.com/dirkjanm/ROADtools or ```pip install roadrecon```.

How to use see:
```
python3 azurepwchecker.py
py azurepwchecker.py
usage: azurepwchecker.py [-h] [--roadrecon-dump] [--roadrecon-dump-mfa] [-d DB] [-m] [-l] [-ll] [-lll] [-la] [-lo]

Azure AD Password Checker - This is a parser for the roadrecon database file designed for use by both red and blue teams. While the roadrecon tool can
provide live data for analysis, it is not required for using this parser! roadrecon is developed by https://github.com/dirkjanm credits to him!

options:
  -h, --help            show this help message and exit
  -d DB, --db DB        Specify the path to the 'roadrecon.db' database file, default is this location
  -m, --mfa-list        User Accounts without MFA (No privileged user required)! This argument helps identify user accounts that have not enabled
                        Multi-Factor Authentication (MFA). If an account's creation date and time match its last password change date and time, it may
                        indicate that no human interaction has occurred since the account was created, and the user has not been able to enable MFA or
                        change their password. And there are other 'anomalies' such as the password change date being older than the creation date.
                        This suggests also that Multi-Factor Authentication (MFA) couldn't be enabled because the User wasn't created yet! :-]
  -l, --pw-month        User accounts that had their passwords changed last month
  -ll, --pw-year        User accounts that had their passwords changed last year
  -lll, --pw-older      User accounts that haven't changed their passwords in a long time, oldest first
  -la, --admin          User accounts that are members of 'Admin' named groups, including 'Global Reader'
  -lo, --out-of-hours   User password change that occurred outside of office hours, specifically between 5:00 PM (17:00) and 8:00 AM (08:00) on
                        weekdays, as well as on Saturdays and Sundays

run roadrecon first:
  (Run the following command to install the tool "pip install roadrecon)"

  --roadrecon-dump      "roadrecon dump" command or do it with roadrecon
  --roadrecon-dump-mfa  "roadrecon dump --mfa" command (requires privileged access) or do it with roadrecon
  ```
See intro:

https://user-images.githubusercontent.com/49560894/233073626-d1ccc173-c3cf-4751-878b-e8f0c65e6c0a.mp4


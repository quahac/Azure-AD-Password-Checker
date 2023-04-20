import argparse
import os
import subprocess
import sqlite3
import sys
from datetime import datetime

parser = argparse.ArgumentParser(description='Azure AD Password Checker - This is a parser for the roadrecon database file designed for use by both red and blue teams. While the roadrecon tool can provide live data for analysis, it is not required for using this parser! roadrecon is developed by https://github.com/dirkjanm credits to him!')

group_tool = parser.add_argument_group('run roadrecon first', '(Run the following command to install the tool "pip install roadrecon)"')
group_tool.add_argument('--roadrecon-dump', action='store_true', default=False,
                    help='"roadrecon dump" command or do it with roadrecon')
group_tool.add_argument('--roadrecon-dump-mfa', action='store_true', default=False,
                    help='"roadrecon dump --mfa" command (requires privileged access) or do it with roadrecon')                   
parser.add_argument('-d','--db', type=str, default='roadrecon.db',
                    help="Specify the path to the 'roadrecon.db' database file, default is this location")
parser.add_argument('-m','--mfa-list',action='store_true', default=False,
                    help="User Accounts without MFA (No privileged user required)! This argument helps identify user accounts that have not enabled Multi-Factor Authentication (MFA). If an account's creation date and time match its last password change date and time, it may indicate that no human interaction has occurred since the account was created, and the user has not been able to enable MFA or change their password. And there are other 'anomalies' such as the password change date being older than the creation date. This suggests also that Multi-Factor Authentication (MFA) couldn't be enabled because the User wasn't created yet! :-]")   
parser.add_argument('-l','--pw-month', action='store_true', default=False,
                    help='User accounts that had their passwords changed last month')
parser.add_argument('-ll','--pw-year', action='store_true', default=False,
                    help="User accounts that had their passwords changed last year")
parser.add_argument('-lll','--pw-older', action='store_true', default=False,
                    help="User accounts that haven't changed their passwords in a long time, oldest first")
parser.add_argument('-la','--admin', action='store_true', default=False,
                    help="User accounts that are members of 'Admin' named groups, including 'Global Reader'")
parser.add_argument('-lo','--out-of-hours', action='store_true', default=False,
                    help="User password change that occurred outside of office hours, specifically between 5:00 PM (17:00) and 8:00 AM (08:00) on weekdays, as well as on Saturdays and Sundays")    

args = parser.parse_args()

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

if not os.path.isfile(args.db):
    print(f"Error: Database file '{args.db}' not found.")
    exit()

if args.roadrecon_dump:
    subprocess.run(["roadrecon", "dump"])

if args.roadrecon_dump_mfa:
    subprocess.run(["roadrecon", "dump", "--mfa"])

db_path = os.path.join(os.getcwd(), args.db)

class line:
    end = '\033[0m'
    underline = '\033[4m'

red     = "\033[0;31m"
green   = "\033[0;32m"
yellow  = "\033[0;33m"
white   = "\033[0;37m"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

if args.mfa_list:
    cur.execute(f"SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime), strftime('%Y-%m-%d %H:%M', createdDateTime), strftime('%s', lastPasswordChangeDateTime) - strftime('%s', createdDateTime) as timeDifference, objectId FROM users WHERE accountEnabled = 1 AND timeDifference < 600 ORDER BY lastPasswordChangeDateTime ASC")
    rows = cur.fetchall()
    print("")
    print("Multi-Factor Authentication (MFA) is not enabled on these Users! (prediction)")
    print("There are anomalies, such as the password change date being older than the creation date. \nThis suggests that MFA couldn't be enabled because the User wasn't created yet! :-)")
    print(yellow+"Yellow color is difference time in seconds Created vs Last Password Change datetime"+white)
    print("------------------------------------------------------------------------------------------")
    print(line.underline +"Password Changed"+ line.end+" "*3+ line.underline +"User Created"+line.end+" "*7+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        created = row[2] if row[2] is not None else ""
        timediff = row[3] if row[3] is not None else ""
        print(f"{pw_last_change}   {created}   {mail} {yellow}({timediff} sec){white}")
    print("")
     
if args.pw_month:
    cur.execute(f"SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime), accountEnabled FROM users WHERE strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) >= date('now', '-31 days') AND accountEnabled = 1 ORDER BY lastPasswordChangeDateTime DESC")
    rows = cur.fetchall()
    info = False
    print("")
    print("Last Password Change Within 31 Days")
    print("-----------------------------------")
    print(line.underline +"Password Changed"+line.end+" "*3+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        if int(pw_last_change[10:13]) < 8 or int(pw_last_change[10:13]) > 17:
            print(f"{yellow}{pw_last_change}   {white}{mail}")
            info = True
        else:
            print(f"{pw_last_change}   {mail}")
    if info:
        print(f"{yellow}Yellow color = password changed time after working hours!{white}")
    print("")

if args.pw_year:
    cur.execute(f"SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime), accountEnabled FROM users WHERE strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) >= date('now', '-365 days') AND accountEnabled = 1 ORDER BY lastPasswordChangeDateTime DESC")
    rows = cur.fetchall()
    info = False
    print("")
    print("Last Password Change Within 365 Days")
    print("------------------------------------")
    print(line.underline +"Password Changed"+line.end+" "*3+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        if int(pw_last_change[10:13]) < 8 or int(pw_last_change[10:13]) > 17:
            print(f"{yellow}{pw_last_change}   {white}{mail}")
            info = True
        else:
            print(f"{pw_last_change}   {mail}")
    if info:
        print(f"{yellow}Yellow color = password changed time after working hours!{white}")
    print("")

if args.pw_older:
    cur.execute(f"SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime), accountEnabled FROM users WHERE strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) AND accountEnabled = 1 ORDER BY lastPasswordChangeDateTime ASC")
    rows = cur.fetchall()
    info = False
    print("")
    print("Oldest Password Change > 1 year")
    print("-----------------------------------------")
    print(line.underline +"Password Changed"+line.end+" "*3+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        if int(pw_last_change[10:13]) < 8 or int(pw_last_change[10:13]) > 17:
            print(f"{yellow}{pw_last_change}   {white}{mail}")
            info = True
        else:
            print(f"{pw_last_change}   {mail}")
    if info:
        print(f"{yellow}Yellow color = password changed time after working hours!{white}")
    print("")
    
if args.admin:
    cur.execute(f"SELECT Users.userPrincipalName, DirectoryRoles.displayName, strftime('%Y-%m-%d %H:%M', Users.lastPasswordChangeDateTime), strftime('%Y-%m-%d %H:%M', Users.createdDateTime) FROM DirectoryRoles CROSS JOIN lnk_role_member_user on DirectoryRoles.objectId = lnk_role_member_user.DirectoryRole  CROSS JOIN Users on Users.objectId = lnk_role_member_user.User WHERE DirectoryRoles.displayName LIKE '%Admin%' OR  DirectoryRoles.displayName LIKE '%Global Reader%' AND Users.accountEnabled = 1 ORDER BY Users.lastPasswordChangeDateTime ASC ")
    rows = cur.fetchall()
    info = False
    print("")
    print("List of several Administrators")
    print("------------------------------")
    print(line.underline+"Password Changed"+line.end+" "*3+line.underline+"User Created"+line.end+" "*7+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        role = row[1] if row[1] is not None else ""
        pw_last_change = row[2] if row[2] is not None else ""
        created = row[3] if row[3] is not None else ""  
        if pw_last_change == created:
            print(f"{red}{pw_last_change}   {created}   {mail} {yellow}({role}){white}")
            info = True
        else:
            print(f"{pw_last_change}   {created}   {mail} {yellow}({role}){white}")
    print(f"{yellow}Yellow color = Group where the User is a member!{white}")
    if info:
        print(f"{red}Red color = MFA is not enabled! (prediction){white}")
    print("")

if args.out_of_hours:
    #cur.execute(f"SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) FROM Users WHERE (strftime('%w', lastPasswordChangeDateTime) IN ('0', '6')) OR ((strftime('%H:%M', lastPasswordChangeDateTime) >= '17:00') OR (strftime('%H:%M', lastPasswordChangeDateTime) < '08:00')) AND accountEnabled = 1 ORDER BY lastPasswordChangeDateTime DESC") # if you want to handle with sqlite :-)
    cur.execute(f"SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) FROM Users WHERE accountEnabled = 1 ORDER BY lastPasswordChangeDateTime DESC")
    rows = cur.fetchall()
    print("")
    print("Out of hours Password Changes (between 17h-08h + Sat + Sun) ")
    print("------------------------------------------------------------")
    print(line.underline+"Password Changed"+line.end+" "*3+line.underline+"Changed Day"+line.end+" "*7+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        pw_last_change_convert = datetime.strptime(row[1], '%Y-%m-%d %H:%M')
        dayofweek = pw_last_change_convert.strftime("%A")
        if int(pw_last_change[10:13]) < 8 or int(pw_last_change[10:13]) > 17:       
            if dayofweek == "Saturday" or dayofweek == "Sunday":
                print(f"{pw_last_change}{yellow}   {dayofweek}{white}\t{' '*5}{mail}")
            else:
                print(f"{yellow}{pw_last_change}{white}   {dayofweek}\t{' '*5}{mail}")
        if int(pw_last_change[10:13]) > 8 or int(pw_last_change[10:13]) < 17:
                if dayofweek == "Saturday" or dayofweek == "Sunday":
                    print(f"{pw_last_change}{yellow}   {dayofweek}{white}\t{' '*5}{mail}")       
    print(f"{yellow}Yellow color = password changed time or day of the week out of hours{white}")
    print("")

cur.close()
conn.close()

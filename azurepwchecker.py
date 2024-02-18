import argparse
import os
import subprocess
import sqlite3
import sys
import json
from collections import Counter
from datetime import datetime

script_version = '1.0.1'

parser = argparse.ArgumentParser(description='''Azure AD Password Checker - This is a parser for generated JSON file or the roadrecon database file designed for use by both red and blue teams. 
Database can be created when using --code-javascript option to extract 'merged_users.json' file with be created to later input this file with --json-input argument.
And roadrecon generated roadrecon.db file can be used! roadrecon is developed by https://github.com/dirkjanm credits to him!''')

group_tool = parser.add_argument_group('run roadrecon first', '(Run the following command to install the tool "pip install roadrecon)"')
group_tool.add_argument('--roadrecon-dump', action='store_true', default=False,
                    help='"roadrecon dump" command or do it with roadrecon')
group_tool.add_argument('--roadrecon-dump-mfa', action='store_true', default=False,
                    help='"roadrecon dump --mfa" command (requires privileged access) or do it with roadrecon')                   
parser.add_argument('-d','--db', type=str, default='roadrecon.db',
                    help="Specify the path to the 'roadrecon.db' database file, default is this location")
parser.add_argument('-m','--mfa-list',action='store_true', default=False,
                    help="User Accounts without MFA (No privileged user required)! This argument helps identify user accounts that have not enabled Multi-Factor Authentication (MFA). If an account's creation date and time match its last password change date and time, it may indicate that no human interaction has occurred since the account was created, and the user has not been able to enable MFA or change their password. And there are other 'anomalies' such as the password change date being older than the creation date. This suggests also that Multi-Factor Authentication (MFA) couldn't be enabled because the User wasn't created yet! :-]")   
parser.add_argument('-mo','--outfile', type=str,  default=False,
                    help='Output users with MFA anomalies to file')
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
parser.add_argument('-ji','--json-input', type=str,  default=False,
                    help="Provide the JSON file imported from your web browser's console using JavaScript. For 'createdDateTime' and 'lastPasswordChange' details, ensure you download the JSON output using the '--code-javascript' option. users_temp.db file will be added to the current folder") 
parser.add_argument('-c', '--code-javascript', action='store_true', default=False,
                    help="""Perform extraction even if 'azurepwchecker.py' or 'roadrecon' is unavailable. This script enables extraction through the JavaScript console of a web browser. To proceed, ensure you have a valid account to log in at https://portal.azure.com/#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers or an active session on a computer. Copy and paste the provided JavaScript code into the browser's console. Once the session is validated and you have the necessary permissions, a JSON file named 'merged_users.json' will be generated. You can then import it using the following command as example:
                        'azurepwchecker.py --json-input merged_users.json -m'""")
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {script_version}')

class line:
    end = '\033[0m'
    underline = '\033[4m'

red     = "\033[0;91m"
green   = "\033[1;32m"
yellow  = "\033[0;33m"
cyan_l  = "\033[1;36m"  
cyan    = "\033[0;36m"
white   = "\033[0;37m"
   

args = parser.parse_args()

if args.roadrecon_dump:
    subprocess.run(["roadrecon", "dump"])

if args.roadrecon_dump_mfa:
    subprocess.run(["roadrecon", "dump", "--mfa"])

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

def process_json_and_create_db(data, temp_file):
    def flatten_json(y):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    if a == 'id':
                        out[name[:-1] + 'objectId'] = x[a]
                    elif a == 'accountEnabled':
                        out[name + a] = 1 if x[a] else 0    
                    else:
                        flatten(x[a], name + a + '_')
            else:
                out[name[:-1]] = x
        flatten(y)
        return out
    
    def insert_record(cursor, flat_data):
        keys = ', '.join(flat_data.keys())
        values = ', '.join(['?']*len(flat_data))
        values_list = [str(value) for value in flat_data.values()]
        insert_query = f"INSERT INTO users ({keys}) VALUES ({values})"
        cursor.execute(insert_query, values_list)

    def create_column_if_not_exists(cursor, column_name):
        cursor.execute(f"PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if column_name not in column_names:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} TEXT")


    
    conn = sqlite3.connect(temp_file)
    cursor = conn.cursor()

    if data:
        for record in data:
            flat_data = flatten_json(record)
            column_definitions = ', '.join(f"{key} TEXT" for key in flat_data.keys())
            create_table_query = f"CREATE TABLE IF NOT EXISTS users ({column_definitions})"
            cursor.execute(create_table_query)

            for key in flat_data.keys():
                create_column_if_not_exists(cursor, key)

            insert_record(cursor, flat_data)

        conn.commit()
      #  print("Data inserted successfully.")
    else:
        print("The JSON data is empty.")

    cursor.close()
    conn.close()

def remove_temp():
    current_directory = os.getcwd()    
    remove_temp_file = os.path.join(current_directory, "users_temp.db")
    os.remove(remove_temp_file)

# Check if JavaScript code is not selected
if not args.code_javascript:
    if not os.path.isfile(args.db) and not args.json_input:
        print(f"Error: Database file '{args.db}' not found.")
        exit()

def print_json_file():
    try:
      remove_temp()
    except:
      pass
    
    js_path = os.path.join(os.getcwd(), args.json_input)
    with open(js_path, 'r') as json_file:  
        user_data = json.load(json_file)
    
    current_directory = os.getcwd()    
    file_name = "users_temp.db"
    db_path = os.path.join(current_directory, file_name)
    process_json_and_create_db(user_data, db_path)  

if args.json_input:
    print_json_file()
    current_directory = os.getcwd()    
    file_name = "users_temp.db"
    db_path = os.path.join(current_directory, file_name)
else:
    db_path = os.path.join(os.getcwd(), args.db)

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()
    cur_all = conn.cursor()

def print_mfa_anomalies():
    try:
        cur.execute("""
            SELECT 
                userPrincipalName, 
                strftime('%Y-%m-%d %H:%M:%S', lastPasswordChangeDateTime), 
                strftime('%Y-%m-%d %H:%M:%S', createdDateTime), 
                strftime('%s', lastPasswordChangeDateTime) - strftime('%s', createdDateTime) as timeDifference, 
                objectId,
                mobilePhone, 
                businessPhones
            FROM 
                users 
            WHERE 
                accountEnabled = 1 
            ORDER BY 
                timeDifference ASC
        """)
        rows = cur.fetchall()
    except Exception as e:
        cur.execute("""
            SELECT 
                userPrincipalName, 
                strftime('%Y-%m-%d %H:%M:%S', lastPasswordChangeDateTime), 
                strftime('%Y-%m-%d %H:%M:%S', createdDateTime), 
                strftime('%s', lastPasswordChangeDateTime) - strftime('%s', createdDateTime) as timeDifference, 
                objectId,
                mobile, 
                telephoneNumber,
                shadowMobile,
                shadowOtherMobile    
            FROM 
                users 
            WHERE 
                accountEnabled = 1 
            ORDER BY 
                timeDifference ASC
        """)
        rows = cur.fetchall()
   
    cur_all.execute("""
    SELECT 
        userPrincipalName, 
        strftime('%Y-%m-%d %H:%M:%S', lastPasswordChangeDateTime), 
        strftime('%Y-%m-%d %H:%M:%S', createdDateTime), 
        strftime('%s', lastPasswordChangeDateTime) - strftime('%s', createdDateTime) as timeDifference, 
        objectId 
    FROM 
        users
    """)
    rows_all = cur_all.fetchall()
    
    print("\n# Multi-Factor Authentication (MFA) is not enabled on these Users! (prediction)")
    print("# There are anomalies, such as the password change date being older than the creation date.")
    print("# This suggests that MFA couldn't be enabled because the User wasn't created yet! :-)")
    print("# "+yellow+"Yellow color is difference time in seconds Created vs Last Password Change datetime"+white)
    print("#"+cyan+" The blue color is another MFA anomaly: What is the likelihood of two users changing their"+white)
    print("#"+cyan+" passwords at the exact same time. This function verifies if the lastPasswordChangeDateTime"+white)
    print("#"+cyan+" matches with another user's, and how many times (x times)"+white)
    print("#" + cyan_l + " Light blue indicates that the user has a phone number. If not, it's more likely that" + white)
    print("#" + cyan_l + " the admin has not added Phone/SMS to the conditional access settings,"+ white)
    print("#" + cyan_l + " increasing the risk of MFA anomalies. format: (phone numbers: x)\n" + white)
    print(line.underline +"Password Changed"+ line.end+" "*6+ line.underline +"User Created"+line.end+" "*10+line.underline+"UserPrincipalName"+ line.end)
 
    password_change_dates = []
    for row in rows_all:
            password_change_dates.append(row[1].translate(str.maketrans('', '', ' TZ:-')))   

    date_counts = Counter(password_change_dates)
    usersToFile = []    
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        created = row[2] if row[2] is not None else ""
        timediff = row[3] if row[3] is not None else ""
        phone_numbers = [str(num) for num in row[5:] if num not in [None, 'None', [], '[]']]               
        if phone_numbers:
            phones = f"(phone: {', '.join(phone_numbers)})"
        else:
            phones = ""
        pw_last_change_RAW = pw_last_change.translate(str.maketrans('', '', ' TZ:-'))
        doublePW = ''
        doublePWint = 0
        for date, count in date_counts.items():
            if count > 1 and date in pw_last_change_RAW:
                doublePW = f"({count}x)"   
                doublePWint = count
        if timediff < 600 or doublePWint > 1:
            print(f"{pw_last_change}   {created}   {mail} {yellow}({timediff} sec){cyan}{doublePW}{white}{cyan_l}{phones}{white}")
            usersToFile.append(mail)
    print("")
    if args.outfile:
        with open(args.outfile, 'w') as file:  
            for email in usersToFile:
                file.write(email + "\n")
        print(f'{white}#{green} MFA anomaly email list saved: {args.outfile}{white}\n')        
    conn.close()
 
def print_password_change_info(days):
    cur.execute(f"""
        SELECT 
            userPrincipalName, 
            strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime), 
            accountEnabled 
        FROM 
            users 
        WHERE 
            strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) >= date('now', '-{days} days') 
            AND accountEnabled = 1 
        ORDER BY 
            lastPasswordChangeDateTime DESC
    """)
    rows = cur.fetchall()
    if days < 366:
        print(f"\n# Last Password Change Within {days} Days")
    if days > 365:
        print("# Oldest Password Change > 1 year")
    print(f"# {yellow}Yellow color {white}= password changed time after working hours!\n")
    print(line.underline +"Password Changed"+line.end+" "*3+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        if int(pw_last_change[10:13]) < 8 or int(pw_last_change[10:13]) > 17:
            print(f"{yellow}{pw_last_change}   {white}{mail}")
        else:
            print(f"{pw_last_change}   {mail}")
    print("")
    conn.close()

def print_admin_users():
    cur.execute("""
        SELECT 
            Users.userPrincipalName, 
            DirectoryRoles.displayName, 
            strftime('%Y-%m-%d %H:%M', Users.lastPasswordChangeDateTime), 
            strftime('%Y-%m-%d %H:%M', Users.createdDateTime) 
        FROM 
            DirectoryRoles 
        CROSS JOIN 
            lnk_role_member_user 
        ON 
            DirectoryRoles.objectId = lnk_role_member_user.DirectoryRole  
        CROSS JOIN 
            Users 
        ON 
            Users.objectId = lnk_role_member_user.User 
        WHERE 
            (DirectoryRoles.displayName LIKE '%Admin%' OR DirectoryRoles.displayName LIKE '%Global Reader%') 
            AND Users.accountEnabled = 1 
        ORDER BY 
            Users.lastPasswordChangeDateTime ASC 
    """)
    rows = cur.fetchall()

    print("\n# List of several Administrators")
    print(f"# {yellow}Yellow color{white} = Group where the User is a member!")
    print(f"# {red}Red color{white} = MFA is not enabled! (prediction)\n")
    print(line.underline+"Password Changed"+line.end+" "*3+line.underline+"User Created"+line.end+" "*7+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        role = row[1] if row[1] is not None else ""
        pw_last_change = row[2] if row[2] is not None else ""
        created = row[3] if row[3] is not None else ""  
        if pw_last_change == created:
            print(f"{red}{pw_last_change}   {created}   {mail} {yellow}({role}){white}")
        else:
            print(f"{pw_last_change}   {created}   {mail} {yellow}({role}){white}")
    conn.close()

def print_out_of_hours_password_change():
    cur.execute("""
        SELECT userPrincipalName, strftime('%Y-%m-%d %H:%M', lastPasswordChangeDateTime) 
        FROM Users 
        WHERE accountEnabled = 1 
        ORDER BY lastPasswordChangeDateTime DESC
    """)    
    rows = cur.fetchall()
    print("\n# Out of hours Password Changes (between 17h-08h + Sat + Sun)")
    print(f"# {yellow}Yellow color{white} = password changed time or day of the week out of hours\n")
    print(line.underline+"Password Changed"+line.end+" "*3+line.underline+"Changed Day"+line.end+" "*4+line.underline+"UserPrincipalName"+ line.end)
    for i, row in enumerate(rows):
        mail = row[0] if row[0] is not None else ""
        pw_last_change = row[1] if row[1] is not None else ""
        pw_last_change_convert = datetime.strptime(row[1], '%Y-%m-%d %H:%M')
        dayofweek = pw_last_change_convert.strftime("%A")
        if int(pw_last_change[10:13]) < 8 or int(pw_last_change[10:13]) > 17:       
            if dayofweek == "Saturday" or dayofweek == "Sunday":
                print(f"{pw_last_change}{yellow}   {dayofweek}{white}\t{' '*2}{mail}")
            else:
                print(f"{yellow}{pw_last_change}{white}   {dayofweek}\t{' '*2}{mail}")
        if int(pw_last_change[10:13]) > 8 or int(pw_last_change[10:13]) < 17:
                if dayofweek == "Saturday" or dayofweek == "Sunday":
                    print(f"{pw_last_change}{yellow}   {dayofweek}{white}\t{' '*2}{mail}")       
    print("")
    conn.close()

def print_generated_javascript_code():
    print(f"\n# Copy the JavaScript code below in {cyan}blue{white}.")
    print(f"# Go to {line.underline}https://portal.azure.com/#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers{line.end}")
    print(f"# after logging in and once the page has loaded successfully, paste this text into the web browser console:{white}\n")
 
    print(cyan+'''(async()=>{function downloadJSON(content,filename){const blob=new Blob([content],{type:'text/plain'});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=filename;link.click();};let secret,myData=[];async function fetchData(id){const response=await fetch("https://graph.microsoft.com/beta/users/"+id+"?$select=id,accountEnabled,userPrincipalName,lastPasswordChangeDateTime,createdDateTime",{headers:{accept:"application/json, text/plain, */*",authorization:"Bearer "+secret},method:"GET"});return response.json()};const formattedData=[];async function fetchUserData(){for(const data of myData){try{const userData=await fetchData(data.id);const formattedUser={id:userData.id,userPrincipalName:userData.userPrincipalName,lastPasswordChangeDateTime:userData.lastPasswordChangeDateTime,createdDateTime:userData.createdDateTime,timeDifference:Math.floor((new Date(userData.lastPasswordChangeDateTime).getTime()-new Date(userData.createdDateTime).getTime())/1000),accountEnabled:userData.accountEnabled};formattedData.push(formattedUser);}catch(error){console.error(error);}}} async function fetchAllDataAndUserData(){async function fetchData(url){try{const response=await fetch(url,{"headers":{"accept":"application/json, text/plain, */*","authorization":"Bearer "+secret},"method":"GET"});if(!response.ok){throw new Error('Network response was not ok')};const data=await response.json();return data}catch(error){throw error}};async function fetchAllData(){try{for(let i=0;i<sessionStorage.length;i++){let key=sessionStorage.key(i);let value=JSON.parse(sessionStorage.getItem(key));if(typeof value==='object'&&value!==null&&value.hasOwnProperty('secret')){let stringValue=JSON.stringify(value);if(stringValue.includes('openid')){secret=value.secret;break}}};let url="https://graph.microsoft.com/beta/users";while(url){const data=await fetchData(url);if(data&&data.value){myData=myData.concat(data.value)};await new Promise(resolve=>setTimeout(resolve,1000));url=data['@odata.nextLink']}}catch(error){console.error('Error:',error)}};await fetchAllData();await fetchUserData();};await fetchAllDataAndUserData();const mergedData=myData.map(data=>{const formattedUser=formattedData.find(user=>user.id===data.id);return{...data,...formattedUser};});const mergedJSON=JSON.stringify(mergedData);downloadJSON(mergedJSON,"merged_users.json");})();'''+white+"\n")
    exit()

if len(sys.argv) == 3 and args.json_input:
    print_mfa_anomalies()

if args.mfa_list:
    print_mfa_anomalies()
    
if args.outfile:
    print_mfa_anomalies()

if args.pw_month:
    print_password_change_info(31)

if args.pw_year:
    print_password_change_info(365)

if args.pw_older:
    print_password_change_info(36500)
    
if args.admin:
    try:
      print_admin_users()
    except:
      pass
          
if args.out_of_hours:
    print_out_of_hours_password_change()

if args.code_javascript:
    print_generated_javascript_code() 
    

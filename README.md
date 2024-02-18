# Azure AD Password Checker

In an Azure AD environment, it's possible to determine whether a user has Multi-Factor Authentication (MFA) disabled without requiring any special privileges. This can be accomplished by analyzing the account's creation date and last password change date. 

If an account's creation date and time match its last password change date and time, it may indicate that no human interaction has occurred since the account was created, and the user has not been able to enable Multi-Factor Authentication (MFA) or change their password. And there are other 'anomalies' such as the password change date being older than the creation date. This suggests also that Multi-Factor Authentication (MFA) couldn't be enabled because the User wasn't created yet!

Update on 16-10-2023:
What is the likelihood of two users changing their passwords at the exact same time? This could be considered as another MFA anomaly. It will be marked in blue and denoted as (times that it appears)

Update on 18-02-2024: 
It is possible to enable Multi-Factor Authentication (MFA) without requiring a password update, with phone call or SMS. However, if a user's account does not have a phone number listed, administrators will be unable to activate phone or text message verification options. This omission means users are unable to verify their phone number upon account creation or during login. The lack of phone number verification can make it easier to identify accounts where MFA is not configured. To address this, accounts without a phone number will be marked in light blue and annotated as (phone numbers: x).
<br>See: [Microsoft/Azure](https://learn.microsoft.com/en-us/azure/active-directory-b2c/multi-factor-authentication?pivots=b2c-user-flow#verification-methods)
_SMS or phone call - During the first sign-up or sign-in, the user is asked to provide and verify a phone number. During subsequent sign-ins, the user is prompted to select either the Send Code or Call Me option._

This information can be useful for identifying potential security risks designed for use by both red and blue teams.

The roadrecon database file or JSON file that has been extracted with the help of --code-javascript option is needed for this tool. 
Roadrecon tool is developed by dirkjanm and can be download on github https://github.com/dirkjanm/ROADtools or ```pip install roadrecon```.

How to use see:
```
python3 azurepwchecker.py
usage: azurepwchecker.py [-h] [--roadrecon-dump] [--roadrecon-dump-mfa] [-d DB] [-m] [-l] [-ll] [-lll] [-la] [-lo]
                         [-ji JSON_INPUT] [-c]

Azure AD Password Checker - This is a parser for generated JSON file or the roadrecon database file designed for use by both red and blue teams. 
Database can be created when using --code-javascript option to extract 'merged_users.json' file with be created to later input this file with --json-input argument.
And roadrecon generated roadrecon.db file can be used! roadrecon is developed by https://github.com/dirkjanm credits to him!

options:
  -h, --help            show this help message and exit
  -d DB, --db DB        Specify the path to the 'roadrecon.db' database file, default is this location
  -m, --mfa-list        User Accounts without MFA (No privileged user required)! This argument helps identify user
                        accounts that have not enabled Multi-Factor Authentication (MFA). If an account's creation
                        date and time match its last password change date and time, it may indicate that no human
                        interaction has occurred since the account was created, and the user has not been able to
                        enable MFA or change their password. And there are other 'anomalies' such as the password
                        change date being older than the creation date. This suggests also that Multi-Factor
                        Authentication (MFA) couldn't be enabled because the User wasn't created yet! :-]
  -mo OUTFILE, --outfile OUTFILE
                        Output users with MFA anomalies to file
  -l, --pw-month        User accounts that had their passwords changed last month
  -ll, --pw-year        User accounts that had their passwords changed last year
  -lll, --pw-older      User accounts that haven't changed their passwords in a long time, oldest first
  -la, --admin          User accounts that are members of 'Admin' named groups, including 'Global Reader'
  -lo, --out-of-hours   User password change that occurred outside of office hours, specifically between 5:00 PM
                        (17:00) and 8:00 AM (08:00) on weekdays, as well as on Saturdays and Sundays
  -ji JSON_INPUT, --json-input JSON_INPUT
                        Provide the JSON file imported from your web browser's console using JavaScript. For
                        'createdDateTime' and 'lastPasswordChange' details, ensure you download the JSON output using
                        the '--code-javascript' option.
  -c, --code-javascript
                        Perform extraction even if 'azurepwchecker.py' or 'roadrecon' is unavailable. This script
                        enables extraction through the JavaScript console of a web browser. To proceed, ensure you
                        have a valid account to log in at https://portal.azure.com/#view/Microsoft_AAD_UsersAndTenants
                        /UserManagementMenuBlade/~/AllUsers or an active session on a computer. Copy and paste the
                        provided JavaScript code into the browser's console. Once the session is validated and you
                        have the necessary permissions, a JSON file named 'merged_users.json' will be generated. You
                        can then import it using the following command as example: 'azurepwchecker.py --json-input
                        merged_users.json -m'
  -v, --version         show program's version number and exit
  
run roadrecon first:
  (Run the following command to install the tool "pip install roadrecon)"

  --roadrecon-dump      "roadrecon dump" command or do it with roadrecon
  --roadrecon-dump-mfa  "roadrecon dump --mfa" command (requires privileged access) or do it with roadrecon
  ```

### Don't have roadrecon > generate and copy ```azurepwchecker.py --code-javascript``` or js file in folder:

Follow these steps to retrieve a list of users along with their account information using the provided script.

1. **Login to Azure Portal**
   - Go to [https://portal.azure.com](https://portal.azure.com) and log in with your valid account.

2. **Access User Management**
   - Navigate to [User Management](https://portal.azure.com/#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers) in the Azure portal.

3. **Open Developer Tools**
   - Press `F12` on your web browser to open the developer tools.

4. **Execute the Script**
   - Copy and paste the provided script.

5. **Retrieve UsersList and UserInfo**
   - The script will fetch the UsersList along with user information including creation date and last password change.

6. **Download Merged User Information**
   - Once the script execution is complete, check your downloads. A file named `merged_users.json` will be generated if everything went smoothly.

7. **Run on Azure AD Password Checker**
   -  `azurepwchecker.py --json-input merged_users.json` 
  

See example:

https://github.com/quahac/Azure-AD-Password-Checker/assets/49560894/0fd77e2c-068e-4aef-aafd-c5ec23db7385

See intro:

https://user-images.githubusercontent.com/49560894/233073626-d1ccc173-c3cf-4751-878b-e8f0c65e6c0a.mp4

Update 16-10-2023:

![double_lastpasswordchangedatetime](https://github.com/quahac/Azure-AD-Password-Checker/assets/49560894/4650df7d-82b4-48cb-93eb-af438a441f66)

How to use the ```--code-javascript``` argument to generate a list of users on the Azure Portal, which can then be imported using the command ```azurepwchecker.py --json-input merged_users.json```:

Update 13-02-2024:

I uploaded edited version of GraphRunner from @dafthack and credits to him. In this modified version, I have added a new feature that lets you read HAR files directly from the "victim's" device. This new function helps in checking and examining Access Tokens to access different permissions or scopes. Additionally, if an Access Token has expired, this version allows the use of a Refresh Token to create a new Access Token. This process is time-sensitive, but it removes the need for usernames and passwords, if you already have logged in to Office365 enviroment, as it only requires the session tokens found in HAR files.

Please understand that the code might seem a bit disorganized. My expertise is not primarily in JavaScript, so my main focus was on adding new features rather than organizing the code.

1. Download HAR file(s) you can use the Development Tools available in web browsers. For most browsers, simply press F12 to open the Development Tools, then navigate to the 'Network' tab to save the HAR files, after refreshing webpage:
[video](https://github.com/quahac/Azure-AD-Password-Checker/assets/49560894/84dddabd-3feb-4fa5-a00d-eaa2277b8789)

3. Upload your HAR file(s) via the provided interface. Once uploaded, you can navigate through various Access Tokens to analyze session details, including their scopes and more. Tokens displayed in red indicate that they have expired. GraphRunner also supports the use of Refresh Tokens to generate new, valid Access Tokens when necessary:
[video](https://github.com/quahac/Azure-AD-Password-Checker/assets/49560894/c7b045a1-ab21-4cae-b06f-d10bb3cf8af2)

4. Added features to allow the downloading of complete user data in a JSON file, detect MFA anomalies in accounts, and download a list of these anomalies:
[video](https://github.com/quahac/Azure-AD-Password-Checker/assets/49560894/e14741c0-0cc5-44b5-b231-fea0b9b0d17b)





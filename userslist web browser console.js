// Login to: https://portal.azure.com with valid account
// Goto: https://portal.azure.com/#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers
// F12 on you web browser
// Copy Paste this script 
// Get UsersList + UserInfo (created date + last password change) together in one script.
// Look at your downloads when finished and 'merged_users.json' wil be generated when all goes good


(async() => {
    function downloadJSON(content, filename) {
        const blob = new Blob([content], {
            type: 'text/plain'
        });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    };
    let secret,
    myData = [];
    async function fetchData(id) {
        const response = await fetch("https://graph.microsoft.com/beta/users/" + id + "?$select=id,accountEnabled,userPrincipalName,lastPasswordChangeDateTime,createdDateTime", {
            headers: {
                accept: "application/json, text/plain, */*",
                authorization: "Bearer " + secret
            },
            method: "GET"
        });
        return response.json()
    };
    const formattedData = [];
    async function fetchUserData() {
        for (const data of myData) {
            try {
                const userData = await fetchData(data.id);
                const formattedUser = {
                    id: userData.id,
                    userPrincipalName: userData.userPrincipalName,
                    lastPasswordChangeDateTime: userData.lastPasswordChangeDateTime,
                    createdDateTime: userData.createdDateTime,
                    timeDifference: Math.floor((new Date(userData.lastPasswordChangeDateTime).getTime() - new Date(userData.createdDateTime).getTime()) / 1000),
                    accountEnabled: userData.accountEnabled
                };
                formattedData.push(formattedUser);
            } catch (error) {
                console.error(error);
            }
        }
    }
    async function fetchAllDataAndUserData() {
        async function fetchData(url) {
            try {
                const response = await fetch(url, {
                    "headers": {
                        "accept": "application/json, text/plain, */*",
                        "authorization": "Bearer " + secret
                    },
                    "method": "GET"
                });
                if (!response.ok) {
                    throw new Error('Network response was not ok')
                };
                const data = await response.json();
                return data
            } catch (error) {
                throw error
            }
        };
        async function fetchAllData() {
            try {
                for (let i = 0; i < sessionStorage.length; i++) {
                    let key = sessionStorage.key(i);
                    let value = JSON.parse(sessionStorage.getItem(key));
                    if (typeof value === 'object' && value !== null && value.hasOwnProperty('secret')) {
                        let stringValue = JSON.stringify(value);
                        if (stringValue.includes('openid')) {
                            secret = value.secret;
                            break
                        }
                    }
                };
                let url = "https://graph.microsoft.com/beta/users";
                while (url) {
                    const data = await fetchData(url);
                    if (data && data.value) {
                        myData = myData.concat(data.value)
                    };
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    url = data['@odata.nextLink']
                }
            } catch (error) {
                console.error('Error:', error)
            }
        };
        await fetchAllData();
        await fetchUserData();
    };
    await fetchAllDataAndUserData();
    const mergedData = myData.map(data => {
        const formattedUser = formattedData.find(user => user.id === data.id);
        return {
            ...data,
            ...formattedUser
        };
    });
    const mergedJSON = JSON.stringify(mergedData);
    downloadJSON(mergedJSON, "merged_users.json");
})();

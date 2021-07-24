import subprocess #import required library
data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n') #store profiles data in "data" variable
profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i] #store the profile by converting them to list
for i in profiles:
    # running the command to check passwords
    results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split('\n')
    # storing passwords after converting them to list
    results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]

    try:
        print ("{:<30}|  {:<}".format(i, results[0]))
    except IndexError:
        print ("{:<30}|  {:<}".format(i, ""))

 # Coded with 💙 by Mr. Unity Buddy

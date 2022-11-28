from screeninfo import get_monitors    

def getMonitorInfo():  
    monitors = {}
    c = 1
    for m in get_monitors():
        monitors[c] = [m.width, m.height]
        c += 1
    return monitors

def loadProfiles():
    profiles = {}
    try:
        with open("profile.txt", "r") as file:
            lines = file.readlines()
            print(lines)
        for line in lines:
            line_data = line.split(",")
            line_data[8] = line_data[8][:-1]
            profiles[line_data[8]] = line_data
        print(profiles)
        return profiles
    except:
        return None
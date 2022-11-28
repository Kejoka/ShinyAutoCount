from PIL import Image
import mss, mss.tools, time, pytesseract
import PySimpleGUI as gui
from multiprocessing import Process
import multiprocessing
from os.path import exists
from sys import platform
import utils

def main():
    print("Loading profile...")
    monitors = utils.getMonitorInfo()
    profile = utils.loadProfiles()
    font = ("Arial", 13)
    if not profile:
        print("No Profile found")
        profile = {}
        if platform != "darwin":
            profile["Shuckle"] = ["1", "Route", 0, 0, 500, 300, "C:/Example/Counter/txt/File/Path.txt", "C:\\Program Files\\Tesseract-OCR\\tesseract.exe", "Shuckle"]
        else:
            profile["Shuckle"] = ["1", "Route", 0, 0, 500, 300, "/Example/Counter/txt/File/Path.txt", "/opt/homebrew/Cellar/tesseract/5.2.0/", "Shuckle"]
        saveProfile(profile["Shuckle"])
        print("Profile generated")
    for i in range(2,6):
        profile[list(profile.keys())[0]][i] = int(float(profile[list(profile.keys())[0]][i]))
    active = list(profile.keys())[0]

    input_column = [
        [gui.Text("Oh no! Shuckle can't read punctuation, ä, ö, ü and ß very well :(", font=font)],
        [gui.Text("Profile Name", size=(7,1)), gui.InputText(key="profile_name", default_text=profile[active][8], size=(64,10))],
        [gui.Text("Monitor", size=(7,1)), gui.InputText(key="monitor_num", default_text=profile[active][0], size=(64,10))],
        [gui.Text("Scan-Text", size=(7,1)), gui.InputText(key="scan_text", default_text=profile[active][1], size=(64,10))],
        [gui.Text("Offset-X", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,monitors[int(profile[active][0])][0]), default_value=profile[active][2], size=(50,10), key="offset-x", enable_events=True)], 
        [gui.Text("Offset-Y", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,monitors[int(profile[active][0])][1]), default_value=profile[active][3], size=(50,10), key="offset-y", enable_events=True)], 
        [gui.Text("Width", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,monitors[int(profile[active][0])][0]), default_value=profile[active][4], size=(50,10), key="width", enable_events=True)], 
        [gui.Text("Height", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,monitors[int(profile[active][0])][1]), default_value=profile[active][5], size=(50,10), key="height", enable_events=True)], 
        [gui.Text("File", size=(7,1)), gui.InputText(default_text=profile[active][6], key="path_text", size=(55,10)), gui.FileBrowse(key="txt_browse", target="path_text")],
        [gui.Button("Start Counter", size=(65,1), key="start", enable_events=True)],
        [gui.Button("Save Profile", key="save", enable_events=True, size=(65, 1))],
        [gui.Button("Delete Profile", key="delete", enable_events=True, size=(65, 1))],
        [gui.Text("Choose a profile", font=font)],
        [gui.Listbox(values=profile.keys(), size=(65,8), key="profile_box", enable_events=True)]
    ]

    image_viewer_column = [
        [gui.Text("Preview: ")],
        [gui.Image(key="img", size=(300, 300), filename="img/shuckle.png")]
    ]

    layout_setup = [
        [
            gui.Column(input_column, key="param"),
            gui.VSeperator(),
            gui.Column(image_viewer_column),
        ]
    ]

    layout_run = [
        [gui.Text("Shuckle is searching for: ", key="search_text")],
        [gui.Text("and writing to: ", key="file_text")],
        [gui.Text("Thanks, Shuckle!")],
        [gui.Image(filename="img/shuckle.png")],
        [gui.Button("Stop Counting", key="stop", enable_events=True)],
        [gui.Button("Increment Count by 1", key="inc", enable_events=True)],
        [gui.Button("Decrement Count by 1", key="dec", enable_events=True)]
    ]

    layout_tess = [
        [gui.Text("Tesseract-OCR could not be found")],
        [gui.Text("Specifiy the Path to tesseract.exe, save profile and restart")],
        [gui.Text("Current", size=(7,1)), gui.InputText(default_text=profile[active][7], key="tess_path", size=(55,10)), gui.FileBrowse(key="tess_browse", target="tess_path")],
        [gui.Button("Save Profile", key="save", enable_events=True, size=(65, 1))]
    ]

    tess_check = exists(profile[active][7])
    if tess_check:
        if platform != "darwin":
            pytesseract.pytesseract.tesseract_cmd = profile[active][7]

        layout = [
            [
                gui.Column(layout_setup, key="setup"),
                gui.Column(layout_run, key="running", visible=False)
            ]
        ]
    else:
        layout = [
            [
                gui.Column(layout_tess)
            ]
        ]

    window = gui.Window("ShinyAutoCount", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == gui.WIN_CLOSED:
            try:
                p.terminate()
                break
            except:
                break
        if event in ["offset-x", "offset-y", "width", "height"]:
            screenPreview(values, window)
        elif event == "start":
            window["search_text"].update("Shuckle is searching for: " + values["scan_text"])
            window["file_text"].update("and writing to: " + values["path_text"])
            window["setup"].update(visible=False)
            window["running"].update(visible=True)
            print("Starting AutoCounter Process...")
            p = Process(target=count, args=(int(values["monitor_num"]), int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]), values["scan_text"], values["path_text"], profile[active][7]))
            p.start()
        elif event == "stop":
            window["setup"].update(visible=True)
            window["running"].update(visible=False)
            p.terminate()
            print("AutoCounter terminated")
        elif event == "save":
            print("Saving Profile...")
            data = []
            profile_names = []
            for key in profile.keys():
                profile_names.append(profile[key][8])
            if tess_check:
                data.append(values["monitor_num"])
                data.append(values["scan_text"])
                data.append(str(values["offset-x"]))
                data.append(str(values["offset-y"]))
                data.append(str(values["width"]))
                data.append(str(values["height"]))
                data.append(values["path_text"])
                data.append(profile[active][7])
                data.append(values["profile_name"])
            else:
                data = profile
                data[7] = values["tess_path"]
            if values["profile_name"] not in profile_names:
                saveProfile(data)
            else:
                updateProfile(data)
            profile = utils.loadProfiles()
            for i in range(2,6):
                profile[list(profile.keys())[0]][i] = int(float(profile[list(profile.keys())[0]][i]))
            active = list(profile.keys())[0]
            window["profile_box"].update(values = profile.keys())
        elif event == "delete":
            deleteProfile(values["profile_name"])
            profile = utils.loadProfiles()
            for i in range(2,6):
                profile[list(profile.keys())[0]][i] = int(float(profile[list(profile.keys())[0]][i]))
            active = list(profile.keys())[0]
            window["profile_box"].update(values = profile.keys())
        elif event == "profile_box":
            selected = window["profile_box"].get_indexes()[0]
            active = list(profile.keys())[selected]
            window["profile_name"].update(value=profile[active][8])
            window["monitor_num"].update(value=profile[active][0])
            window["scan_text"].update(value=profile[active][1])
            window["offset-x"].update(value=profile[active][2])
            window["offset-y"].update(value=profile[active][3])
            window["width"].update(value=profile[active][4])
            window["height"].update(value=profile[active][5])
            window["path_text"].update(value=profile[active][6])
        elif event == "inc":
            incrementTxt(values["path_text"])
        elif event == "dec":
            decrementTxt(values["path_text"])
    window.close()

def screenPreview(values, window):
    screen(int(values["monitor_num"]), int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]))
    img = Image.open("1.png")
    img.thumbnail((300,300), Image.Resampling.LANCZOS)
    img.save("1.png", "PNG")
    window["img"].update(filename="1.png")

def count(mon, x, y, w, h, scan_val, txt_path, tess_path):
    print("AutoCounter started")
    counter = 0
    if platform != "darwin":
        pytesseract.pytesseract.tesseract_cmd = tess_path

    starttime = time.time()
    backupCount(txt_path)
    paused = False
    not_found_again = 0
    while True:
        # print("tick")
        screen(mon, x, y, w, h)
        img_string = pytesseract.image_to_string(Image.open("1.png"))
        # print(img_string)
        # print(not_found_again)
        if scan_val in img_string:
            if paused == False:
                not_found_again = 0
                # print(scan_val + " found")
                counter += 1
                # print("Current Session Counter: " + str(counter))
                incrementTxt(txt_path)
                paused = True
        else:
            not_found_again += 1
        if not_found_again > 10:
                paused = False
                not_found_again = 0
        time.sleep(0.1)

def grabMon(mon, x, y, w, h):
    with mss.mss() as sct:
        monitor_number = mon
        try:
            mon = sct.monitors[monitor_number]
        except:
            mon = sct.monitors[1]
        monitor = {
            "top": mon["top"] + y,
            "left": mon["left"] + x,
            "width": w,
            "height": h,
            "mon": monitor_number
        }
        return monitor

def screen(mon, x, y, w, h):
    monitor = grabMon(mon, x, y, w, h)
    output = "1.png".format(**monitor)
    with mss.mss() as sct:
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)

def incrementTxt(txt_path):
    try:
        file = open(txt_path, "r")
        curr_count = int(file.readline())
        curr_count += 1
        file = open(txt_path, "w")
        file.write(str(curr_count))
        return True
    except:
        print("Error: File not Found")
        return False

def decrementTxt(txt_path):
    try:
        file = open(txt_path, "r")
        curr_count = int(file.readline())
        curr_count -= 1
        file = open(txt_path, "w")
        file.write(str(curr_count))
        return True
    except:
        print("Error: File not Found")
        return False

def backupCount(path):
    try:
        file = open(path, "r")
        num = int(file.readline())
        file = open("backup.txt", "w+")
        file.write(str(num))
        return True
    except:
        print("Error: File not Found")
        return False

def saveProfile(data):
    try:
        file = open("profile.txt", "a")
        for index, val in enumerate(data):
            if index == len(data)-1:
                file.write(str(val))
            else:
                file.write(str(val) + ",")
        file.write("\n")
        print("Profile saved:")
        print(data)
    except:
        print("Error: Saving not possible")

def updateProfile(data):
    profiles = utils.loadProfiles()
    try:
        file = open("profile.txt", "w")
        for key in profiles.keys():
            if key == data[8]:
                for i in range(len(profiles[key])):
                    if i == len(profiles[key])-1:
                        file.write(str(data[i]))
                    else:
                        file.write(str(data[i]) + ",")
            else:
                for i in range(len(profiles[key])):
                    if i == len(profiles[key])-1:
                        file.write(str(profiles[key][i]))
                    else:
                        file.write(str(profiles[key][i]) + ",")
            file.write("\n")
        print("Profile updated:")
    except:
        print("Error - Updating failed")

def deleteProfile(name):
    profiles = utils.loadProfiles()
    try:
        file = open("profile.txt", "w")
        for key in profiles.keys():
            if key == name:
                continue
            for i in range(len(profiles[key])):
                if i == len(profiles[key])-1:
                    file.write(str(profiles[key][i]))
                else:
                    file.write(str(profiles[key][i]) + ",")
            file.write("\n")
        print("Profile deleted:")
        print(name)
    except:
        print("Error: Deleting not possible")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
from PIL import Image
import mss, mss.tools, time, pytesseract
import PySimpleGUI as gui
from multiprocessing import Process
import multiprocessing
from os.path import exists

def main():
    print("Loading profile...")
    profile = loadProfile()
    if not profile:
        print("No Profile found")
        profile = ["1", "Shuckle", 0, 0, 500, 300, "C:/Example/Counter/txt/File/Path.txt", "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"]
        print("Profile generated")
    else:
        for i in range(2,6):
            profile[i] = int(float(profile[i]))
    print(profile)


    input_column = [
        [gui.Text("Monitor", size=(7,1)), gui.InputText(key="monitor_num", default_text=profile[0], size=(64,10))],
        [gui.Text("Scan-Text", size=(7,1)), gui.InputText(key="scan_text", default_text=profile[1], size=(64,10))],
        [gui.Text("Offset-X", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,1920), default_value=profile[2], size=(50,10), key="offset-x", enable_events=True)], 
        [gui.Text("Offset-Y", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,1080), default_value=profile[3], size=(50,10), key="offset-y", enable_events=True)], 
        [gui.Text("Width", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,1920), default_value=profile[4], size=(50,10), key="width", enable_events=True)], 
        [gui.Text("Height", size=(7,1)), gui.Slider(orientation='horizontal', range=(0,1080), default_value=profile[5], size=(50,10), key="height", enable_events=True)], 
        [gui.Text("File", size=(7,1)), gui.InputText(default_text=profile[6], key="path_text", size=(55,10)), gui.FileBrowse(key="txt_browse", target="path_text")],
        [gui.Button("Start Counter", size=(65,1), key="start", enable_events=True)],
        [gui.Button("Save Profile", key="save", enable_events=True, size=(65, 1))]
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
        [gui.Button("Stop Counting", key="stop", enable_events=True)]
    ]

    layout_tess = [
        [gui.Text("Tesseract-OCR could not be found")],
        [gui.Text("Specifiy the Path to tesseract.exe, save profile and restart")],
        [gui.Text("Current", size=(7,1)), gui.InputText(default_text=profile[7], key="tess_path", size=(55,10)), gui.FileBrowse(key="tess_browse", target="tess_path")],
        [gui.Button("Save Profile", key="save", enable_events=True, size=(65, 1))]
    ]

    tess_check = exists(profile[7])
    if tess_check:
        pytesseract.pytesseract.tesseract_cmd = profile[7]

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
            screen(int(values["monitor_num"]), int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]))
            img = Image.open("1.png")
            img.thumbnail((300,300), Image.Resampling.LANCZOS)
            img.save("1.png", "PNG")
            window["img"].update(filename="1.png")
        elif event == "start":
            window["search_text"].update("Shuckle is searching for: " + values["scan_text"])
            window["file_text"].update("and writing to: " + values["path_text"])
            window["setup"].update(visible=False)
            window["running"].update(visible=True)
            print("Starting AutoCounter Process...")
            p = Process(target=count, args=(int(values["monitor_num"]), int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]), values["scan_text"], values["path_text"]))
            p.start()
        elif event == "stop":
            window["setup"].update(visible=True)
            window["running"].update(visible=False)
            p.terminate()
            print("AutoCounter terminated")
        elif event == "save":
            print("Saving Profile...")
            data = []
            if tess_check:
                data.append(values["monitor_num"])
                data.append(values["scan_text"])
                data.append(str(values["offset-x"]))
                data.append(str(values["offset-y"]))
                data.append(str(values["width"]))
                data.append(str(values["height"]))
                data.append(values["path_text"])
                data.append(profile[7])
            else:
                data = profile
                data[7] = values["tess_path"]
            saveProfile(data)
    window.close()

def count(mon, x, y, w, h, scan_val, txt_path):
    print("AutoCounter started")
    counter = 0
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    starttime = time.time()
    backupCount(txt_path)
    while True:
        print("tick")
        screen(mon, x, y, w, h)
        img_string = pytesseract.image_to_string(Image.open("1.png"))
        if scan_val in img_string:
            print(scan_val + " found")
            counter += 1
            print("Current Session Counter: " + str(counter))
            incrementTxt(txt_path)
            time.sleep(5)
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
        count = int(file.readline())
        count += 1
        file = open(txt_path, "w")
        file.write(str(count))
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
        file = open("profile.txt", "w+")
        for val in data:
            file.write(str(val) + ",")
        print("Profile saved:")
        print(data)
    except:
        print("Error: Saving not possible")

def loadProfile():
    profile = []
    try:
        file = open("profile.txt", "r")
        data = file.readline()
        profile = data.split(",")
        return profile
    except:
        return None

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
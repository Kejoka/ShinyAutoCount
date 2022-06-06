from PIL import Image
import mss, mss.tools, time, pytesseract
import PySimpleGUI as gui
import os.path
from multiprocessing import Process

def main():
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    profile = loadProfile()
    if not profile:
        profile = ["1", "Shuckle", 0, 0, 500, 300, "C:/Example/Counter/txt/File/Path.txt"]
    else:
        for i in range(2,6):
            profile[i] = int(float(profile[i]))

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

    layout = [
        [
            gui.Column(layout_setup, key="setup"),
            gui.Column(layout_run, key="running", visible=False)
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
            img.thumbnail((300,300), Image.ANTIALIAS)
            img.save("1.png", "PNG")
            window["img"].update(filename="1.png")
        if event == "start":
            window["search_text"].update("Shuckle is searching for: " + values["scan_text"])
            window["file_text"].update("and writing to: " + values["path_text"])
            window["setup"].update(visible=False)
            window["running"].update(visible=True)
            p = Process(target=count, args=(int(values["monitor_num"]), int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]), values["scan_text"], values["path_text"]))
            p.start()
        if event == "stop":
            window["setup"].update(visible=True)
            window["running"].update(visible=False)
            p.terminate()
        elif event == "save":
            data = []
            data.append(values["monitor_num"])
            data.append(values["scan_text"])
            data.append(str(values["offset-x"]))
            data.append(str(values["offset-y"]))
            data.append(str(values["width"]))
            data.append(str(values["height"]))
            data.append(values["path_text"])
            saveProfile(data)
    window.close()

def count(mon, x, y, w, h, scan_val, txt_path):
    counter = 0
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    starttime = time.time()
    backupCount(txt_path)
    while True:
        screen(mon, x, y, w, h)
        if scan_val in pytesseract.image_to_string(Image.open("1.png")):
            counter += 1
            print(counter)
            if not incrementTxt(txt_path):
                return
            time.sleep(5.0 - ((time.time() - starttime) % 5.0))
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))

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
    main()
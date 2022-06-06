from PIL import Image
import mss, mss.tools, time, pytesseract
import PySimpleGUI as gui
import os.path
from multiprocessing import Process

# p doesnt stop on window close
# counter not written to txt file
# UI ugly af
# implement runngin ui
# implement save button
# build exe
# add profiles

scan_val = "Pottrott"
txt_path = ""

def main():
    global scan_val
    global txt_path
    counter = 0
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    starttime = time.time()

    input_column = [
        [gui.Text("Scan-Text", size=(10,1)), gui.InputText(key="scan_text", default_text="Pottrott", enable_events=True)],
        [gui.Text("Offset-X"), gui.Slider(orientation='horizontal', range=(0,1920), default_value=0, size=(50,10), key="offset-x", enable_events=True)], 
        [gui.Text("Offset-Y"), gui.Slider(orientation='horizontal', range=(0,1080), default_value=0, size=(50,10), key="offset-y", enable_events=True)], 
        [gui.Text("Width"), gui.Slider(orientation='horizontal', range=(300,1300), default_value=0, size=(50,10), key="width", enable_events=True)], 
        [gui.Text("Height"), gui.Slider(orientation='horizontal', range=(100,1100), default_value=0, size=(50,10), key="height", enable_events=True)], 
        [gui.Text("Current: "), gui.InputText(default_text="C:/Example/Counter/txt/File/Path", key="path_text"), gui.FileBrowse(key="txt_browse", target="path_text"), gui.Button("Start Counter", size=(10,1), key="btn", enable_events=True)]

    ]

    image_viewer_column = [
        [gui.Text("Preview: ")],
        [gui.Image(key="img")]
    ]

    layout_run = [
        [gui.Text("Test", size=(50,10))]
    ]

    layout = [
        [
            gui.Column(input_column, key="param"),
            gui.VSeperator(),
            gui.Column(image_viewer_column),
            gui.Column(layout_run)
        ]
    ]

    window = gui.Window("EinfachKeyl AutoCounter", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == gui.WIN_CLOSED:
            break
        if event == "txt":
            filename = values["txt"]
        if event == "offset-x":
            screen(int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]))
            window["img"].update(filename="1.png")
        elif event == "offset-y":
            screen(int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]))
            window["img"].update(filename="1.png")
        elif event == "width":
            screen(int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]))
            window["img"].update(filename="1.png")
        elif event == "height":
            screen(int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"]))
            window["img"].update(filename="1.png")
        elif event == "scan_text":
            scan_val = values["scan_text"]
        elif event == "btn":
            txt_path = values["path_text"]
            window["param"].update(visible=False)
            p = Process(target=count, args=(int(values["offset-x"]), int(values["offset-y"]), int(values["width"]), int(values["height"])))
            p.start()
    window.close()

def count(x, y, w, h):
    counter = 0
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    starttime = time.time()
    print("- EinfachKeyl Autocounter -")
    print("running...")
    print("CTRL + C to stop")
    while True:
        screen(x, y, w, h)
        if "Neumondinsel" in pytesseract.image_to_string(Image.open("1.png")):
            counter += 1
            print(counter)
            time.sleep(5.0 - ((time.time() - starttime) % 5.0))
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))

def grabMon(x, y, w, h):
    with mss.mss() as sct:
        monitor_number = 1
        mon = sct.monitors[monitor_number]
        monitor = {
            "top": mon["top"] + y,
            "left": mon["left"] + x,
            "width": w,
            "height": h,
            "mon": monitor_number
        }
        return monitor

def screen(x, y, w, h):
    monitor = grabMon(x, y, w, h)
    output = "1.png".format(**monitor)
    with mss.mss() as sct:
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)

if __name__ == "__main__":
    main()
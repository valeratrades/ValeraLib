import json
import time
import pandas as pd
import os
from datetime import datetime


def dbg(*args):
    print("\n#==========================================================")
    print(args[0])
    for arg in args[1:]:
        print(f'\n{arg}')
    print("#==========================================================\n")
    alert()
    input()

# <tg>


class Telegram:
    def __init__(self):
        import telebot
        self.bot_keys = {'PollPuller_bot': '5131848746:AAEk1LuXl7_0fdN5WzA956t_jjo8Pn6cbl8',
                         'ValeraMainBot': '6225430873:AAEYlbJ2bY-WsLADxlWY1NS-z4r75sf9X5I'}
        self.tb = telebot.TeleBot(self.bot_keys['ValeraMainBot'], False)

        self.chat_ids = {"WTT": -1001179171854, "Alerts": -1001800341082}
        self.default_chat_id = self.chat_ids['Alerts']

    def msg(self, msg, chat_id=None):
        chat_id = self.default_chat_id if chat_id is None else chat_id
        self.tb.send_message(chat_id, msg)

    def img(self, directory, chat_id=None):
        chat_id = self.default_chat_id if chat_id is None else chat_id
        with open(directory, "rb") as img:
            self.tb.send_photo(chat_id, img)


def tg_msg(text=""):
    if text == "":
        caller = get_caller_name()
        text = f"{caller} has finished"
    tb = Telegram()
    tb.msg(text)
# </tg>


def shutdown():
    os.system("shutdown /s /t 1")


def load(path):
    if not path.endswith('.json'):
        path += '.json'
    data = json.load(open(path, 'r'))
    return data


class TimePerfCounters():
    def __init__(self, mark=' * ', autoprint=False):
        self.perfcounters = []
        self.mark = mark
        self.autoprint = autoprint

        self.longest_text = 0
        self.total = 0

    def __call__(self, text=''):
        self.perfcounters.append((time.perf_counter(), text))
        if len(text) > self.longest_text:
            self.longest_text = len(text)

        if self.autoprint and len(self.perfcounters) > 1:
            self.p()

    def p(self, total=True):
        total = self.total + self.perfcounters[-1][0] - self.perfcounters[0][0]
        for i in range(len(self.perfcounters)-1):
            if self.perfcounters[i+1][1] == '':
                continue
            elapsed = self.perfcounters[i+1][0] - self.perfcounters[i][0]
            text = f"{self.perfcounters[i+1][1]:>{self.longest_text}}"
            if self.perfcounters[i+1][1] != '':
                text = f"{text} in: "
            bottleneck_mark = " (!)" if elapsed > total ** 0.75 else ""
            print(f"{self.mark}{text}{elapsed:.2f}{bottleneck_mark}")
        if total:
            empty = f"{' ':>{self.longest_text}}"
            empty += '   : '
            total_print = f"{self.mark}{empty}{total} total"
            print(total_print)
        self.perfcounters = [self.perfcounters[-1]]


def decide_on_datetime_format(*args, format_str='%Y-%m-%d %H:%M:%S'):  # //
    if len(args) == 2:
        CASE = 'strings'
        t1, t2 = args
        if isinstance(t1, datetime):
            dt1, dt2 = t1, t2
        else:
            dt1 = datetime.strptime(t1, format_str)
            dt2 = datetime.strptime(t2, format_str)
    elif len(args) == 1 and isinstance(args[0], list):
        CASE = "list"
        _list = args[0]
        datetime_list = [ts if isinstance(ts, pd.DatetimeIndex) else ts.to_pydatetime(
        ) if isinstance(ts, pd.Timestamp) else None for ts in _list]
        dt1 = next((item for item in datetime_list if item is not None), None)
        dt2 = next((item for item in reversed(
            datetime_list) if item is not None), None)
    elif len(args) == 1 and isinstance(args[0], pd.DatetimeIndex):
        CASE == 'DatetimeIndex'
        print('The hell do I do with a DatetimeIndex?')
    else:
        CASE == 'Unknown'
        raise Exception(
            'Can only process one list or two datetime-like values')

    diff = abs(dt1 - dt2)
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        new_format_str = '%Y-%m-%d %H:%M:%S'
    elif hours > 0:
        new_format_str = '%H:%M:%S'
    elif minutes > 0:
        new_format_str = '%M:%S'
    else:
        new_format_str = '%S'

    out = CASE
    if CASE == 'strings':
        out = new_format_str
    elif CASE == 'list':
        out = [dt.strftime(new_format_str)
               if dt is not None else None for dt in datetime_list]
    return out


# // move to be a property of .utils.DuckTypes class Timestamp
def round_time_down(dt, round_to=300):
    timestamp = dt.to_ms() / 1000
    rounded_timestamp = timestamp // round_to * round_to
    return datetime.fromtimestamp(rounded_timestamp)


def create_shortcut(source_path, destination_folder):
    import pythoncom
    from win32com.shell import shell

    file_name = os.path.basename(source_path)
    source_folder = os.path.dirname(source_path)
    destination_path = os.path.join(destination_folder, file_name + ".lnk")

    shortcut = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_IShellLink
    )

    shortcut.SetPath(source_path)
    shortcut.SetDescription("Shortcut to " + file_name)
    shortcut.SetIconLocation(source_path, 0)
    shortcut.SetWorkingDirectory(source_folder)

    persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(os.path.abspath(destination_path), 0)


def time_wrapper(fn, *args, **kwargs):
    shutdown_after = False
    if args[0] == 'shutdown_after':
        shutdown_after = True
        args = args[1:]
    start_time = time.time()
    fn(*args, **kwargs)
    elapsed = time.time() - start_time
    if elapsed > 60:
        tg_msg(f'{fn.__name__} has finished')
    if shutdown_after and elapsed > 180:
        shutdown()


def silent_wrapper(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except:
        pass


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def alert(_input=False):
    dir = os.path.dirname(os.path.abspath(__file__))
    from playsound import playsound
    playsound(os.path.join(dir, 'utils/Notification.mp3'))
    if _input:
        input()


def get_caller_name():
    import inspect
    caller_frame = inspect.stack()[1]
    caller_filename_full = caller_frame.filename
    caller_filename_only = os.path.splitext(
        os.path.basename(caller_filename_full))[0]
    return caller_filename_only


def text_from_image():
    import pytesseract
    from PIL import Image

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    t = Image.open("img.png")
    text = pytesseract.image_to_string(t, config='')
    print(text)


if __name__ == '__main__':
    try:
        print('normally I test some function here')
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        from Valera import alert
        alert()

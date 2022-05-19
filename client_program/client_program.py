import datetime
import subprocess
import requests
import psutil
import uuid
import time
import sys

update_time = 60
version = 0.5


def version_check():
    return float(version)


def new_pc_check():
    id = uuid.getnode()
    data = {"pc": id}
    r = requests.post("https://api.legende.cc/check", data=data)
    print(r.text)
    print("Sending interval is set to 1 minute")
    if "New server detected." in r.text:
        sys.exit(0)
    else:
        while True:
            send_data()


def get_network_usage():
    old_value = 0
    arr = []
    for i in range(int(update_time / 2)):  # change updating time
        new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        value = new_value - old_value
        value = value / 1024. / 1024. * 8
        old_value = new_value
        arr.append("%0.3f" % value)
        time.sleep(1)
    arr.pop(0)
    return arr


def send_data():
    id = uuid.getnode()
    cpu_usage = psutil.cpu_percent(interval=update_time / 2)
    ram = psutil.virtual_memory().percent
    x = str(get_network_usage())
    data = {"pc": id, "cpu_usage": cpu_usage, "ram_usage": ram, "network_usage": x}
    last_updated = datetime.datetime.now().strftime("%H:%M")
    try:
        req = requests.post("https://api.legende.cc", data=data).text
        if "Service Unavailable" in req:
            print(f"Update failed at {last_updated}")
        print(f"Updated successfully at {last_updated}")
    except:
        print(f"Updated failed at {last_updated}")

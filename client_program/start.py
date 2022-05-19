try:
    import client_program
    import requests
    import zipfile
    import shutil
    import sys
    import os
except ModuleNotFoundError:
    print('run "pip install -r requirements.txt", before you run the program')
    raise SystemExit(0)

try:
    req = requests.get("https://api.legende.cc/version")
    api_version = float(req.text)
except:
    print("I can't reach the service, please check if you have a working internet connection.\n"
          "If you do have a working internet connection --> Wait a couple of hours and try again.")
    sys.exit(0)

if client_program.version != api_version:
    print(f"Outdated version (V{client_program.version})\n"
          f"updating to V{api_version}...")
    with requests.get(f"https://cdn.legende.cc/versions/{api_version}.zip", stream=True) as r:
        with open("update.zip", 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    with zipfile.ZipFile("update.zip", 'r') as zip_ref:
        zip_ref.extractall("")
    os.remove("update.zip")
    os.system("python start.py")

else:
    print("✓ Most recent version installed")
    client_program.new_pc_check()

from flask import Flask, request
import datetime
import json
import time
import os

app = Flask(__name__)


@app.route('/', methods=['POST'])
def result():
    pc_id = request.form['pc']
    cpu_usage = request.form['cpu_usage']
    mem_usage = request.form['ram_usage']
    last_updated = round(time.time())
    print(pc_id)
    print(cpu_usage)
    print(mem_usage)
    print(request.form['network_usage'])
    if not os.path.isdir(f"/var/www/html/cdn/pcs/{pc_id}"):
        os.makedirs(f"/var/www/html/cdn/pcs/{pc_id}")
    with open(f"/var/www/html/cdn/pcs/{pc_id}/network_graph_data.txt", "w") as file:
        file.write(request.form['network_usage'])
    print(last_updated)
    with open("data.json", "r+") as file:
        j = json.load(file)
        j[pc_id]["cpu_usage"] = float(cpu_usage)
        j[pc_id]["ram_usage"] = float(mem_usage)
        j[pc_id]["last_updated"] = last_updated
        file.seek(0)
        file.truncate(0)
        json.dump(j, file, indent=4)
        found = False
        with open("statistics.csv", "r+") as f:
            if pc_id not in f.read():
                found = True
            if found:
                f.write(f'\n{pc_id};{datetime.datetime.today().strftime("%d/%m/%Y")}')
    return "Call was successful"


@app.route('/check', methods=['POST'])
def pc_id_checker():
    pc_id = request.form['pc']
    with open("data.json", "r+") as file:
        j = json.load(file)
        try:
            j[pc_id]
            return f"Successfully started updater with ID: {pc_id}"
        except KeyError:
            return f'New server detected. Please add this ID to the discord bot by using "--setup {pc_id}" and restart start.py'


@app.route('/version', methods=['GET'])
def version_checker():
    return "0.5"


if __name__ == '__main__':
    app.run()

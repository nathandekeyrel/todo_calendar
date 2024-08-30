import json
from flask import Flask, request, render_template

app = Flask(__name__, static_url_path='', static_folder='static')

with open("other/data/contacts.json", mode="r", encoding="utf-8") as read_file:
    contact_data = json.load(read_file)

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(port=5000)

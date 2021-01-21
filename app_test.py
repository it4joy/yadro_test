import pygal
import json
import time

from flask import Flask
from flask import render_template

app_test = Flask(__name__)
app_test.debug = True

@app_test.route('/')
def index():
    return "Welcome to Pygal Charting Lib!"

@app_test.route('/hello')
def hello():
    #return "Hello, World!"
    with open('tpl.json', 'r') as bar_f:
        data = json.load(bar_f)

    chart = pygal.Bar()
    mark_list = [x['mark'] for x in data]

    chart.add('Annual Mark List', mark_list)
    chart.x_labels = [x['y'] for x in data]

    chart.render_to_file('static/images/bar_chart.svg')
    img_url = 'static/images/bar_chart.svg?cache=' + str(time.time())
    return render_template('app.html', image_url = img_url)

if __name__ == "__main__":
    app_test.run()

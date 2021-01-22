import pygal
import json
import time
import sqlite3

from sqlite3 import Error
from flask import Flask
from flask import render_template

app_test = Flask(__name__)
app_test.debug = True

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("SQLite :: Successfully connected")
    except Error as e:
        print(f"SQLite :: The error '{e}' occured")

    return connection

connection = create_connection('./db/fio_test_db.sqlite')

def exec_query( connection, query, tuple_ = () ):
    cursor = connection.cursor()
    try:
        if len(tuple_) > 1:
            cursor.execute(query, tuple_)
            connection.commit()
        else:
            cursor.execute(query)
            connection.commit()
        print("SQLite :: Query executed successfully")
    except Error as e:
        print(f"SQLite :: The error '{e}' occured")

create_jobs_table = """
CREATE TABLE IF NOT EXISTS fio_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    job_runtime INTEGER,
    read_iops REAL,
    read_iops_min INTEGER,
    read_iops_max INTEGER
);
"""

exec_query(connection, create_jobs_table)

# gets values from json
with open('./tmp/test.out', 'r') as jobs_f:
    job_data = json.load(jobs_f)

    job_name = job_data['jobs'][0]['jobname']
    job_runtime = job_data['jobs'][0]['job_runtime']
    read_iops = job_data['jobs'][0]['read']['iops']
    read_iops_min = job_data['jobs'][0]['read']['iops_min']
    read_iops_max = job_data['jobs'][0]['read']['iops_max']

# inserts job's data into the table
insert_job_data = """
INSERT INTO
    fio_jobs (job_name, job_runtime, read_iops, read_iops_min, read_iops_max)
VALUES
    (?, ?, ?, ?, ?)
"""

job_data_tuple = (job_name, job_runtime, read_iops, read_iops_min, read_iops_max)

exec_query(connection, insert_job_data, job_data_tuple)


@app_test.route('/')
def index():
    #return "Welcome to Pygal Charting Lib!"
    metric_1 = '/latency'
    metric_2 = '/iops'
    metric_3 = '/bw'

    return render_template('index.html', jobName = job_name, jobRuntime = job_runtime, latency = metric_1, iops = metric_2, bw = metric_3)


@app_test.route('/latency')
def hello():
    #return "Hello, World!"
    with open('./tmp/test.out', 'r') as bar_f:
        data = json.load(bar_f)

    chart = pygal.Bar()

    iops_min = data['jobs'][0]['read']['iops_min']
    iops_max = data['jobs'][0]['read']['iops_max']

    chart.add('iops_min', iops_min)
    chart.add('iops_max', iops_max)

    chart.render_to_file('static/images/fio_t_chart.svg')
    svg_url = 'static/images/fio_t_chart.svg?cache=' + str(time.time())
    return render_template('app.html', img_url = svg_url)

if __name__ == "__main__":
    app_test.run()

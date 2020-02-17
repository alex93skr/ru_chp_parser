#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################
#
# - Ru_chp comment sorter
# - by skr
#
#############################################################
import os
import threading
import time
from datetime import datetime

import requests
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='', static_folder='')


#############################################################

class Parser(threading.Thread):

    def __init__(self, year, month, request_comm):
        """Инициализация потока"""

        self.year = year
        self.month = month
        self.request_comm = request_comm
        self.url = None
        self.title = None
        self.arr = []

        threading.Thread.__init__(self)

    def run(self):
        self.make_url()
        self.parsing_html()

        # if check_proxy(self.ip):
        #     lockarr.acquire()
        #     proxy_list_good.append(self.ip)
        #     lockarr.release()

    def make_url(self):
        mon = f'0{str(self.month)}' if self.month < 10 else str(self.month)
        self.url = f'https://ru-chp.livejournal.com/{str(self.year)}/{mon}'

    def parsing_html(self):
        comm_arr = []

        r = requests.get(self.url)
        r.encoding = 'utf-8'
        html = r.text

        self.title = html[html.find("<title>") + 7: html.find("</title>")]

        while " comments" in html:  # совпадение
            moveLeft = html.find(" comments")
            obrez = html

            while obrez[moveLeft - 1: moveLeft] != ">":  # колво комментов
                moveLeft = moveLeft - 1
            else:
                tmp1 = obrez[moveLeft: obrez.find(" ", moveLeft)]

            moveLeft = moveLeft - 40

            while obrez[moveLeft: moveLeft + 5] != ".html":  # описание
                moveLeft = moveLeft - 1
            else:
                tmp3 = obrez[moveLeft + 7: obrez.find("</a>", moveLeft)]

            while obrez[moveLeft: moveLeft + 5] != ".html":  # href
                moveLeft = moveLeft - 1
            else:
                tmp2 = obrez[obrez.find(".com/", moveLeft - 13) + 5: obrez.find(".html", moveLeft)]

            if int(tmp1) > int(self.request_comm):
                comm_arr.append([int(tmp1), tmp2, tmp3])

            html = html[html.find(" comments") + 20: len(html)]  # отрез строки

        self.arr = sorted(comm_arr, reverse=True)


#############################################################


@app.route('/', methods=['GET', 'POST'])
def index():
    appdata = {
        'comm_list': [300, 200, 100, 50, 0],
        # 'year_list': [n for n in range(2020, 2008, -1)],
        'year_list': [n for n in range(datetime.now().year, 2008, -1)],
        'request_comm': None,
        'request_year': None,
        'work_time': 0
    }

    if request.method == 'GET':
        return render_template('ru_chp.html', appdata=appdata)

    if request.method == 'POST':
        try:
            year = int(request.form.get('year'))
            if year in appdata['year_list']:
                appdata['request_year'] = year
            comm = int(request.form.get('comm'))
            if comm in appdata['comm_list']:
                appdata['request_comm'] = comm
        except:
            pass

        # print(appdata['request_year'])
        # print(appdata['request_comm'])

        threads = []

        if not appdata['request_year'] is None and not appdata['request_comm'] is None:

            time_start = time.perf_counter_ns()

            for month in range(1, 13):
                t = Parser(appdata['request_year'], month, appdata['request_comm'])
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            appdata['work_time'] = (time.perf_counter_ns() - time_start) / 1000000000

        return render_template('ru_chp.html', appdata=appdata, threads=threads)


#############################################################

if __name__ == "__main__":

    if "HEROKU" in list(os.environ.keys()):
        app.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
    else:
    # app.run()
        app.run(debug=True)

#############################################################

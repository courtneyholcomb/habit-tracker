import sys
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime, timedelta
import dateutil.parser


class Page(QWebEnginePage):

    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebEnginePage.__init__(self)
        self.html = ""
        self.loadFinished.connect(self.on_page_load)
        self.load(QUrl(url))
        self.app.exec_()

    def on_page_load(self):
        self.html = self.toHtml(self.Callable)
        print('Load finished')

    def Callable(self, html_str):
        self.html = html_str
        self.app.quit()



def get_ritual_classes():#start_dt, end_dt):
    """Get a list of Ritual classes within given date range."""
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(days=3)
    # Get today's weekday, starting with Sunday = 0
    start_date = start_dt.date()
    end_date = end_dt.date()

    num_days = (end_date - start_date).days + 1
    date_range = [(start_date + timedelta(days=i)) for i in range(num_days)]

    all_classes = []
    for input_date in date_range:
        today = datetime.now().date()
        today_wkday = today.isoweekday() % 7
        input_wkday = input_date.isoweekday() % 7

        delta = (input_date - today).days
        input_wk = (today_wkday + delta - input_wkday) / 7

        page = Page(f"https://reserve.ritualhotyoga.com/reserve/index.cfm?action=Reserve.chooseClass&site=2&wk={input_wk}")

        soup = BeautifulSoup(page.html, "html.parser")
        classes = soup.find('td', class_=f"day{input_wkday}").find_all("div", class_="scheduleBlock")
        for clas in classes:
            instructor = clas.find_all("span", class_="scheduleInstruc")[0].text.strip()
            title = clas.find_all("span", class_="scheduleClass")[0].text.strip()
            start = clas.find_all("span", class_="scheduleTime")[0].find(text=True).strip()
            duration = clas.find_all("span", class_="classlength")[0].text.strip()
            # WIP - convert start time from string to approp formatted datetime object
            # end = (str(input_date) + start).strftime() + timedelta(minutes=int(duration[:-4]))
            end = (dateutil.parser.parse(start) + timedelta(minutes=int(duration[:-4]))).strftime("%-I:%M %p")
            all_classes.append({"studio": "Ritual FiDi", "title": title,
                                "instructor": instructor, "start": start, 
                                "end": end, "duration": duration,
                                "address": "49 Kearny St"})
    return all_classes


if __name__ == '__main__':
    get_ritual_classes()

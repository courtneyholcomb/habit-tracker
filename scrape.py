import sys
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from bs4 import BeautifulSoup
import urllib.request


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



def get_love_story_classes():
    page = Page("https://reserve.ritualhotyoga.com/reserve/index.cfm?action=Reserve.chooseClass&site=2")
    soup = BeautifulSoup(page.html, 'lxml')
    classes = soup.find_all('div', class_="columns ClassTimeScheduleItemMobile_separator__T8qcO")
    for clas in classes:
        print(clas.prettify())

if __name__ == '__main__': main()

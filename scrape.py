from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import dateutil.parser


def get_ritual_classes(start_dt, end_dt):
    """Get a list of Ritual classes within given date range."""

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

        info = requests.get(f"https://reserve.ritualhotyoga.com/reserve/index.cfm?action=Reserve.chooseClass&site=1&wk={input_wk}")
        soup = BeautifulSoup(info.content, "lxml")
        classes = soup.find('td', class_=f"day{input_wkday}").find_all("div", class_="scheduleBlock")

        for clas in classes:
            if not "cancelled" in clas.text:
                instructor = clas.find_all("span", class_="scheduleInstruc")[0].text.strip()
                title = clas.find_all("span", class_="scheduleClass")[0].text.strip()
                start = clas.find_all("span", class_="scheduleTime")[0].find(text=True).strip()
                duration = clas.find_all("span", class_="classlength")[0].text.strip()
                end = (dateutil.parser.parse(start) + timedelta(minutes=int(duration[:-4]))).strftime("%-I:%M %p")
                all_classes.append({"studio": "Ritual", "title": title,
                                    "instructor": instructor, "start": start, 
                                    "end": end, "duration": duration,
                                    "address": "49 Kearny St"})

    return all_classes


if __name__ == '__main__':
    get_ritual_classes()

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import dateutil.parser
from tzlocal import get_localzone
import pytz




def get_ritual_classes(start, end):
    """Get a list of Ritual classes within given date range."""

    pst = pytz.timezone('US/Pacific')
    local_tz = get_localzone()
    input_date = start.astimezone(pst).date()

    # Get today's weekday and input's weekday, starting with Sunday = 0
    # Use to create correct request URL & find correct html block
    today = datetime.now().astimezone(local_tz).date()
    today_wkday = today.isoweekday() % 7
    input_wkday = input_date.isoweekday() % 7
    delta = (input_date - today).days
    input_wk = int((today_wkday + delta - input_wkday) / 7)

    locations = [{"location_num": 1, "name": "Ritual SoMa",
                  "address": "1122 Howard St, SF"},
                 {"location_num": 2, "name": "Ritual FiDi",
                  "address": "49 Kearny St, SF"}]

    all_classes = []
    for location in locations:
        info = requests.get("https://reserve.ritualhotyoga.com/reserve/" \
                            "index.cfm?action=Reserve.chooseClass&" \
                            f"site={location['location_num']}&wk={input_wk}")
        soup = BeautifulSoup(info.content, "lxml")
        day_tds = soup.find('td', class_=f"day{input_wkday}")
        schedule_blocks = day_tds.find_all("div", class_="scheduleBlock")

        for clas in schedule_blocks:

            # Eliminate canceled classes
            if not "cancelled" in clas.text:
                # Get start time & duration from scraped info
                start_block = clas.find_all("span", class_="scheduleTime")[0]
                clas_start = dateutil.parser.parse(input_date.strftime("%m/%d/%Y") + " " +
                             start_block.find(text=True).strip()).astimezone(pst)
                print(f"clas_start scrape.py={clas_start}")
                duration_block = clas.find_all("span", class_="classlength")[0]
                duration = int(duration_block.text.strip()[:-4])
                duration_td = timedelta(minutes=duration)

                # Calculate end time
                clas_end = clas_start + duration_td
                print(f"clas_end scrape.py={clas_end}")

                # Get instructor & title text
                instructor = clas.find_all("span", class_="scheduleInstruc")[0]\
                             .text.strip()
                title = clas.find_all("span", class_="scheduleClass")[0] \
                        .text.strip()

            if clas_start >= start and clas_end <= end:
                # Add each class info to list
                all_classes.append({"studio": location["name"], "title": title,
                    "instructor": instructor, "start": clas_start,
                    "end": clas_end, "duration": duration,
                    "address": location["address"]})

    return all_classes


if __name__ == '__main__':
    get_ritual_classes()

from datetime import datetime, timedelta
from app.emailDataBaseHandler import *

def scrape_Emails():
    global FROM
    global TO
    global LAST_SCRAPED_DAY
    LAST_SCRAPED_DAY = read_last_Scraped_date()
    if not LAST_SCRAPED_DAY:
        LAST_SCRAPED_DAY = FROM
    start_date = datetime.strptime(LAST_SCRAPED_DAY, "%Y/%m/%d")
    end_date = datetime.strptime(TO, "%Y/%m/%d")
    current_date = start_date
    while current_date <= end_date:
        CURRENT_DAY = current_date.strftime("%Y/%m/%d")
        NEXT_DAY = (current_date + timedelta(days=1)).strftime("%Y/%m/%d") if current_date + timedelta(days=1) <= end_date else "N/A"
        update_DB_On_Single_Date(from_date=CURRENT_DAY, to_date=NEXT_DAY)
        current_date += timedelta(days=1)
        write_last_Scraped_date(CURRENT_DAY)


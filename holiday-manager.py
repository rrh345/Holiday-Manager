# %%
from datetime import datetime, date, timedelta
import json
from bs4 import BeautifulSoup
import requests

class Holiday:
    def __init__(self, name, date):
        self.name = name
        # only accept datetime objects as date
        self.date = datetime.strptime(date, "%Y-%m-%d")
    
    def __str__(self):
        return f"{self.name} ({self.date})"

class HolidayList:
    "HolidayList class"
    def __init__(self):
        self.innerHolidays = []

    def addHoliday(self, holidayObj):
        if isinstance(holidayObj, Holiday):
            # Make sure holidayObj is an Holiday Object by checking the type. Add to innerHolidays
            self.innerHolidays.append(holidayObj)
            print(f"Success:\n{holidayObj} has been added to holiday list.")

    def findHoliday(self, HolidayName, Date):
        for holiday in self.innerHolidays:
            # Find and return Holiday in innerHolidays
            if holiday.name == HolidayName and holiday.date == Date:
                return holiday
            else:
                print(f"{holiday} is not in list.")

    def removeHoliday(self, HolidayName):
        for holiday in self.innerHolidays:
            # Find Holiday in innerHolidays by searching the name and date combination
            if holiday.name == HolidayName:
                # remove the Holiday from innerHolidays, and inform user you deleted the holiday
                self.innerHolidays.remove(holiday)
                print(f"Success:\n{holiday} has been removed from the holiday list.")
                break

    def read_json(self, filelocation):
        # Read in things from json file location and add holidays to innerHolidays
        with open(filelocation, "r") as jsonfile:
            data = json.load(jsonfile)
            for i in range(len(data["holidays"])):
                holiday = Holiday(data["holidays"][i]["name"], data["holidays"][i]["date"][0:10])
                HolidayList.addHoliday(self, holiday)
        jsonfile.close()

    def save_to_json(self, filelocation):
        json_list = []
        json_dict = {"holidays": json_list}
        # Write out json file to selected file.
        with open(filelocation, "w") as jsonfile:
            for holiday in self.innerHolidays:
                holiday.date = str(holiday.date)
                json_list.append(holiday.__dict__)
            json.dump(json_dict, jsonfile, indent=3)
        jsonfile.close()

    def scrapeHolidays(self):
        def getHTML(url):
            response = requests.get(url)
            return response.text
        # Scrape holidays from 2020-2024
        for year in range(2020,2025):
            year = str(year)
            html = getHTML("https://www.timeanddate.com/calendar/custom.html?year=" + year +"&country=1&cols=3&df=1&hol=33554809")
            soup = BeautifulSoup(html,'html.parser')
            holiday_data = soup.find('table', attrs = {'class':'cht lpad'}).find('tbody')
            for row in holiday_data:
                items = row.find_all('tr')
                holiday_dict = {}
                holiday_dict['name'] = row.find('td').find_next('td').string
                holiday_dict['date'] = f"{row.find('td').string}, {year}"
                # Check to see if name and date of holiday is in innerHolidays array. If it is, don't add it to list
                if holiday_dict['name'] in self.innerHolidays and holiday_dict['date'] in self.innerHolidays:
                    continue
                else:
                    # converting date to correct format
                    holiday_dict['date'] = str(datetime.strptime(holiday_dict['date'], "%b %d, %Y"))[0:10]
                    # add holiday to list
                    holiday = Holiday(holiday_dict["name"], holiday_dict["date"])
                    HolidayList.addHoliday(self, holiday)
    
    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        return len(self.innerHolidays)

    def filter_holidays_by_week(self, year, week_number):
        # Use a Lambda function to filter by week number and cast results as list
        global filter_by_week
        filter_by_week = filter(lambda holiday:datetime.strftime(holiday.date, "%U") == week_number
            and datetime.strftime(holiday.date, "%Y") == year, self.innerHolidays)
        filter_by_week = list(filter_by_week)
        return(filter_by_week)
    
    def displayHolidaysInWeek(self, year, week_number):
        # Print list of holidays within a week as a parameter
        HolidayList.filter_holidays_by_week(self, year, week_number)
        for row in range(len(filter_by_week)):
            print(filter_by_week[row])
    
    def getWeather_currentweek(self):
        # Query API for weather in current week
        url = "https://community-open-weather-map.p.rapidapi.com/forecast/daily"
        querystring = {"q":"new york,us","lat":"41","lon":"74","cnt":"7","units":"imperial"}
        headers = {'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
            'x-rapidapi-key': "1e19830f3bmshf56abb61a6e9168p189818jsnf035a12afc26"}
        weather = requests.request("GET", url, headers=headers, params=querystring)
        weather_dict = weather.json()
        current_week_weather = []
        # return weather string for current week
        for i in range(0,7):
            daily_weather = (weather_dict["list"][i]["weather"][0]["main"])
            current_week_weather.append(daily_weather)
        return(current_week_weather)
    
    def viewCurrentWeek(self):
        # Create list of dates for current week
        today = date.today()
        this_week = []
        for i in range(0,7):
            this_week.append(str(today + timedelta(days=i)))
        print(this_week)
        # Use the Datetime Module to look up current week and year
        current_year = datetime.strftime(today, "%Y")
        current_week = datetime.strftime(today, "%U")
        # Use your filter_holidays_by_week function to get the list of holidays for the current week and year
        HolidayList.filter_holidays_by_week(self, current_year, current_week)
        # Use your displayHolidaysInWeek function to display the holidays in the week
        HolidayList.displayHolidaysInWeek(self, current_year, current_week)
        # Ask user if they want to get the weather
        while True:
            weather_yn  = str(input("Would you like to see this week's weather? [y/n]"))
            # If yes, use your getWeather function and display results
            if weather_yn == "y":
                current_week_weather = HolidayList.getWeather_currentweek(self)
                current_weather_date = {}
                for i in range(0,7):
                    current_weather_date['date'] = this_week[i]
                    current_weather_date['weather'] = current_week_weather[i]
                    print(current_weather_date)
                False
                break
            elif weather_yn == "n":
                False
                break
            else:
                print("I didn't understand. Try again.")

def main():
    # 1. Initialize HolidayList Object
    holidaylist = HolidayList()
    # 2. Load JSON file via HolidayList read_json function
    holidaylist.read_json("holidays.json")
    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    holidaylist.scrapeHolidays()
    # 4. Create while loop for user to keep adding or working with the Calender

    #Start Up
    print(f"""
    Holiday Management
    ===================
    There are {holidaylist.numHolidays()} holidays stored in the system.
    """)

    #Main Menu
    print("""
    Holiday Menu
    ================
    1. Add a Holiday
    2. Remove a Holiday
    3. Save Holiday List
    4. View Holidays
    5. Exit
    """)

    exit = "n"

    def holiday_name_date():
        global holiday_name, holiday_date
        while True:
            holiday_name = str(input("Holiday: "))
            holiday_date = str(input("Date [yyyy-mm-dd]: "))
            if len(holiday_date) == 10 and holiday_date[0:3].isnumeric and holiday_date[4] == "-"\
                and holiday_date[5:6].isnumeric and holiday_date[7] == "-" and holiday_date[8:9].isnumeric:
                False
                return holiday_name, holiday_date
            else:
                print("Error:\nInvalid date. Please try again.")
                continue

    while exit != "y":
        menu_selection = int(input("Enter 1 for Add a Holiday.\nEnter 2 for Remove a Holiday.\
            \nEnter 3 for Save Holiday List.\nEnter 4 for View Holidays.\nEnter 5 for Exit.\n"))
        if menu_selection == 1:
            print("Add a Holiday\n=============")
            holiday_name_date()
            print(f"Holiday: {holiday_name}")
            print(f"Date: {holiday_date}\n")
            holiday1 = Holiday(holiday_name, holiday_date)
            holidaylist.addHoliday(holiday1)
        elif menu_selection == 2:
            print("Remove a Holiday\n================")
            holiday_name_date()
            print(f"Holiday Name: {holiday_name}")
            holidaylist.removeHoliday(holiday_name, holiday_date)
        elif menu_selection == 3:
            print("Saving Holiday List\n====================")
            save= str(input("Are you sure you want to save your changes? [y/n]: "))
            print(f"Are you sure you want to save your changes? [y/n]: {save}\n")
            if save == "y":
                holidaylist.save_to_json("holidays-new.json")
                print("Changes saved.")
            elif save == "n":
                print("Changes not saved.")
            else:
                print(f"Error: {save} is not an option\nSave your changes? [y/n]")
        elif menu_selection == 4:
            print("View Holidays\n=================")
            year = int(input("Which year?: "))
            year = str(year)
            print(f"Which year?: {year}")
            week = input("Which week? #[00-52, Leave blank for the current week]: ")
            week = str(week)
            print(f"Which week? #[00-52, Leave blank for the current week]: {week}")
            while True:
                if week == "":
                    print(f"These are the holidays for this week:")
                    holidaylist.viewCurrentWeek()
                    False
                else:
                    print(f"These are the holidays for year {year}, week {week}:")
                    holidaylist.displayHolidaysInWeek(year, week)
                    False
                    break
        elif menu_selection == 5:
            print("Exit\n=====\nAny unsaved changes will be lost.")
            exit = str(input("Are you sure you want to exit? [y/n]"))
            print(f"Are you sure you want to exit? [y/n]: {exit}\n")
            if exit == "y":
                print("Goodbye!")
                break
            elif exit == "n":
                print("Okay. Not exiting.")
            else:
                print(f"Error: {exit} is not an option\nAre you sure you want to exit? [y/n]")
        else:
            print("Please select a menu option from 1 through 5.")

if __name__ == "__main__":
    main();




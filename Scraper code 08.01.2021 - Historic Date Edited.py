#!/usr/bin/env python
# coding: utf-8

# In[18]:


# 3rd Party, Keep here if turning into one file
import re as reg_ex
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from datetime import datetime

#Headless or Background mode
chromeOptions = Options()
chromeOptions.binary_location ="/opt/google/chrome/google-chrome"
chromeOptions.add_argument("--headless")
chromeOptions.add_argument("window-size=1400,1500")
chromeOptions.add_argument("--disable-gpu")
chromeOptions.add_argument("--no-sandbox")
chromeOptions.add_argument("start-maximized")
chromeOptions.add_argument("enable-automation")
chromeOptions.add_argument("--disable-infobars")
chromeOptions.add_argument("--disable-dev-shm-usage")

class TimeStamp:
    def timestamp():
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        return timestampStr

class WebDriver:
    """Responsible for handling the webdriver and giving bs4 formatted html"""

    print("class WebDriver "+ TimeStamp.timestamp()) #Elina 08-12-2020
    
    def __init__(self, new_domain):
        self.domain = new_domain
        self.current_page_url = None
        self.current_page = None
        self.is_error_page = False
        self.web_driver = None

        try:
            self.web_driver = webdriver.Chrome(executable_path = "/usr/bin/chromedriver", options = chromeOptions)  # options=chrome_options
        except Exception as error:
            print("\n \nThe webdriver could not be started - {error}")

    def move_to_page(self, target_url):
        """Swaps the webdriver to the specified url"""
        
        print("def move_to_page (Swaps the webdriver to the specified url) "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        self.is_error_page = False
        try:
            self.web_driver.get(target_url)
        except Exception as error:
            print("Could not reach web page url: {target_url}\nError Message :{error}")
            self.is_error_page = True

        self.current_page_url = target_url
        sleep(15)  # Give html time to load
        self.set_web_page_html()
        self.handle_403_error(target_url)
        self.check_for_invalid_page()

    def set_web_page_html(self):
        """Turns a web drivers source into soup"""
        print("def set_web_page_html "+ TimeStamp.timestamp()) #Elina 08-12-2020
        self.current_page = BeautifulSoup(self.web_driver.page_source, features="html.parser")

    def handle_403_error(self, target_url):
        """Recursive method which waits a given sleep_time of seconds
        after encountering access denied error"""
        
        print("Start handle_403_error "+ TimeStamp.timestamp()) #Elina 08-12-2020
        sleep_time = 600
        new_url = target_url
        
        if self.is_access_denied():
            print("check access denied true"+ TimeStamp.timestamp()) #Elina 08-12-2020
            print("Access was denied from the website - driver will try again in {sleep_time} seconds")
            self.restart_driver(sleep_time)
            self.web_driver.get(target_url)
            self.refresh_driver(5)
            self.set_web_page_html()
            if self.is_access_denied():
                self.handle_403_error(new_url)
        else:
            print("check access denied false "+ TimeStamp.timestamp()) #Elina 08-12-2020
            return

    def is_access_denied(self):
        """Checks if 403 error is present"""
        if self.current_page.find("div", {"id": "main-frame-error"}):
            return True #if self.current_page.find("div", {"id": "main-frame-error"}) 
        else: return False

    def check_for_invalid_page(self):
        print("def check_for_invalid_page "+ TimeStamp.timestamp()) #Elina 08-12-2020
        possible_errors = [self.page_not_found(),
                           self.list_did_not_load(),
                           self.flight_not_found(),
                           self.no_flights_found()]
        if any(possible_errors):
            self.is_error_page = True

    def page_not_found(self):
        """Checks if page does not load"""
        print("def page_not_found "+ TimeStamp.timestamp()) #Elina 08-12-2020
        couldnt_get_page = "Unfortunately, we couldn't find the page you were looking for. Please try again."
        page_not_found = self.current_page.find('div', text=reg_ex.compile(rf"{couldnt_get_page}"))
        return True if page_not_found else False

    def list_did_not_load(self) -> bool:
        """Checks if the page is not displaying the list and returns"""
        print("def list_did_not_load "+ TimeStamp.timestamp()) #Elina 08-12-2020
        list_not_load_text = "The list couldn't be loaded. Please try again"
        if self.current_page.find_all('div', text=reg_ex.compile(list_not_load_text)):
            print("list not load true "+ TimeStamp.timestamp()) #Elina 08-12-2020
            return True
        else:
            print("list not load false "+ TimeStamp.timestamp()) #Elina 08-12-2020
            return False

    def flight_not_found(self):
        """Some record urls do not have a record page"""
        
        print("def flight_not_found "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        couldnt_get_flight = "Unfortunately we couldn't find this flight, please try a different flight number."
        flight_not_found = self.current_page.find('strong', text=reg_ex.compile(rf"{couldnt_get_flight}"))
        return True if flight_not_found else False

    def no_flights_found(self):
        """Checks if the page is not displaying and flights and returns"""
        
        print("def no_flights_found "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        no_flights_text = 'No further flights found, please select another date'
        if self.current_page.find_all('span', text=reg_ex.compile(no_flights_text)):
            print("no_flights_found true "+ TimeStamp.timestamp()) #Elina 08-12-2020
            return True
        else:
            print("no_flights_found false "+ TimeStamp.timestamp()) #Elina 08-12-2020
            return False

    def wait_for_class_element_to_load(self, target_class):
        print("def wait_for_class_element_to_load "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        try:
            WebDriverWait(self.web_driver, 15).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, target_class))
            )
        except TimeoutException:
            print("Target element took too long to load - Moving on")

    def new_driver(self):
        print("def new_driver "+ TimeStamp.timestamp()) #Elina 08-12-2020
        self.web_driver = webdriver.Chrome()

    def stop_driver(self):
        print("def stop_driver "+ TimeStamp.timestamp()) #Elina 08-12-2020
        try:
            self.web_driver.quit()
        except Exception as error:
            print("There was an issue closing the webdriver - {error}")

    def restart_driver(self, sleep_time):
        print("def restart_driver "+ TimeStamp.timestamp()) #Elina 08-12-2020
        self.stop_driver()
        sleep(sleep_time)
        self.new_driver()

    def refresh_driver(self, sleep_time):
        print("def refresh_driver "+ TimeStamp.timestamp()) #Elina 08-12-2020
        sleep(sleep_time)
        self.web_driver.refresh()
        sleep(5)


# In[19]:


class FlightRecord:
    """Responsible for storing a single flight records data"""
    
    print("class FlightRecord "+ TimeStamp.timestamp()) #Elina 08-12-2020
    
    def __init__(self, new_record_date,
                 new_flight_code,
                 new_flight_type,

                 new_origin, new_destination,

                 new_scheduled_departure, new_scheduled_departure_test,
                 new_actual_departure,
                 new_departure_status, 

                 new_scheduled_arrival, new_actual_arrival,
                 new_arrival_status,

                 new_duration,
                 new_distance,
                 new_speed,
                 new_airline_name,
                 new_plane_model,
                 new_seat_numbers,
                 new_flight_status):
        
        print("class FlightRecord def __init__ "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        self.date = new_record_date
        self.flight_code = new_flight_code
        self.flight_type = new_flight_type

        self.origin = new_origin
        self.destination = new_destination

        self.scheduled_departure = new_scheduled_departure
        self.scheduled_departure_test = new_scheduled_departure_test
        self.actual_departure = new_actual_departure
        self.departure_status = new_departure_status

        self.scheduled_arrival = new_scheduled_arrival
        self.actual_arrival = new_actual_arrival
        self.arrival_status = new_arrival_status

        self.duration = new_duration
        self.distance = new_distance
        self.speed_kph = new_speed

        self.airline_name = new_airline_name
        self.plane_model = new_plane_model
        self.seat_numbers = new_seat_numbers
        self.flight_status = new_flight_status

    def __str__(self) -> str:
        
        print("class FlightRecord def __str__ "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        all_values = ""
        for _, value in self.__dict__.items():
            all_values += f"{value} "
        return all_values + "\n"


# In[ ]:


# 3rd Party, Keep here if turning into one file
import re as reg_ex
from datetime import datetime


class FlightScraper:
    
    print("class FlightScraper "+ TimeStamp.timestamp()) #Elina 08-12-2020
    
    def __init__(self, new_date, new_web_page):
        
        print("class FlightScraper def __init__ "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        self.flight_date = new_date
        self.web_page = new_web_page
        self.missing_field = "N/A"

    def flight_record_factory(self, new_record_url, new_flight_type):
        """Responsible for creating a flight record and its attributes"""
        
        print("def flight_record_factory "+ TimeStamp.timestamp()) #Elina 08-12-2020

        record_date = self.flight_date
        flight_code = new_record_url.split("/")[-3]
        flight_type = new_flight_type

        origin = self.get_origin()
        destination = self.get_destination()

        scheduled_departure = self.get_scheduled_departure()
        scheduled_departure_test = self.get_scheduled_departure_test()
        scheduled_arrival = self.get_scheduled_arrival()
        

        flight_status = self.get_flight_status()

        plane_model = self.get_plane_model() if self.has_plane_model() else self.missing_field
        seat_numbers = self.get_seat_numbers() if self.has_seat_numbers() else self.missing_field

        airline_name = self.get_airline_name() if self.has_airline_name() else self.missing_field

        duration = self.get_duration() if self.has_duration() else self.missing_field
        distance = self.get_distance() if self.has_distance() else self.missing_field

        speed_kph = self.get_speed(distance, duration)

        actual_arrival = self.get_actual_arrival() if self.has_actual_arrival() else self.missing_field
        actual_departure = self.get_actual_departure() if self.has_actual_departure() else self.missing_field

        departure_status = self.create_status(scheduled_departure, actual_departure)
        arrival_status = self.create_status(scheduled_arrival, actual_arrival)

        return FlightRecord(record_date, flight_code, flight_type,
                            origin, destination,
                            scheduled_departure, scheduled_departure_test, actual_departure, departure_status,
                            scheduled_arrival, actual_arrival, arrival_status,
                            duration, distance, speed_kph,
                            airline_name, plane_model, seat_numbers, flight_status)

    def temp_record_factory(self, new_record_url, new_flight_type):
        """Responsible for creating a flight record that has an error page"""
        
        print("def temp_record_factory "+ TimeStamp.timestamp()) #Elina 08-12-2020
        print("temp_record_factory, new record url: " + new_record_url) #Elina 08-12-2020
        
        record_date = self.flight_date
        flight_code = new_record_url.split("/")[-3]
        flight_type = new_flight_type

        return FlightRecord(record_date, flight_code, flight_type,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field,
                            self.missing_field, self.missing_field)

    def has_airline_name(self):
        return True if self.web_page.find('a', href=reg_ex.compile("/airline/")) else False

    def has_plane_model(self):
        return True if self.web_page.find('h4', text=reg_ex.compile("Plane")) else False

    def has_actual_arrival(self):
        arrival_actual = self.web_page.find('span', text=reg_ex.compile("Actual Arrival:"))
        return True if arrival_actual else False

    def has_actual_departure(self):
        departure_actual = self.web_page.find('span', text=reg_ex.compile("Actual Departure:"))
        return True if departure_actual else False

    def has_seat_numbers(self):
        seat_config_txt = self.web_page.find("span", text=reg_ex.compile("Seat Configuration:"))
        return True if seat_config_txt else False

    def get_seat_numbers(self):
        print("def get_seat_numbers "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        seat_config_txt = self.web_page.find("span", text=reg_ex.compile("Seat Configuration:"))
        parent_element = seat_config_txt.find_parent("div")
        seat_number_element = parent_element.find("p")
        seat_numbers = self.get_element_text(seat_number_element).split(" ")[0]
        return seat_numbers

    def get_flight_status(self):
        print("def get_flight_status "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        all_flight_stats = self.web_page.find_all("span", {"class": "badge"})
        if all_flight_stats:
            current_flight_status = self.get_element_text(all_flight_stats[0])
            print("get flight status control true "+ TimeStamp.timestamp())
            return current_flight_status
        else: print("get flight status control false "+ TimeStamp.timestamp())

    def get_airline_name(self):
        airline_link_title = self.web_page.find('a', href=reg_ex.compile("/airline/"))
        return airline_link_title.get("title").replace('All Details for', "")

    def get_plane_model(self):
        plane_model_link = self.web_page.find('a', href=reg_ex.compile("/model/"))
        return self.get_element_text(plane_model_link)

    def get_origin(self):
        airport_links = self.web_page.find_all('a', href=reg_ex.compile("/airport/"))
        
        print("def get_origin "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        if airport_links:
            origin_airport = self.get_element_text(airport_links[0])
            print("get origin control true " + TimeStamp.timestamp())
            return origin_airport
        else: print("get origin control false " + TimeStamp.timestamp())

    def get_destination(self):
        airport_links = self.web_page.find_all('a', href=reg_ex.compile("/airport/"))
        print("def get_destination "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        if airport_links:
            destination_airport = self.get_element_text(airport_links[1])
            print("destination controls true " + TimeStamp.timestamp())
            return destination_airport
        else: print("destination controls false " + TimeStamp.timestamp())
        #destination_airport = self.get_element_text(airport_links[1])
        #return destination_airport

    def get_scheduled_departure(self):
        print("def get_scheduled_departure "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        flight_data_boxes = self.web_page.find_all("div", {"class": "col-12 col-lg-5 detail-box"})
        if flight_data_boxes:
            departure_box = flight_data_boxes[0]
            flight_data = departure_box.find_all("div", {"class": "p-2"})
            scheduled_departure_box = flight_data[1]
            scheduled_departure = scheduled_departure_box.find("span", {"class": "text-nowrap"})
            print("get scheduled departure true " + TimeStamp.timestamp())
            return self.get_element_text(scheduled_departure)
        else: print("get scheduled departure false " + TimeStamp.timestamp())
            
    def get_scheduled_departure_test(self):
        print("def get_scheduled_departure "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        flight_data_boxes_test = self.web_page.find_all("div", {"class": "col-12 col-lg-5 detail-box"})
        if flight_data_boxes_test:
            departure_box_test = flight_data_boxes_test[0]
            flight_data_test = departure_box_test.find_all("div", {"class": "p-2"})
            scheduled_departure_box_test = flight_data_test[1]
            scheduled_departure_test = scheduled_departure_box_test.find("span", {"class": "text-primary"})
            #print("get scheduled departure true " + TimeStamp.timestamp())
            return self.get_element_text(scheduled_departure_test)
        #else: print("get scheduled departure false " + TimeStamp.timestamp())

    def get_actual_departure(self):
        print("def get_actual_departure "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        flight_data_boxes = self.web_page.find_all("div", {"class": "col-12 col-lg-5 detail-box"})
        departure_box = flight_data_boxes[0]
        flight_data = departure_box.find_all("div", {"class": "p-2"})
        actual_departure_box = flight_data[2]
        actual_departure = actual_departure_box.find("span", {"class": "text-nowrap"})
        return self.get_element_text(actual_departure)

    def get_scheduled_arrival(self):
        print("def get_scheduled_arrival "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        flight_data_boxes = self.web_page.find_all("div", {"class": "col-12 col-lg-5 detail-box"})
        if flight_data_boxes:
            arrival_box = flight_data_boxes[1]
            flight_data = arrival_box.find_all("div", {"class": "p-2"})
            scheduled_arrival_box = flight_data[1]
            scheduled_arrival = scheduled_arrival_box.find("span", {"class": "text-nowrap"})
            print("get scheduled arrival true " + TimeStamp.timestamp())
            return self.get_element_text(scheduled_arrival)
        else: print("get scheduled arrival false " + TimeStamp.timestamp())

    def get_actual_arrival(self):
        print("def get_actual_arrival "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        flight_data_boxes = self.web_page.find_all("div", {"class": "col-12 col-lg-5 detail-box"})
        arrival_box = flight_data_boxes[1]
        flight_data = arrival_box.find_all("div", {"class": "p-2"})
        actual_arrival_box = flight_data[2]
        actual_arrival = actual_arrival_box.find("span", {"class": "text-nowrap"})
        return self.get_element_text(actual_arrival)

    def has_callsign_info(self):
        #print("def has_callsign_info "+TimeStamp.timestamp()) #Elina 08-12-2020
        callsign_header = self.web_page.find('span', text=reg_ex.compile("Callsign:"))
        return True if callsign_header else False

    def has_duration(self):
        #print("def has_duration "+TimeStamp.timestamp()) #Elina 08-12-2020
        return True if self.web_page.find("span", {"class": "fas fa-clock"}) else False

    def has_distance(self):
        return True if self.web_page.find("span", {"class": "fas fa-ruler"}) else False

    def get_duration(self):
        duration_index = 2 if self.has_callsign_info() else 0
        duration_and_distance_box = self.web_page.find("div", {"class": "col-12 col-lg-2 my-auto"})
        duration_and_distance_elements = duration_and_distance_box.find_all("span", {"class": "text-nowrap"})
        return self.get_element_text(duration_and_distance_elements[duration_index])

    def get_distance(self):
        """Multiple ifs required here, because
        there are no unique ids for target elements, need to use
        index numbers which change when elements are missing"""
        # Callsign info increases index by 2 values
        # Duration info increases index by 1 value
        if self.has_callsign_info() and self.has_duration():
            distance_index = 3
        elif self.has_callsign_info() is True and self.has_duration() is False:
            distance_index = 2
        elif self.has_callsign_info() is False and self.has_duration() is True:
            distance_index = 1
        else:
            distance_index = 0

        duration_and_distance_box = self.web_page.find("div", {"class": "col-12 col-lg-2 my-auto"})
        duration_and_distance_elements = duration_and_distance_box.find_all("span", {"class": "text-nowrap"})
        return self.get_element_text(duration_and_distance_elements[distance_index])

    def get_speed(self, new_distance, new_time):
        if self.missing_field in new_time or self.missing_field in new_distance:
            return self.missing_field

        unwanted_chars = ["k", "m", "i", "(", ")", "[", "]", ","]
        km_and_miles = "".join([char for char in new_distance if char not in unwanted_chars])
        distance_km = int(km_and_miles.split(" ")[0])
        hours_or_minutes = new_time.split(" ")
        hours = 0

        for a_time_value in hours_or_minutes:
            if "h" in a_time_value:
                a_time_value = int(a_time_value.replace("h", ""))
            elif "m" in a_time_value:
                a_time_value = int(a_time_value.replace("m", "")) / 60
            hours += a_time_value

        return str(round(distance_km / hours))

    def create_status(self, scheduled_time, actual_time): 
        print("def create_status for flights "+ TimeStamp.timestamp()) #Elina 08-12-2020
        
        if self.missing_field in actual_time:
            return self.missing_field

        scheduled = scheduled_time.split(" ")[0].split(":")
        actual = actual_time.split(" ")[0].split(":")

        now = datetime.now()
        scheduled_datetime = now.replace(hour=int(scheduled[0]), minute=int(scheduled[1]))
        actual_datetime = now.replace(hour=int(actual[0]), minute=int(actual[1]))

        if scheduled_datetime == actual_datetime:
            return "On Time"
        elif scheduled_datetime > actual_datetime:
            time_calculation = scheduled_datetime - actual_datetime
            late_or_early = "Early"
        else:
            time_calculation = actual_datetime - scheduled_datetime
            late_or_early = "Late"

        time = str(time_calculation)
        return f"{time} {late_or_early}"

    @staticmethod
    def get_element_text(element):
        """Gets the text of an html element tag and removes extra whitespace"""
        print("def get_element_text " + TimeStamp.timestamp()) #Elina 08-12-2020
        return " ".join(element.get_text().split())


# In[ ]:


# 3rd Party, Keep here if turning into one file
import re as reg_ex
from datetime import datetime, timedelta


class AirportScraper:
    """Responsible for navigating an airport and
    finding its flight record urls"""
    
    print("class AirportScraper " + TimeStamp.timestamp()) #Elina 08-12-2020

    def __init__(self, new_target_date: datetime):
        self.web_page = None
        self.target_date = new_target_date
        self.all_temp_flight_records = []
        self.previous_page_of_records = []
        self.record_set_completed = False
        self.target_day_has_started = False

    def set_page(self, new_web_page):
        self.web_page = new_web_page
 
    def get_page_records(self, record_type):
        print("def get_page_records " + TimeStamp.timestamp()) #Elina 08-12-2020
        self.target_day_has_started = False  # Reset to false

        duplicated_elements = self.web_page.find_all('a', href=reg_ex.compile("/flight_details/"))
        record_urls = [a_element.get("href") for a_element in duplicated_elements[::2]]
        
        if self.previous_page_of_records:
            if self.is_duplicated_data_page(record_urls):
                self.record_set_completed = True
                return

        self.previous_page_of_records = record_urls

        for a_record_url in record_urls:
            print(TimeStamp.timestamp()+"get page record, a record url: "+ a_record_url) #Elina 08-12-2020
            self.loop_through_new_records(a_record_url, record_type)
            if self.record_set_completed is True:
                print("record_set_completed "+ TimeStamp.timestamp()) #Elina 08-12-2020
                return

    def loop_through_new_records(self, record_url, record_type):
        print("def loop_through_new_records " + TimeStamp.timestamp()) #Elina 08-12-2020
        date_attr = record_url.split("/")[-1].split("-")
        record_date = datetime(int(date_attr[0]), int(date_attr[1]), int(date_attr[2]))

        if self.target_day_has_started and record_date.date() < self.target_date.date():
            # If the target day has started and the records date started at an earlier day
            new_temp_record = TempFlightRecord(record_type, record_url)
            self.all_temp_flight_records.append(new_temp_record)

        elif record_date.date() == self.target_date.date():
            # IF record date matches the date we want to scrape
            self.target_day_has_started = True
            new_temp_record = TempFlightRecord(record_type, record_url)
            self.all_temp_flight_records.append(new_temp_record)

        elif record_date.date() > self.target_date.date():
            # IF record date is day after target date we want to scrape
            self.record_set_completed = True

    def is_duplicated_data_page(self, new_record_set):
        """Checks if page is a complete duplicate"""
        print("def is_duplicated_data_page " + TimeStamp.timestamp()) #Elina 08-12-2020
        previous_page_links = [old_record for old_record in self.previous_page_of_records]

        def is_duplicate_record(new_record):
            return True if new_record in previous_page_links else False

        all_is_duplicates = [is_duplicate_record(a_record) for a_record in new_record_set]
        return True if all(all_is_duplicates) else False

    def get_later_flights_link(self):
        """finds the later flights link"""
        print("def get_later_flights_link " + TimeStamp.timestamp()) #Elina 08-12-2020
        try:
            next_link_element = self.web_page.find('a', text=reg_ex.compile("Later Flights"))
            print("next link element: "+ TimeStamp.timestamp()) #Elina 08-12-2020
            return next_link_element.get("href")
        except AttributeError:
            print("Could not Find later flights link, driver will retry")
            return None

    @staticmethod
    def date_string(date_object):
        return date_object.strftime('%Y-%m-%d')  # YYYY-MM-DD


class TempFlightRecord:
    """Temporary object for storing a record before scraping
    all of its attributes on its individual page"""
    print("class TempFlightRecord " + TimeStamp.timestamp()) #Elina 08-12-2020
    
    def __init__(self, new_flight_type, new_url_link):
        self.flight_type = new_flight_type
        self.url = new_url_link
        print("def init of TempFlightRecord: "+ self.url + TimeStamp.timestamp()) #Elina 08-12-2020

# In[ ]:


class CountryScraper:
    """Responsible for getting a countries list of airport codes
    and applying the airport filter defined in the client code"""
    
    print("class CountryScraper " + TimeStamp.timestamp()) #Elina 08-12-2020
    
    def __init__(self, new_name, new_web_page, airports_to_scrape=None):
        self.name = new_name
        self.web_page = new_web_page
        self.all_airport_names = airports_to_scrape
        self.all_airport_codes = []  # format = "airport_name/ICAO"

    def get_correct_airports(self):
        self.get_all_airport_codes()
        self.filter_airports()

    def get_all_airport_codes(self):
        """Gets airport codes on country page.
        Follows format of: airport_name/ICAO"""

        target_class = {"class": "d-inline-block"}
        airport_elements = self.web_page.find_all("a", target_class)

        for an_airport_element in airport_elements:
            an_airport_code = f"{an_airport_element.get('href')}"
            self.all_airport_codes.append(an_airport_code)

    def filter_airports(self):
        """Applies the filter to the list of airports"""
        new_airport_set = []
        if not self.all_airport_names:
            return

        for an_airport_code in self.all_airport_codes:
            a_code = an_airport_code.lower()
            if any(a_name.lower().strip().replace(" ", "+") in a_code for a_name in self.all_airport_names):
                new_airport_set.append(an_airport_code)

        self.all_airport_codes = new_airport_set


# In[ ]:


# 3rd Party, Keep here if turning into one file
from datetime import datetime, timedelta
from os import path
import pandas as pd


class Director:
    """"Controls the main flow of logic between different
    webpages, also responsible for writing records to parquet
    and starting the program"""
    
    print("class Director " + TimeStamp.timestamp()) #Elina 08-12-2020
    
    def __init__(self, countries,record_date, airports=None):
        print("class Director, def init " + TimeStamp.timestamp()) #Elina 08-12-2020
        self.all_country_names = countries
        self.all_airport_names = airports

        self.domain_name = "https://www.flightera.net"
        
        self.record_date = record_date
        self.my_browser = WebDriver(self.domain_name)
        self.current_country = None
        self.current_airport = None
        self.current_flight_page = None

    def run_program(self):
        print("class Director, def run_program " + TimeStamp.timestamp()) #Elina 08-12-2020
        """Groups main logic to be executed via client code"""
        self.loop_countries()
        self.my_browser.stop_driver()
        print("Program Has Finished. " + TimeStamp.timestamp())

    def loop_countries(self):
        """"Starts loop for a set of countries
        and creates the country_scraper class"""
        
        print("class Director, def loop_countries " + TimeStamp.timestamp()) #Elina 08-12-2020
        for country_name in self.all_country_names:
            self.my_browser.move_to_page(f"{self.domain_name}/en/country/{country_name}")
            if self.my_browser.is_error_page: continue
            self.current_country = CountryScraper(country_name,
                                                  self.my_browser.current_page,
                                                  self.all_airport_names)
            self.current_country.get_correct_airports()
            self.loop_airports()

    def loop_airports(self):
        """Starts loop for a given set of airports
        and creates the airport_scraper class"""
        
        print("class Director, def loop_airports " + TimeStamp.timestamp()) #Elina 08-12-2020
        
        for a_airport_code in self.current_country.all_airport_codes:
            print("def loop_airports, start loop airport code" + a_airport_code + TimeStamp.timestamp()) #Elina 08-12-2020
            self.current_airport = AirportScraper(self.record_date)
            self.loop_departures_or_arrivals(a_airport_code, "departure")
            self.current_airport.record_set_completed = False
            self.loop_departures_or_arrivals(a_airport_code, "arrival")

    def loop_departures_or_arrivals(self, airport_code, flight_type):
        """loop so that the same logic can be used for both
        arrival and departure airport pages"""
        
        print("class Director, def loop_departures_or_arrivals " + TimeStamp.timestamp()) #Elina 08-12-2020
        
        target_page = f"{self.domain_name}{airport_code}/{flight_type}/{self.date_string()} 00_00?"
        print("def loop_departures_or_arrivals, target page: "+ target_page + TimeStamp.timestamp()) #Elina 08-12-2020
        self.my_browser.move_to_page(target_page)
        if self.my_browser.is_error_page: return
        self.current_airport.set_page(self.my_browser.current_page)

        while self.current_airport.record_set_completed is False:
            self.loop_airport_pages(flight_type)
            #Elina 08-12-2020. Check the While Loop.

    def loop_airport_pages(self, flight_type):
        """Grabs record links off an airport page and calls the loop for them,
        also contains considerable error checking behaviour"""
        
        print("class Director, def loop_airport_pages " + TimeStamp.timestamp()) #Elina 08-12-2020
        
        self.my_browser.wait_for_class_element_to_load("container-fluid")

        if self.my_browser.no_flights_found():
            self.current_airport.record_set_completed = True
            return
            #Elina 08-12-2020. Check the record set complete statement.
            
        next_page_link = self.current_airport.get_later_flights_link()
        print("loop airport pages, next_page_link: " + TimeStamp.timestamp()) #Elina 08-12-2020 
        airport_url = self.my_browser.current_page_url
        print("loop airport pages, airport url: "+airport_url+ TimeStamp.timestamp()) #Elina 08-12-2020 
        self.current_airport.get_page_records(flight_type)
        self.loop_records()

        if next_page_link is None:
            next_page_link = self.handle_no_later_flights_link(retry_tokens=1)
            if next_page_link is None:
                self.current_airport.record_set_completed = True
                return

        if self.current_airport.record_set_completed is False: #Elina 08-12-2020. Check the record set complete statement.
            self.my_browser.move_to_page(f"{self.domain_name}/{next_page_link}")
            if self.my_browser.is_error_page:
                self.current_airport.record_set_completed = True
                return
            self.current_airport.set_page(self.my_browser.current_page)

    def loop_records(self):
        """Loops a given page of records,
        Moves to a records page and creates the final record object using
        the flight_Scraper class. It also calls write_record_to_parquet"""
        
        print("class Director, def loop_records " + TimeStamp.timestamp()) #Elina 08-12-2020
        
        for temp_record in self.current_airport.all_temp_flight_records:
            self.my_browser.move_to_page(f"{self.domain_name}{temp_record.url}")
            self.current_flight_page = FlightScraper(self.date_string(), self.my_browser.current_page)
            if self.my_browser.is_error_page is True:
                new_record = self.current_flight_page.temp_record_factory(temp_record.url,
                                                                          temp_record.flight_type)
            else:
                new_record = self.current_flight_page.flight_record_factory(temp_record.url,
                                                                            temp_record.flight_type)
                print("def loop_records, write new record to parquet:" + TimeStamp.timestamp()) #Elina 08-12-2020
            self.write_record_to_parquet(new_record)

        self.current_airport.all_temp_flight_records = [] #Elina 08-12-2020. Check this []

    def write_record_to_parquet(self, flight_record):
        """Reads old file, and writes a to a new file with the new record"""
        
        print("class Director, def write_record_to_parquet " + TimeStamp.timestamp()) #Elina 08-12-2020
        
        country_no_spaces = self.current_country.name.replace(" ", "_")
        file_name = f"{country_no_spaces}.parquet"
        new_data = pd.DataFrame([vars(flight_record)])

        if path.exists(file_name):
            existing_data = pd.read_parquet(file_name, engine='pyarrow')
            combined_data = pd.concat([existing_data, new_data])
            combined_data.to_parquet(file_name, index=False)
            print("one record appended " + TimeStamp.timestamp())
        else:
            new_data.to_parquet(file_name, index=False)
            print("new record appended " + TimeStamp.timestamp())
            
    def handle_no_later_flights_link(self, retry_tokens=1):
        """Tries to find the later flight link 3 times before moving on"""
        
        print("class Director, def handle_no_later_flights_link " + TimeStamp.timestamp()) #Elina 08-12-2020
        
        if retry_tokens < 3:
            self.my_browser.refresh_driver(5)
            self.my_browser.move_to_page(self.my_browser.current_page_url)
            self.current_airport.set_page(self.my_browser.current_page)
            next_page_link = self.current_airport.get_later_flights_link()
            if next_page_link is None:
                new_tokens = retry_tokens + 1
                self.handle_no_later_flights_link(new_tokens)
            else:
                print("Success! found the link after: "+ {retry_tokens} +"tries")
                return next_page_link
        else:
            print("Number of Tries: "+ str({retry_tokens}))
            return None
       
    def date_string(self) -> str:
        """Returns a string version of the date"""
        #print("class Director, def date_string " + TimeStamp.timestamp()) #Elina 08-12-2020
        return self.record_date.strftime('%Y-%m-%d')

#class TimeStamp:
    #def timestamp():
        #dateTimeObj = datetime.now()
        #timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        #return timestampStr
    
if __name__ == "__main__":
    
    # Add/remove Countries you wish to scrape.
    target_countries = ["Australia"]

    # Add/remove airports you to scrape,
    # Leave empty to scrape all airports.
    #target_airports =["Gold Coast"]
    target_airports = ["Mildura"]
    print("Start main program "+TimeStamp.timestamp()) #Elina 08-12-2020
    datelist = pd.date_range(start='2018-12-30',end='2018-12-30').tolist()
    for i in range(len(datelist)):
        record_date = datelist[i]
        my_director = Director(target_countries,record_date, target_airports)
        my_director.run_program()


# In[ ]:





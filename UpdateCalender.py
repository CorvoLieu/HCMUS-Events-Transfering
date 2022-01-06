import os
from unittest import result
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as act
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import collections

'''
TO-DO
[x] Change Calendar
[x] Change data get from web
[x] Check if yet saved
[x] Sort Calendar event
[x] Take next Month
[ ] Check if entered correctly
[ ] Customize notif
[ ] Create new Account
[ ] Create new calendar
'''

PATH = "chromedriver.exe"
driver = webdriver.Chrome(PATH)

MonthToInt = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

MoodleAcc = ""
MoodlePas = ""
GGAcc = ""
GGPas = ""
SelectedCalendar = ''
numOfMonthTake = 3

MoodleCalendar = "https://courses.ctda.hcmus.edu.vn/calendar/view.php?view="
CalLink = "https://calendar.google.com/calendar/u/0/r/day/"

isFinished = False
timeLooped = 0
calenEvent = {
    '09 January 2022': [('test1', '09:00')]
}

def findNewEvent(oldEvent: dict) -> dict:
    if not oldEvent:
        return calenEvent

    newKey = list(calenEvent.keys())
    oldKey = list(oldEvent.keys())
    result = {}

    i = j = 0
    while i < len(oldKey) and j < len(newKey):
        if oldKey[i] < newKey[j]:
            i += 1
            continue
        elif oldKey[i] > newKey[j]:
            j += 1
            continue
        else:
            temp = set(calenEvent[newKey[j]]).symmetric_difference(oldEvent[oldKey[i]])
            if temp:
                result[newKey[j]] = temp
            i += 1
            j += 1

    return result

def loadOldEvent() -> dict:
    if os.stat('OldEvents.txt').st_size == 0:
        return {}

    result = {}
    oldEventFile = open('OldEvents.txt', 'rt')
    data = oldEventFile.read().split('\n')
    
    for value in data:
        item = value.split(': ')
        result[item[0]] = []
        events = item[1].split('; ')
        for evnt in events:
            info = tuple(evnt.split(', '))
            result[item[0]].append(info)
    oldEventFile.close()
    return dict(sorted(result.items()))

def saveAllEvents():
    saveFile = open('OldEvents.txt', 'wt')
    for k, vs in calenEvent.items():
        saveFile.write(f'{k}: ')
        for v in vs:
            if v != vs[0]:
                saveFile.write('; ')
            saveFile.write(f'{v[0]}, {v[1]}')
        if calenEvent[k] != calenEvent[list(calenEvent.keys())[-1]]:
            saveFile.write('\n')
    saveFile.close()

def compileEvent() -> dict:
    oldEvent = loadOldEvent()
    result = findNewEvent(oldEvent)
    return result

def loginMoodle():
    accField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
    )
    accField.send_keys(MoodleAcc)
    pwField = driver.find_element(By.ID, "password")
    pwField.send_keys(MoodlePas)
    lgButton = driver.find_element(By.ID, "loginbtn")
    lgButton.click()

def loginCalendar():
    super_get(CalLink)
    
    time.sleep(3)          # In case of bot detection
    accField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
    )
    accField.send_keys(GGAcc)
    accField.send_keys(Keys.ENTER)
    time.sleep(2)
    pwField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
    )
    time.sleep(2)
    pwField.send_keys(GGPas)
    pwField.send_keys(Keys.ENTER)

def eventProcessing(event):
    # Get event ID
    temp = event.find_element(By.XPATH, ".//a")
    id = temp.get_attribute("data-event-id")
    event.click()

    # Wait for info window and info
    tempWindow = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//div[@class='summary-modal-container'][@data-event-id='{id}']"))
    )
    time.sleep(1)
    year = driver.find_element(By.XPATH, "//h2[@class='current']").text[-4:]
    title = tempWindow.get_attribute("data-event-title")
    date_time = tempWindow.text
    time_info = date_time.split(', ')

    # Save event
    date = time_info[1][:2]
    if int(date) < 10:
        time_info[1] = '0' + time_info[1]
    key = time_info[1] + ' ' + year
    calenEvent.setdefault(key, [])
    time_info[2] = time_info[2].replace(time_info[2][time_info[2].find('\n'):], '')
    calenEvent[key].append((title, time_info[2]))

    # Close info window
    print(key + ': ' + str(calenEvent[key]))
    closeButton = tempWindow.find_element(By.XPATH, "//button[@type='button'][@class='close']")
    closeButton.click()
    time.sleep(1)

def createEventForm():
    calendarField = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='G5v83e elYzab-DaY83b-ppHlrf J2aUD T8M5bd']"))
    )
    calendarField.click()
    time.sleep(1)
    eventInfoWidow  = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='BTotkb JaKw1']"))
    )
    moreOption = eventInfoWidow.find_element(By.XPATH, ".//span[@class='NPEfkd RveJvd snByac']")
    moreOption.click()

def setDate(date: str):
    temp = driver.find_element(By.XPATH, "//div[@aria-label='Event Details']")

    dateField = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Start date']"))
    )
    dateField.click()
    time.sleep(.5)
    dateField.send_keys(Keys.BACKSPACE)
    dateField.send_keys(f"{MonthToInt[date[3:-5]]}/{date[:2]}/{date[-4:]}\n")
    time.sleep(.5)
    dateField.send_keys(Keys.ENTER)

    temp.click()
    dateField = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='End date']"))
    )
    dateField.click()
    time.sleep(.5)
    dateField.send_keys(Keys.BACKSPACE)
    dateField.send_keys(f"{MonthToInt[date[3:-5]]}/{date[:2]}/{date[-4:]}\n")
    time.sleep(.5)
    dateField.send_keys(Keys.ENTER)
    temp.click()

def setTime(timeInput: str):
    settedTime = timeInput[1][:5]
    if int(settedTime[:2]) < 11:
        settedTime += 'am'

    startTimeField = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Start time']"))
    )
    startTimeField.click()
    time.sleep(1)
    startTimeField.send_keys(Keys.BACKSPACE)
    startTimeField.send_keys(settedTime)
    startTimeField.send_keys(Keys.ENTER)

    endTimeField = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='End time']"))
    )
    endTimeField.click()
    time.sleep(1)
    endTimeField.send_keys(Keys.BACKSPACE)
    endTimeField.send_keys(settedTime)
    endTimeField.send_keys(Keys.ENTER)

def ChangeCalender():
    time.sleep(1)
    calendarOption = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Calendar'][@id='xCalSel']"))
    )
    calendarOption.click()
    time.sleep(1)
    availableOption = calendarOption.find_elements(By.XPATH, ".//child::div[@class='OA0qNb ncFHed']//div[@role='option']")
    for option in availableOption:
        if option.text == SelectedCalendar:
            time.sleep(1)
            option.click()
            break

def makeNotif():
    temp = driver.find_element(By.XPATH, "//div[@aria-label='Event Details']")
    addNotif = driver.find_element(By.XPATH, "//div[@aria-label='Add notification']")
    addNotif.click()

    # Amount
    timeNotif = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Minutes in advance for notification']"))
    )
    timeNotif.click()
    timeNotif.clear()
    timeNotif.send_keys(1)      # Time
    timeNotif.send_keys(Keys.ENTER)
    temp.click()

    # Unit
    timeOptionButton = driver.find_element(By.XPATH, "//div[@aria-label='Unit of time selection']")
    timeOptionButton.click()
    timeOption = timeOptionButton.find_elements(By.XPATH, ".//child::div[@class='OA0qNb ncFHed']//div[@role='option']")

    for option in timeOption:
        if option.text == 'days':     # Unit
            time.sleep(1)
            option.click()
            break
    temp.click()

def enterTitle(title: str):
    titleField =  WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Title']"))
    )
    titleField.click()
    titleField.send_keys(title)
    titleField.send_keys(Keys.ENTER)

def super_get(url: str):
    driver.get(url)
    driver.execute_script("window.onbeforeunload = function() {};")

def main():
    global timeLooped, isFinished, driver, calenEvent
    while (not isFinished) and (timeLooped < 5):
        super_get(MoodleCalendar + "month")
    
        #Open moodle
        loginMoodle()
        
        # try:
        cldrEvents = []
        for i in range(numOfMonthTake - 1):
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "calendarwrapper"))
            )
            cldrEvents = container.find_elements(By.XPATH, "//li[@data-region='event-item']")

            ### Get events from Moodle
            # Get Event Info
            for event in cldrEvents:
                eventProcessing(event)
            nextMonthButton = driver.find_element(By.XPATH, "//a[@title='Next month']")
            nextMonthButton.click()
            cldrEvents.clear()
            time.sleep(1)
        ### Get new event and skip old events
        calenEvent = dict(sorted(calenEvent.items()))
        newEvents = compileEvent()
        if not newEvents:
            print('There are no new events on the new list')
            isFinished = True
            break
        
        ### Save to Google
        # Enter GG Acount
        loginCalendar()

        # Save to Calendar
        for key, items in newEvents.items():
            for item in items:
                time.sleep(1)
                todayButton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='U26fgb O0WRkf oG5Srb C0oVfc GXlaye qRI4pc M9Bg4d']"))
                )
                todayButton.click()

                # Enter create form
                createEventForm()
                time.sleep(2)

                if SelectedCalendar:
                    ChangeCalender()

                # Enter event
                setTime(item)
                setDate(key)
                makeNotif()
                enterTitle(item[0])
        isFinished = True

        # except:
        #     print("Something went wrong, retrying")
        #     timeLooped += 1

    if timeLooped == 5:
        print("Time retry exceeded the limit")
    else:
        print("Run successfully")
    
    saveAllEvents()

    os.system('pause')
    driver.quit()

if __name__ == "__main__":
    main()
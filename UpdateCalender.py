import os
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as act
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

FORMAT = 'utf-8'
EDGE_PATH = "msedgedriver.exe"
driver = webdriver.Edge(EDGE_PATH)
# CHROME_PATH = "chromedriver.exe"
# driver = webdriver.Chrome(CHROME_PATH)

MoodleAcc = ""
MoodlePas = ""
GGAcc = ""
GGPas = ""
SelectedCalendar = ''
numOfMonthTake = 2
allNotif = [
    '1 h'
]

MoodleCalendar = "https://courses.ctda.hcmus.edu.vn/calendar/view.php?view=month"
CalLink = "https://calendar.google.com/calendar/u/0/r/day/"

calenEvent = {}
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

def super_send_keys(parent, byEle, eleSource, inputData):
    try:
        enterField = WebDriverWait(parent, 30).until(
            EC.element_to_be_clickable((byEle, eleSource))
        )
    except:
        return

    finished = False
    while not finished:
        enterField.click()
        enterField.send_keys(Keys.BACKSPACE)
        enterField.send_keys(inputData)
        enterField.send_keys(Keys.ENTER)
        temp = enterField.get_attribute('data-initial-value')
        if temp == inputData:
            finished = True

def normalizeTime(inputTime):
    temp = int(inputTime[:2])
    result = ''
    isPM = True
    if temp == 0:
        result += str(12)
    elif temp < 10:
        result += inputTime[1]
    elif temp > 12:
        result += str(temp - 12)
        isPM = True
    else:
        result += str(12)
        isPM = True

    result += ':' + inputTime[3:]
    result = result.replace(result[result.find('\n'):], '')
    
    if isPM:
        result += 'pm'
    else:
        result += 'am'

    return result

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
            result[newKey[j]] = calenEvent[newKey[j]]
            j += 1
            continue
        else:
            temp = set(calenEvent[newKey[j]]).symmetric_difference(oldEvent[oldKey[i]])
            if temp:
                result[newKey[j]] = temp
            i += 1
            j += 1

    while j < len(newKey):
        result[newKey[j]] = calenEvent[newKey[j]]
        j += 1

    return result

def loadOldEvent() -> dict:
    if os.stat('OldEvents.data').st_size == 0:
        return {}

    result = {}
    oldEventFile = open('OldEvents.data', 'rb')
    data = oldEventFile.read().decode(FORMAT).split('\n')
    
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
    saveFile = open('OldEvents.data', 'wb')
    for k, vs in calenEvent.items():
        saveFile.write(f'{k}: '.encode(FORMAT))
        for v in vs:
            if v != vs[0]:
                saveFile.write('; '.encode(FORMAT))
            saveFile.write(f'{v[0]}, {v[1]}'.encode(FORMAT))
        if calenEvent[k] != calenEvent[list(calenEvent.keys())[-1]]:
            saveFile.write('\n'.encode(FORMAT))
    saveFile.close()

def compileEvent() -> dict:
    oldEvent = loadOldEvent()
    result = findNewEvent(oldEvent)
    return result

def loginMoodle():
    accField = WebDriverWait(driver, 20).until(
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
    accField = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
    )
    accField.send_keys(GGAcc)
    accField.send_keys(Keys.ENTER)
    time.sleep(2)
    pwField = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
    )
    time.sleep(2)
    pwField.send_keys(GGPas)
    pwField.send_keys(Keys.ENTER)

    time.sleep(3)

def eventProcessing(event):
    # Get event ID
    time.sleep(.5)
    temp = event.find_element(By.XPATH, ".//a")
    id = temp.get_attribute("data-event-id")
    event.click()

    # Wait for info window and info
    tempWindow = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//div[@class='summary-modal-container'][@data-event-id='{id}']"))
    )
    time.sleep(1)
    year = driver.find_element(By.XPATH, "//h2[@class='current']").text[-4:]
    title = tempWindow.get_attribute("data-event-title")
    date_time = tempWindow.text
    time_info = date_time.split(', ')

    # Save event
    time_info[2] = normalizeTime(time_info[2])
    key = time_info[1] + ' ' + year
    calenEvent.setdefault(key, [])
    calenEvent[key].append((title, time_info[2]))

    # Close info window
    print(key + ': ' + str(calenEvent[key]))
    closeButton = tempWindow.find_element(By.XPATH, "//button[@type='button'][@class='close']")
    closeButton.click()

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

def setDate(inputDate: str):
    temp = driver.find_element(By.XPATH, "//div[@aria-label='Event Details']")

    formattedDate = ''
    if inputDate[1] == ' ':
        formattedDate = (f"{MonthToInt[inputDate[2:-5]]}/{inputDate[:1]}/{inputDate[-4:]}")
    else:
        formattedDate += (f"{MonthToInt[inputDate[3:-5]]}/{inputDate[:2]}/{inputDate[-4:]}")

    super_send_keys(driver, By.XPATH, "//input[@aria-label='Start date']", formattedDate)
    temp.click()

    super_send_keys(driver, By.XPATH, "//input[@aria-label='End date']", formattedDate)
    temp.click()

def setTime(timeInput: str):
    settedTime = timeInput[1]

    temp = driver.find_element(By.XPATH, "//div[@aria-label='Event Details']")

    super_send_keys(driver, By.XPATH, "//input[@aria-label='Start time']", settedTime)
    temp.click()

    super_send_keys(driver, By.XPATH, "//input[@aria-label='End time']", settedTime)
    temp.click()

def ChangeCalender():
    calendarOption = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Calendar'][@id='xCalSel']"))
    )
    calendarOption.click()
    time.sleep(.5)
    availableOption = calendarOption.find_elements(By.XPATH, ".//child::div[@class='OA0qNb ncFHed']//div[@role='option']")
    for option in availableOption:
        if option.text == SelectedCalendar:
            time.sleep(.5)
            option.click()
            break

def makeNotif():
    temp = driver.find_element(By.XPATH, "//div[@aria-label='Event Details']")
    addNotif = driver.find_element(By.XPATH, "//div[@aria-label='Add notification']")
    for i in enumerate(allNotif):
        time.sleep(.5)
        addNotif.click()

    i = 0
    notif_info = []
    for notifTime in allNotif:
        notif_info.append(notifTime.split(' '))
        i += 1

    # Amount
    i = 0
    notifsFields = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Minutes in advance for notification']"))
    )
    notifsFields = driver.find_elements(By.XPATH, "//input[@aria-label='Minutes in advance for notification']")
    for notifsField in notifsFields:
        notifsField.click()
        notifsField.clear()
        notifsField.send_keys(notif_info[i][0])      # Time
        notifsField.send_keys(Keys.ENTER)
        temp.click()
        i += 1

    # Unit
    i = 0
    timeOptionButtons = driver.find_elements(By.XPATH, "//div[@aria-label='Unit of time selection']")
    for timeOptionButton in timeOptionButtons:
        timeOptionButton.click()
        timeOption = timeOptionButton.find_element(By.XPATH, ".//div//div[@role='option']")
        timeOption.send_keys(notif_info[i][1])
        time.sleep(.5)
        chosenOptions = timeOption.find_element(By.XPATH, "..//div[@class='MocG8c LMgvRb KKjvXb']")
        chosenOptions.send_keys(Keys.ENTER)
        i += 1

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
    if not MoodleAcc or not MoodlePas or not GGAcc or not GGPas:
        print('Please follow the instruction and edit the code accordingly')
        return

    super_get(MoodleCalendar)

    #Open moodle
    loginMoodle()
    
    cldrEvents = []
    for i in range(numOfMonthTake - 1):
        container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "calendarwrapper"))
        )
        cldrEvents = container.find_elements(By.XPATH, "//li[@data-region='event-item']")        ### Get events from Moodle
        # Get Event Info
        time.sleep(1)
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
        return
    
    ### Save to Google
    # Enter GG Acount
    loginCalendar()    # Save to Calendar
    for key, items in newEvents.items():
        for item in items:
            time.sleep(1)
            todayButton = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='U26fgb O0WRkf oG5Srb C0oVfc GXlaye qRI4pc M9Bg4d']"))
            )
            todayButton.click()            # Enter create form
            createEventForm()
            time.sleep(.5)            
            if SelectedCalendar:
                ChangeCalender()            # Enter event
            setTime(item)
            setDate(key)
            makeNotif()
            enterTitle(item[0])

    isFinished = True
    
    saveAllEvents()

    os.system('pause')
    driver.quit()

if __name__ == "__main__":
    main()
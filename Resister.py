import os
from selenium import webdriver

EDGE_PATH = "msedgedriver.exe"
url = 'https://accounts.google.com/signup'
driver = webdriver.Edge(EDGE_PATH)

def main():
    driver.get(url)
    print('Create your new account and press any key here to stop')
    os.system('pause')
    try:
        driver.close()
    except:
        pass

if __name__ == '__main__':
    main()
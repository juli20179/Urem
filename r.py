import re
import json
import time
from sys import argv
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidArgumentException, NoSuchAttributeException, ElementNotVisibleException, NoSuchElementException, ElementNotInteractableException
from terminate_chrome import killChromeProcess
from clear_data import clearChromeData

CommonExceptions = (TimeoutException, WebDriverException, InvalidArgumentException, NoSuchAttributeException, ElementNotVisibleException, NoSuchElementException, ElementNotInteractableException)

IS_SIGNED_IN = False
BASE_URL = 'https://rewards.bing.com/'

def progress(driver, wait, device):
    try:
        ptrn = re.compile("<b>(\d{1,3})<\/b> \/ (\d{2,3})<\/p>")
        driver.get(BASE_URL+"pointsbreakdown")
        if wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal-host"]/div[2]'))):
            print('--')
            platform = {'Desktop':0, 'Mobile':1}
            for i in driver.find_elements(By.CLASS_NAME, 'cardContainer'):
                result = ptrn.findall(i.get_attribute('innerHTML'))
                print(result)
                if len(result) >  1:
                    if device in platform:
                        return result[platform[device]]
                    else: return result[:2]
    except (Exception, *(CommonExceptions)) as e:
        print(f"There's some exception in progress-\n{e}")
    
def bingLogin(wait):
    try:
        Sign_in = wait.until(EC.text_to_be_present_in_element_value((By.ID,'id_a'), 'Sign in'))
        if (Sign_in):
            wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/header/div/a[1]/div/span/input'))).click()
    except CommonExceptions as e:
        print("Already Signed In", e)

def startSearch(driver, wait, exten, device):
    global IS_SIGNED_IN
    
    driver.execute_script(f"window.open('https://www.bing.com/news/?form=ml11z9&crea=ml11z9&wt.mc_id=ml11z9&rnoreward=1&rnoreward=1')")    
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(10)

    if not IS_SIGNED_IN:
        bingLogin(wait)
        IS_SIGNED_IN = True
     
    driver.get(exten)
    spoofing = Select(driver.find_element(By.ID, 'platform-spoofing'))
    spoofing.select_by_visible_text(f'{device} only')
    wait.until(EC.element_to_be_clickable((By.ID, 'search'))).click()
    driver.switch_to.window(driver.window_handles[0])

    while True:
        time.sleep(10)
        p1, p2 = progress(driver, wait, device=f'{device}')
        if p1 == p2: break
        driver.refresh()

    driver.switch_to.window(driver.window_handles[1])
    driver.execute_script(f"window.open('data:;')")
    driver.switch_to.window(driver.window_handles[2])
    driver.get(exten)
    wait.until(EC.element_to_be_clickable((By.ID, 'stop'))).click()
    time.sleep(0.5)
    driver.close()
    time.sleep(0.5)
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    time.sleep(0.5)
    driver.switch_to.window(driver.window_handles[0])

def runMSreward(user, password, date_ , fs):
    global IS_SIGNED_IN

    userdatadir = r'C:\Users\Tushar\AppData\Local\Google\Chrome\User Data'
    chromeOptions = webdriver.ChromeOptions()
    if len(argv) >= 2 and argv[1] == '-h':
        chromeOptions.headless = True
        print('Starting chrome in headless mode - ')
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-logging"])
    chromeOptions.add_argument(f"--user-data-dir={userdatadir}")
    chromeOptions.add_argument("profile-directory=Default")
 
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions) as driver:
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        
        # REWARD LOGIN
        reward_sign = BASE_URL+'signin'

        driver.get(reward_sign)
        time.sleep(1)
       
        if (wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="loginHeader"]/div[1]'),'Sign in'))):
            EMAILFIELD = (By.ID, "i0116")
            PASSWFIELD = (By.ID, "i0118")
            NEXTBUTTON = (By.ID, "idSIButton9")
            SRTYBUTTON = (By.ID, "iLandingViewAction")

            wait.until(EC.element_to_be_clickable(EMAILFIELD)).\
                send_keys(user)
            wait.until(EC.element_to_be_clickable(NEXTBUTTON)).\
                click()
            wait.until(EC.element_to_be_clickable(PASSWFIELD)).\
                send_keys(password)                
            wait.until(EC.element_to_be_clickable(NEXTBUTTON)).\
                click()

            if 'Abuse' in driver.current_url:
                points = 'Blocked'
                fs = open('log_points.txt', 'a', encoding='utf-8')
                fs.write(f"{dateObj[0]}-{dateObj[1]}-{dateObj[2]} :   {user : <40} :   {points : >10}\n")
                fs.close()
                return driver.quit() 

            wait.until(EC.element_to_be_clickable(NEXTBUTTON)).\
                click()

            if 'Rewards Error' in driver.title:
                points = 'Suspended'
                fs = open('log_points.txt', 'a', encoding='utf-8')
                fs.write(f"{dateObj[0]}-{dateObj[1]}-{dateObj[2]} :   {user : <40} :   {points : >10}\n")
                fs.close()
                return driver.quit()

            time.sleep(2)
            
        # SEARCH EXTENSION
        abs_extension  = "chrome-extension://ipbgaooglppjombmbgebgmaehjkfabme/popup.html"
        driver.switch_to.window(driver.window_handles[0])    

        progress_state = progress(driver, wait, None)
        if not (progress_state[0][0] == progress_state[0][1] and progress_state[1][0] == progress_state[1][1]):     
            if progress_state[0][0] != progress_state[0][1]:
                startSearch(driver, wait, abs_extension, 'Desktop')
            if progress_state[1][0] != progress_state[1][1]:
                startSearch(driver, wait, abs_extension, 'Mobile')
        else:
            driver.execute_script(f"window.open('https://www.bing.com/news/?form=ml11z9&crea=ml11z9&wt.mc_id=ml11z9&rnoreward=1&rnoreward=1')")    
            driver.switch_to.window(driver.window_handles[1])

            time.sleep(5)       
            if not IS_SIGNED_IN:
                bingLogin(wait)
                IS_SIGNED_IN = True
            driver.close()

        driver.switch_to.window(driver.window_handles[0])
        print("....")
        driver.get(reward_sign)

        addSym = "AddMedium"
        skpSym = "SkypeCircleCheck"
        xp_50_skype = "/html/body/div[4]/div/div/div/div/div/div[1]/span[2]/span[2]/span/div/img"
        xp_30_skype1 = "/html/body/div[4]/div/div/div/div/div/div[1]/span/span[2]/span/div/img"
        xp_30_skype2 = "/html/body/div[4]/div/div/div/div/div/div[1]/span[2]/span[2]/span/div/img"
        overlay = ""
        poll = "/html/body/div[3]/div/div/div/div/div/span/div/img"
        quiz = "/html/body/div[2]/main/ol/li[1]/div/div[3]/div/div[1]/span[2]/div/img"


        # REWAED SECTION
        tab_Wait = WebDriverWait(driver, 3)
        task_Wait1 = WebDriverWait(driver, 5)
        task_Wait2 = WebDriverWait(driver, 60)

        for reward in driver\
            .find_elements(By.CSS_SELECTOR, f"span.mee-icon-{addSym}, span.mee-icon-HourGlass"):
            if(tab_Wait.until(EC.element_to_be_clickable(reward)).click()):
                time.sleep(3)
            if driver.current_url == BASE_URL+'legaltextbox' and WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal-host"]/div[2]'))):
                tab_Wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="legalTextBox"]/div/div/div[3]/a/span'))).click()
            
            driver.switch_to.window(driver.window_handles[1])
            
            try:
                if(task_Wait1.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#overlayPanel')))):
                    print(f'inside overlay panel tab -')
                    count += 1
                    if 'RewardsDailyPoll' not in driver.current_url:
                        try:
                            if(task_Wait2.until(EC.visibility_of_element_located((By.XPATH, f'{xp_50_skype}')))):
                                print('performing 50 points reward')
                                driver.close()
                        except:
                            try:
                                if(task_Wait2.until(EC.visibility_of_element_located((By.XPATH, f'{xp_30_skype1} | {xp_30_skype2}')))):
                                    print('performing 30 points reward')
                                    driver.close()
                            except: pass
                    else:
                        try:
                            if(task_Wait2.until(EC.visibility_of_element_located((By.XPATH, f'{poll}')))):
                                print('performing poll reward')
                                driver.close()
                        except: pass                     
            except:
                try:
                    if(task_Wait1.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h2.b_focusLabel')))):
                        if(task_Wait2.until(EC.visibility_of_element_located((By.XPATH, f'{quiz}')))):
                            print('performing quiz reaward')
                            driver.close()
                except:
                    print('performing plane reweard')
                    driver.close()
           
            driver.switch_to.window(driver.window_handles[0])

        time.sleep(3)
        points = driver.find_element(By.XPATH, '//*[@id="balanceToolTipDiv"]/p/mee-rewards-counter-animation/span').get_attribute('innerHTML')

        open('log_points.txt', 'a', encoding='utf-8').write(f"{dateObj[0]}-{dateObj[1]}-{dateObj[2]} :   {user : <40} :   {points : >10}\n")


if __name__ == '__main__':
    killChromeProcess()
    time.sleep(1)

    with open('_data.json') as user_data:
        file_contents = user_data.read()
        data_ids = tuple(dict(json.loads(file_contents)).items())

    date_ = date.today()
    day = f'{date_.day:02d}'
    month = f'{date_.month:02d}'
    year = f'{date_.year:04d}'
    dateObj = [day, month, year]

    # with open('log_points.txt', 'a', encoding='utf-8') as fs:
    i = 0
    while i < len(data_ids):
        clearChromeData()
        try:
            user, password = data_ids[i]
            i += 1
            start = time.time()
            print(f'Signing in to {user} -')
            runMSreward(user, password, dateObj)
            end = time.time()
            print(f"Total execution time : {end - start}")
        except (Exception, *CommonExceptions) as e:
            print(f'Something went wrong, while working with {user}\n {e}\nRetrying with same user data...')
            i -= 1
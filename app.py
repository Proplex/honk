import requests, os, sys, time, pickle, LocalStorage, uuid
from selenium import webdriver
from LocalStorage import LocalStorage

MYSUBARU_USER = os.getenv("MYSUBARU_USER", "") # email
MYSUBARU_PASS = os.getenv("MYSUBARU_PASS", "") # password
MYSUBARU_PIN  = os.getenv("MYSUBARU_PIN", "") # 4 digit PIN
MYSUBARU_SECURITY = os.getenv("MYSUBARU_SECURITY", "") # security question answer (i think there's only one?)

if MYSUBARU_USER == "" or MYSUBARU_PASS == "" or MYSUBARU_PIN == "" or MYSUBARU_SECURITY == "":
  print("Please set MYSUBARU_USER, MYSUBARU_PASS, MYSUBARU_SECURITY and MYSUBARU_PIN envvars.")
  sys.exit(1)
client = webdriver.Chrome() # start selenium (after dev, use headless)
localstorage = LocalStorage(client)

client.get('https://www.mysubaru.com')

# try to load previous state, this is important as we don't want to continually
# keep adding new authorized devices to MySubaru
try:
  # load cookies
  with open('cookies.pkl', 'rb') as cookies_file:
    print("Using cookies from previous state.")
    cookies = pickle.load(cookies_file)
    for cookie in cookies:
      print("Inserting: {}".format(cookie))
      client.add_cookie(cookie)
  # load localstorage
  with open('localstorage.pkl', 'rb') as localstorage_file:
    print("using LocalStorage from previous state.")
    localstore = pickle.load(localstorage_file)
    for key, value in localstore.items():
      print("Inserting: {} -> {}".format(key, value))
      localstorage[key] = value
except Exception as err:
  print(err)
  print("Couldn't find cookies or localstorage from previous state, this will cause a new device to be registered with MySubaru.")



client.find_element_by_id("username").send_keys(MYSUBARU_USER)
client.find_element_by_id("password").send_keys(MYSUBARU_PASS)
client.find_element_by_class_name("submitLoginForm").click()
time.sleep(10) # FIXME: better detection then just waiting

try:
  client.find_element_by_class_name("securityQuestionText") # test to see if security modal shows
  print("We got prompted for a security question.")
  client.find_element_by_class_name("securityAnswer").send_keys(MYSUBARU_SECURITY)
  client.find_element_by_class_name("submitSecurityAnswer").click()
  time.sleep(2)
  client.find_element_by_name("deviceName").send_keys("Honk {}".format(str(uuid.uuid4())[:4])) 
  client.find_elements_by_xpath('//*[@id="setDeviceNameModal"]/div/div/form/div/div/div/div[2]/div[2]/button')[0].click() # submit button
except:
  print("Looks like we didn't get a security check.")

time.sleep(2)

with open('cookies.pkl', 'wb') as cookies_file: # save cookies for next time (authorized device stuff)
  print("Saved cookies to disk.")
  pickle.dump(client.get_cookies(), cookies_file)

with open('localstorage.pkl', 'wb') as localstorage_file:
  print("Saved LocalStorage to disk.")
  pickle.dump(localstorage.items(), localstorage_file)


# lock car [just a test action at this point]
client.find_element_by_class_name("lockButton").click()
client.find_element_by_id("pin").send_keys(MYSUBARU_PIN)
client.find_element_by_class_name("submitOptionsTrigger").click()
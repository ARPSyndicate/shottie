from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from Screenshot import Screenshot_Clipping
import sys
import optparse
import os
import concurrent.futures
from PIL import ImageFile
import time
import warnings

warnings.filterwarnings("ignore")

BLUE='\033[94m'
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CLEAR='\x1b[0m'

print(BLUE + "Shottie[1.0] by ARPSyndicate" + CLEAR)
print(YELLOW + "web screenshot utility" + CLEAR)

ImageFile.LOAD_TRUNCATED_IMAGES = True

if len(sys.argv)<2:
        print(RED + "[!] ./shottie --help" + CLEAR)
        sys.exit()

else:
        parser = optparse.OptionParser()
        parser.add_option('-l', '--list', action="store", dest="list", help="list of targets to screenshot")
        parser.add_option('-o', '--output', action="store", dest="output", help="output directory")
        parser.add_option('-t', '--timeout', action="store", dest="timeout", help="timeout in seconds [default=30]", default=30)
        parser.add_option('-r', '--retries', action="store", dest="retries", help="retries [default=2]", default=2)
        parser.add_option('-T', '--tabs', action="store", dest="tabs", help="maximum tabs [default=10]", default=10)
        parser.add_option('-B', '--browsers', action="store", dest="browsers", help="maximum browsers [default=5]", default=5)

inputs,args  = parser.parse_args()
if not inputs.list:
        parser.error(RED + "[!] list of targets not given" + CLEAR)

ilist = str(inputs.list)
output = str(inputs.output)
timeout = int(inputs.timeout)
tabs = int(inputs.tabs)
retries = int(inputs.retries)
browsers = int(inputs.browsers)


if(not os.path.exists(output)): 
    os.mkdir(output)
output = output + "/"
with open(ilist) as f:
        targets=f.read().splitlines()
targets = list(set(targets))

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
targets = list(chunks(targets, browsers))


def browser(tars):
        global tabs, retries
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("window-size=1280,800")
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
        driver = uc.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(timeout)
        driver.implicitly_wait(int(timeout))
        ss = Screenshot_Clipping.Screenshot()
        count = 0
        for target in tars:
                for retry in range(0,retries):
                        try:
                                screenshot(target, count, tabs, driver, ss, timeout/2)
                                print(BLUE + "[+] " +url + CLEAR)
                                break
                        except Exception as ex:
                                if retry == retries-1:
                                        print(RED + "[!] "+target+"  -  "+str(ex.__class__.__name__)+ CLEAR)
                                continue
        driver.quit()

def screenshot(url, count, tabs, driver, ss, timeout):
        driver.get(url)
        time.sleep(timeout)
        image = ss.full_Screenshot(driver, save_path=output , image_name=url.replace("/","_")+".png")
        if count>tabs:
                count = 0
                for i in range(0,count):
                        driver.close()
                
        else:
                count = count + 1

with concurrent.futures.ThreadPoolExecutor(max_workers=browsers) as executor:
	try:
		executor.map(browser, targets)
	except(KeyboardInterrupt, SystemExit):
		print(RED + "[!] interrupted" + CLEAR)
		executor.shutdown(wait=False)
		sys.exit()


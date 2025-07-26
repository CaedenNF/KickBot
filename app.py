import os
import time
import random
import sys
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

fake = Faker()
channel = os.environ['CHANNEL_NAME']
url = f"https://kick.com/{channel}"

proxies = os.environ.get('PROXY_LIST', '').split(',') if os.environ.get('PROXY_LIST') else []

num_bots = int(input("Enter number of bots: ") or 10)

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

bots = []
for i in range(num_bots):
    try:
        print(f"Starting creation of bot {i+1}/{num_bots}")
        driver_options = options  # Copy options
        if proxies:
            proxy = proxies[i % len(proxies)]
            print(f"Using proxy: {proxy}")
            driver_options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Chrome(options=driver_options)
        
        # Get temp email
        driver.get("https://temp-mail.org/")
        time.sleep(5)
        email = driver.find_element(By.ID, "mail").get_attribute("value")
        print(f"Obtained temp email: {email}")
        
        # Open Kick and sign up
        driver.execute_script("window.open('https://kick.com/', 'newtab');")
        driver.switch_to.window("newtab")
        time.sleep(3)
        
        # Assume sign up button XPath; adjust if needed
        print("Clicking sign up button")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Sign up')]"))).click()
        
        # Fill form (assumed field names; inspect page to confirm)
        username = fake.user_name() + str(random.randint(1000, 9999))
        password = fake.password(length=12)
        print(f"Generated username: {username}, password: {password}")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        
        # Birthday
        month = random.choice(months)
        day = str(random.randint(1, 28))
        year = str(random.randint(1980, 2000))
        print(f"Selected birthday: {month} {day}, {year}")
        Select(driver.find_element(By.NAME, "month")).select_by_visible_text(month)
        driver.find_element(By.NAME, "day").send_keys(day)
        driver.find_element(By.NAME, "year").send_keys(year)
        
        # Terms
        driver.find_element(By.ID, "terms").click()
        
        # Submit
        print("Submitting signup form")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Switch to temp mail, wait for verification email
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(30)  # Adjust wait
        print("Checking for verification email")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".inbox-dataList li a"))).click()
        time.sleep(5)
        code = driver.find_element(By.XPATH, "//*[contains(text(), 'code')]/following-sibling::*").text.strip()[:6]  # Adjust XPath for code
        print(f"Obtained verification code: {code}")
        
        # Switch back, enter code
        driver.switch_to.window(driver.window_handles[1])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "verificationCode"))).send_keys(code)
        print("Submitting verification code")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Go to stream
        print("Navigating to stream URL")
        driver.get(url)
        time.sleep(5)
        try:
            # Set lowest video quality (assumes quality selector; inspect Kick's player for exact selector)
            quality_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Settings']")))
            quality_button.click()
            lowest_quality = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '144p')]")))
            lowest_quality.click()
            print("Set video quality to 144p")
        except:
            print("Failed to set video quality", file=sys.stderr)
        
        bots.append(driver)
        print(f"Bot {i+1} created successfully")
    except Exception as e:
        print(f"Error creating bot {i+1}: {str(e)}", file=sys.stderr)

print(f"All bots created. Keeping {len(bots)} bots active.")
while True:
    time.sleep(60)

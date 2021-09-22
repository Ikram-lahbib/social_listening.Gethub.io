from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import  datetime
from datetime import date
from .Methods import *


def Scraping(search, date1_search, date2_search): # test in django

    clean_json_file() # clean file json instance to add new data
    search = search.replace(' ', '+') # the why search in youtube

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path="static/chrome/chromedriver.exe", options=options)
    driver.get("https://www.youtube.com/results?search_query="+search)

    date_limit = datetime.datetime.now() + datetime.timedelta(minutes=5) # specify the date limit scraping in this case 5 minutes
    try:
        for i in range(10):
            driver.execute_script("window.scrollTo(0, window.scrollY + 5000)")
            sleep(0.5)
        sleep(5)
        list = driver.find_elements_by_xpath("//*[@id='contents']/ytd-item-section-renderer")
        if len(list) < 1:
            sleep(2)
            list = driver.find_elements_by_xpath("//*[@id='contents']/ytd-item-section-renderer")
    except:
        list = []
        driver.close()

    for index, link in enumerate(list[0:2]):
        print("number : " + str(index) + "-------------------------\n")

        for index2, video in enumerate(link.find_elements_by_xpath("//*[@id='contents']/ytd-video-renderer")):
            print("---------------- this for video : " + str(index2))
            if date_limit < datetime.datetime.now():# Check if the date is limit
                print("Time out")
                return "Time out"


            try:
                a = video.find_element_by_tag_name('a')
                a.send_keys(Keys.CONTROL + Keys.RETURN)
                driver.switch_to.window(driver.window_handles[1])

                # =================================== collect data ===================================

                print("----------------- for comments --------------------------\n")

                # -----  for comments ---------------------
                try:
                    driver.execute_script("window.scrollTo(0, window.scrollY + 1000)")
                    sleep(1)
                    driver.execute_script("window.scrollTo(0, window.scrollY + 3000)")
                    sleep(0.5)
                    driver.execute_script("window.scrollTo(0, window.scrollY + 3000)")
                    sleep(4)
                    text_comments = driver.find_element_by_xpath("//*[@id='contents']").text
                    if text_comments == "":
                        sleep(2)
                        text_comments = driver.find_element_by_xpath("//*[@id='contents']").text
                except:
                    text_comments = ""
                    print(" Disable comments ")
                    pass
                #l = list_dic_comments(text_comments)
                print('text_comments')

                # ===================================================================================
                # Close current tab
                driver.close()
                # Switch back to original tab
                driver.switch_to.window(driver.window_handles[0])
                # Save data gated
                try:
                    list_dic_comment = list_dic_comments(text_comments)
                    save_data_anstence_django_json(list_dic_comment) # for django

                except:
                    pass

            except:
                print("!!!! error accede to video number !!!! : " + str(index2))
                sleep(1)
                # for django
                # Close current tab
                driver.close()
                # Switch back to original tab
                driver.switch_to.window(driver.window_handles[0])

    sleep(2)
    driver.close()
    print("-------------------------------------------\n")

###################################################################################################################################
# ['#BBC #BBCiPlayer #BBCStories', 'Viral: The 5G Conspiracy Theory by @BBC Stories - BBC', '294\u202f634 vues•14 juil. 2020', '3,2 K', '884', 'PARTAGER', 'ENREGISTRER']

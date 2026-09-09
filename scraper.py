#jobs is in {ul , class="media-list in-card is-spaced is-divided is-reversed has-hover-d has-rects has-free-img bb" data-empty="Nothing available"}
    #evry job has : {li data-js-job class="has-pointer-d"} but with defrent {data-job-id = ?}
        # the furst enfo is in : {div , class="row is-m no-wrap v-align-center"} then {dive , class="u-flex t-small u-stretch p10l"} then {div , class="u-stretch"} then {h2 , class="t-large-d t-small m0t m5b" , a}
        #the summary is in {div , class="jb-descr m10t t-small"}
 
        #the location is in : {div , class="jb-tags m10t"} then {dl , class="dlist is-spaced t-small m0y row"} then {dt , class="p0 m20r jb-label-location job-company-location-wrapper"} then {a , class="t-default"} then {span}.
            #the second part of location is in : the same {dt} but in the end {a class="t-default"} then {span}

        #the date is in : {div , class="jb-footer row is-m v-align-center m10t"} then {div , class="jb-date col p0x p0t t-mute"} then {span}

from undetected_playwright.sync_api import sync_playwright

import time
import sqlite3 
import os 
from urllib.parse import urljoin
import random
from fake_useragent import UserAgent
import re
import sys
from urllib.parse import quote
import io

import subprocess
def run_scraper() :
    #subprocess.run(['python', '-m', 'playwright', 'install', 'chromium'], check=True)

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # قراءة اسم الوظيفة من سطر الأوامر
    if len(sys.argv) > 1:
        searche = sys.argv[1]
    else:
        searche = 'python'  # قيمة افتراضية

    # استخدم المسار النسبي فقط (سيعمل في السحابة)
    #file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'JOBS.db')
    #status_file_path = 'status.text'
    #status_errors_file_path = 'status_errors_file.text'

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'JOBS.db')
    status_file_path = os.path.join(base_dir, 'status.text')
    status_errors_file_path = os.path.join(base_dir, 'status_errors_file.text')

    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    def save_jobs_to_db(jobs_list) :
        cursor.executemany('''
    INSERT INTO jobs(Job_Title , The_company , Description , Location , Published_date , job_url) VALUES (?,?,?,?,?,?)
    ''' , jobs_list)
        conn.commit()
        
    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    user_agent = ua.random

    all_jobs_list = []

    filter_jobs_with_date_max = 10
    page_number = 1
    with sync_playwright() as p :
        with open(status_file_path , 'w' , encoding='utf-8') as f :
            f.write('running')

        with open(status_errors_file_path, 'w' , encoding='utf-8') as f:
            f.write(f"looking for a '{searche}' job")

        # تمرير أمر لـ Chromium لبدء النافذة مصغرة
        # الطريقة الصحيحة لاستخدام undetected_playwright

        browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process,BlockInsecurePrivateNetworkRequests',
            '--disable-gpu',
            '--window-size=1920,1080'
        ]
        )
    
        context = browser.new_context(
        user_agent=user_agent,
        viewport={'width': 1920, 'height': 1080},
        locale='en-US'
        )

        page = context.new_page()

        # سكربت إخفاء الأتمتة (ضعه قبل page.goto)
        # حقن سكربت إضافي لإخفاء علامات الأتمتة
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        link = f'https://www.bayt.com/en/international/jobs/{quote(searche)}-jobs/' 
        try :
            page.goto(link , timeout=30000)
            time.sleep(random.uniform(2, 5))
        except Exception as e :

            print(f"We cann't open the first page : we have a problem : {e}")
            
            
        
        while True :
            
            try :
                page.wait_for_selector('li.has-pointer-d' , timeout=15000)
            except :
                
                print("Sorry ,The items are not displayed on the page , we don't have any jobs with that name")
                break

            jobs = page.query_selector_all('li.has-pointer-d')
            for job in jobs :
                
                # تحريك الفأرة عشوائياً
                page.mouse.move(
                    random.randint(100, 500),
                    random.randint(100, 500)
                )

                job_title = job.query_selector('h2.t-large-d a')
                job_url = job_title.get_attribute('href')
                if job_url:
                    job_url = urljoin(link, job_url)
                else :
                    job_url = 'Unknown'

                companie = job.query_selector('div.job-company-location-wrapper div a')
                summarie = job.query_selector('div.jb-descr')
                location = job.query_selector('dt.p0.m20r.jb-label-location.job-company-location-wrapper')
                date = job.query_selector('div.jb-date')
                

                if job_title :
                    job_title = job_title.inner_text().strip()
                else :
                    job_title = 'Unknown'
                
                if companie :
                    companie = companie.inner_text().strip()
                else :
                    companie = 'Unknown'
                
                if summarie :
                    summarie = summarie.inner_text().strip()
                else :
                    summarie = 'Unknown'
                
                if location :
                    location = location.inner_text().strip()
                else :
                    location = 'Unknown'
                
                if date :
                    date = date.inner_text().strip()
                else :
                    date = 'Unknown'  

                # '^'	تعني "بداية النص فقط". تضمن عدم سحب أي رقم يظهر في منتصف أو نهاية النص.
                match = re.match(r'\d+',date)
                if match :
                    day_ago = int(match.group())
                    if day_ago <= filter_jobs_with_date_max :
                        all_jobs_list.append([job_title, companie , summarie , location , date , job_url])

                elif 'today' in date.lower() or 'yesterday' in date.lower() :
                    all_jobs_list.append([job_title, companie , summarie , location , date , job_url])
                
            
            print(f'saving the jobs from page number: {page_number} is done.')
            
            try:
                the_last_page = page.query_selector('li.pagination-next.u-none a')
            except:
                pass
            if the_last_page:
                break

            next_li = page.query_selector('li.pagination-next')
            if next_li:
                next_link = next_li.query_selector('a')
                if next_link:
                    href = next_link.get_attribute('href')
                    link = urljoin(link, href)
                    page.goto(link)
                    time.sleep(random.uniform(2, 5))
                    page_number += 1
                else:
                    break
            else:
                break

        if all_jobs_list:

            cursor.execute('DROP TABLE IF EXISTS jobs')
            cursor.execute('''CREATE TABLE IF NOT EXISTS jobs(
        
                    Job_Title TEXT,
                    The_company TEXT,
                    Description TEXT,
                    Location TEXT,
                    Published_date TEXT,
                    job_url TEXT,
                    ID INTEGER PRIMARY KEY AUTOINCREMENT)''')

            save_jobs_to_db(all_jobs_list)

            print(f"✅ تم العثور على {len(all_jobs_list)} وظيفة.")

            with open(status_errors_file_path, 'w' , encoding='utf-8') as f:
                f.write(f"✅ تم العثور على {len(all_jobs_list)} وظيفة.")

            with open(status_file_path, 'w' , encoding='utf-8') as f:
                f.write('done')
        else:
            with open(status_errors_file_path, 'w' , encoding='utf-8') as f:
                f.write(f"We don't have any jobs with this nam {searche}")

            with open(status_file_path, 'w' , encoding='utf-8') as f:
                f.write('error')

            print("❌ لا توجد وظائف مطابقة للبحث.")

    # لا تكتب 'done' في status_errors_file_path هنا   
        context.close()
        conn.close()

if __name__ == '__main__' :
    run_scraper()
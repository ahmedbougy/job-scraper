#jobs is in {ul , class="media-list in-card is-spaced is-divided is-reversed has-hover-d has-rects has-free-img bb" data-empty="Nothing available"}
    #evry job has : {li data-js-job class="has-pointer-d"} but with defrent {data-job-id = ?}
        # the furst enfo is in : {div , class="row is-m no-wrap v-align-center"} then {dive , class="u-flex t-small u-stretch p10l"} then {div , class="u-stretch"} then {h2 , class="t-large-d t-small m0t m5b" , a}
        #the summary is in {div , class="jb-descr m10t t-small"}
 
        #the location is in : {div , class="jb-tags m10t"} then {dl , class="dlist is-spaced t-small m0y row"} then {dt , class="p0 m20r jb-label-location job-company-location-wrapper"} then {a , class="t-default"} then {span}.
            #the second part of location is in : the same {dt} but in the end {a class="t-default"} then {span}

        #the date is in : {div , class="jb-footer row is-m v-align-center m10t"} then {div , class="jb-date col p0x p0t t-mute"} then {span}

#from playwright.sync_api import sync_playwright
from patchright.sync_api import sync_playwright

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

emergency_jobs = [
    # 1 - 5
    ("Python Backend Developer", "TechSolutions Inc.", "Looking for a skilled Python developer experienced with Flask and SQLite to build scalable APIs.", "Algiers, Algeria", "1 day ago", "https://example.com/job/1"),
    ("Data Analyst", "Global Data Corp", "Analyze large datasets using Python, SQL, and Pandas. Experience with data visualization is required.", "Dubai, UAE", "2 days ago", "https://example.com/job/2"),
    ("Web Scraping Specialist", "DataExtract Co.", "Responsibility includes building robust web scrapers using Playwright, BeautifulSoup, and Selenium.", "Remote", "Today", "https://example.com/job/3"),
    ("Frontend Developer", "Creative Web Studios", "Seeking a React/Vue.js frontend developer to build responsive and modern user interfaces.", "Riyadh, Saudi Arabia", "3 days ago", "https://example.com/job/4"),
    ("Full Stack Engineer", "InnovateTech Solutions", "Develop end-to-end web applications using Python Flask, PostgreSQL, and JavaScript.", "Cairo, Egypt", "Yesterday", "https://example.com/job/5"),

    # 6 - 10
    ("DevOps Engineer", "CloudScale Systems", "Manage AWS infrastructure, CI/CD pipelines, Docker containers, and Kubernetes clusters.", "Oran, Algeria", "4 days ago", "https://example.com/job/6"),
    ("Cybersecurity Analyst", "SecureNet Logistics", "Monitor networks for security breaches, perform vulnerability testing, and patch systems.", "Doha, Qatar", "2 days ago", "https://example.com/job/7"),
    ("AI / ML Engineer", "Neural Mind AI", "Train machine learning models using PyTorch and TensorFlow for NLP and predictive tasks.", "Remote", "Today", "https://example.com/job/8"),
    ("Database Administrator", "FinTech Bank", "Maintain and optimize SQLite, MySQL, and PostgreSQL databases for high performance.", "Casablanca, Morocco", "5 days ago", "https://example.com/job/9"),
    ("UI/UX Designer", "Pixel Studio", "Design wireframes, prototypes, and sleek mobile/web app interfaces using Figma.", "Tunis, Tunisia", "Yesterday", "https://example.com/job/10"),

    # 11 - 15
    ("Software QA Tester", "QualityFirst Labs", "Write automated end-to-end integration tests using Python and Playwright.", "Amman, Jordan", "1 day ago", "https://example.com/job/11"),
    ("Mobile App Developer", "AppNation Studio", "Build cross-platform mobile applications using Flutter and Dart.", "Constantine, Algeria", "6 days ago", "https://example.com/job/12"),
    ("SEO & Content Manager", "Digital Marketing Hub", "Optimize website ranking, perform keyword research, and track site analytics.", "Dubai, UAE", "3 days ago", "https://example.com/job/13"),
    ("Technical Support Specialist", "HelpDesk 24/7", "Provide Level 2 technical support for web software applications and servers.", "Riyadh, Saudi Arabia", "Today", "https://example.com/job/14"),
    ("Embedded Systems Engineer", "AutoTech Systems", "Program microcontrollers using C/C++ and integrate IoT hardware modules.", "Sétif, Algeria", "7 days ago", "https://example.com/job/15"),

    # 16 - 20
    ("Graphic Designer", "Visual Dynamics", "Create promotional banners, brand logos, and marketing graphics using Photoshop and Illustrator.", "Cairo, Egypt", "2 days ago", "https://example.com/job/16"),
    ("Cloud Solutions Architect", "Skyline Cloud Services", "Design secure cloud architecture strategies for enterprise-level clients.", "Remote", "Yesterday", "https://example.com/job/17"),
    ("Automation Engineer", "RoboProcess Solutions", "Automate daily business processes using Python scripts and RPA tools.", "Abu Dhabi, UAE", "4 days ago", "https://example.com/job/18"),
    ("Systems Administrator", "Enterprise IT Partners", "Configure Linux/Windows servers, manage user access, and oversee network hardware.", "Algiers, Algeria", "5 days ago", "https://example.com/job/19"),
    ("Product Manager", "NextGen Apps", "Define product roadmaps, organize developer sprints, and collaborate with UI teams.", "Remote", "1 day ago", "https://example.com/job/20"),

    # 21 - 25
    ("Junior Python Developer", "StartUp Hub", "Great opportunity for beginners to work with Flask, SQLite, and Git version control.", "Annaba, Algeria", "Today", "https://example.com/job/21"),
    ("Network Engineer", "Cisco NetWorks", "Design, implement, and maintain local and wide area network infrastructure.", "Muscat, Oman", "8 days ago", "https://example.com/job/22"),
    ("Scrum Master", "Agile Teamwork Co.", "Facilitate daily stand-up meetings, sprint planning, and remove project blockers.", "Riyadh, Saudi Arabia", "3 days ago", "https://example.com/job/23"),
    ("Technical Writer", "DocuTech Publications", "Write clean technical documentation, API guides, and software manuals.", "Remote", "2 days ago", "https://example.com/job/24"),
    ("Game Developer (Pygame)", "Pixel Arcade", "Develop 2D indie games using Python and Pygame engine for Desktop.", "Oran, Algeria", "Yesterday", "https://example.com/job/25"),

    # 26 - 30
    ("IT Project Manager", "Global Tech Services", "Oversee IT project budgets, timelines, team communication, and deliverables.", "Doha, Qatar", "4 days ago", "https://example.com/job/26"),
    ("Data Engineer", "BigData Infrastructure", "Build reliable data pipelines, ETL processes, and data warehouse connections.", "Remote", "Today", "https://example.com/job/27"),
    ("Security Operations Specialist", "CyberDefense Corp", "Identify threat patterns, investigate security events, and audit software code.", "Algiers, Algeria", "6 days ago", "https://example.com/job/28"),
    ("E-commerce Manager", "ShopOnline Stores", "Manage online store catalog, inventory integration, and customer funnels.", "Dubai, UAE", "5 days ago", "https://example.com/job/29"),
    ("Computer Vision Researcher", "VisionAI Labs", "Develop image recognition algorithms using OpenCV and deep learning models.", "Remote", "1 day ago", "https://example.com/job/30")
]

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
        headless=False,
        channel='chrome',
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process,BlockInsecurePrivateNetworkRequests',
            '--disable-gpu',
            '--window-size=1920,1080'
            '--disable-features=IsolateOrigins,site-per-process',
            '--start-maximized'
        ]
        )
    
        context = browser.new_context(
        no_viewport=True,
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
                match = re.search(r'\d+', date)
                if match :
                    day_ago = int(match.group())
                    if day_ago <= filter_jobs_with_date_max :
                        all_jobs_list.append([job_title, companie , summarie , location , date , job_url])

                elif 'today' in date.lower() or 'yesterday' in date.lower() :
                    all_jobs_list.append([job_title, companie , summarie , location , date , job_url])
                
            
            print(f'saving the jobs from page number: {page_number} is done.')

            # ===== محاكاة السلوك البشري قبل الانتقال =====
            # تمرير عشوائي
            for _ in range(random.randint(2, 4)):
                page.mouse.wheel(0, random.randint(200, 600))
                time.sleep(random.uniform(0.5, 1.5))

            # حركة فأرة عشوائية
            for _ in range(random.randint(3, 6)):
                page.mouse.move(
                    random.randint(100, 1800),
                    random.randint(100, 900)
                )
                time.sleep(random.uniform(0.3, 0.8))

            # انتظار عشوائي طويل (8-15 ثانية)
            time.sleep(random.uniform(8, 15))
            
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


        cursor.execute('DROP TABLE IF EXISTS jobs')
        cursor.execute('''CREATE TABLE IF NOT EXISTS jobs(
                
                            Job_Title TEXT,
                            The_company TEXT,
                            Description TEXT,
                            Location TEXT,
                            Published_date TEXT,
                            job_url TEXT,
                            ID INTEGER PRIMARY KEY AUTOINCREMENT)''')
        
        if all_jobs_list and page_number >= 3:

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
            print('تم استخذام الوظائف من القائمة الاحتياطية')
            save_jobs_to_db(emergency_jobs)


    # لا تكتب 'done' في status_errors_file_path هنا   
        context.close()
        conn.close()

if __name__ == '__main__' :
    run_scraper()
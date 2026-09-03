
from flask import Flask, render_template, request
import os
import sqlite3
import subprocess
from flask import flash, redirect, url_for

from playwright.sync_api import sync_playwright
import time

from urllib.parse import urljoin
import random
from fake_useragent import UserAgent
import re
import sys
from urllib.parse import quote
import io

import subprocess
def run_scraper(job_title):
    try:
        
        subprocess.run(['playwright', 'install', 'chromium'], check=True)

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


        # استخدم المسار النسبي فقط (سيعمل في السحابة)
        file_path = 'JOBS.db'
        status_file_path = 'status.text'
        status_errors_file_path = 'status_errors_file.text'

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
                f.write(f"looking for a '{job_title}' job")

            # تمرير أمر لـ Chromium لبدء النافذة مصغرة
            browser = p.chromium.launch(
                headless=True,
                args=[
                '--window-position=-2000,-2000',  # وضع النافذة في مكان خارج نطاق الشاشة تماماً
                '--window-size=1280,720'
            ]
            )
            
            context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
            )
            page = context.new_page()

            # سكربت إخفاء الأتمتة (ضعه قبل page.goto)
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            link = f'https://www.bayt.com/en/international/jobs/{quote(job_title)}-jobs/' 
            try :
                page.goto(link , timeout=30000)
                time.sleep(random.uniform(2, 5))
            except Exception as e :

                print(f"We cann't open the first page : we have a problem : {e}")
                
                
            
            while True :
                try :
                    page.wait_for_selector('div.card.t-center.p0',timeout=15000)
                    break
                except :
                    pass

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
                
                try :
                    the_last_page = page.query_selector('li.pagination-next.u-none a')
                except :
                    pass
                if the_last_page :
                    break
                
                
                next_li = page.query_selector('li.pagination-next')
                if next_li :
                    next_link = next_li.query_selector('a')
                    if next_link :
                        href = next_link.get_attribute('href')
                        link = urljoin(link , href)
                        try:
                            page.goto(link, timeout=60000) # زيادة مهلة الانتظار لـ 60 ثانية
                            time.sleep(random.uniform(2, 5))
                            page_number += 1
                        except Exception as e:
                            print(f"حدث خطأ شبكة أثناء فتح الصفحة {link}: {e}")
                            print("إعادة المحاولة بعد 10 ثوانٍ...")
                            time.sleep(10)
                            try:
                                page.goto(link, timeout=60000)
                                page_number += 1
                            except Exception:
                                
                                break
                    
                else :
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
                    f.write(f"We don't have any jobs with this nam {job_title}")

                with open(status_file_path, 'w' , encoding='utf-8') as f:
                    f.write('error')

                print("❌ لا توجد وظائف مطابقة للبحث.")

        # لا تكتب 'done' في status_errors_file_path هنا   
            context.close()
            conn.close()
    except Exception as e:
        print(f"❌ خطأ في السحب: {e}")
        return False



scraper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper.py')

app = Flask(__name__)
app.secret_key = 'abdelsselam10pyhton'

# دالة مساعدة لجلب مسار قاعدة البيانات لتفادي تكرار الكود
def get_db_connection():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JOBS.db')
    conn = sqlite3.connect(file_path)
    return conn

@app.route('/')
def jobsinfo():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    page = request.args.get('page', 1 , type=int)
    per_page = 12
    offset = (page - 1) * per_page
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = cursor.fetchone()[0]
    total_pages = (total_jobs + (per_page - 1)) // per_page
    
    cursor.execute('SELECT * FROM jobs LIMIT ? OFFSET ?',(per_page , offset))
    rows = cursor.fetchall()
    conn.close()
    dectionary_jobs_list = [
        {
            'Job_Title': row[0],
            'The_company': row[1],
            'Description': row[2],
            'Location': row[3],
            'Published_date': row[4],
            'job_url': row[5],
            'job_id': row[6]
            
        }
        for row in rows
    ]
    return render_template(
        'index.html', 
        jobs=dectionary_jobs_list,
        page=page,
        total_pages=total_pages,
        total_jobs=total_jobs
        )

@app.route('/job/<int:job_id>')
def job_details(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE ID = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        dectionary_job_details = {
            'Job_Title': row[0],
            'The_company': row[1],
            'Description': row[2],
            'Location': row[3],
            'Published_date': row[4],
            'job_url': row[5],
            'job_id': row[6]
        }
        return render_template('job_details.html', job=dectionary_job_details)
    else:
        return render_template('wrong.html')

@app.route('/search')
def search():
    page = request.args.get('page', 1 , type=int)
    per_page = 12
    offset = (page - 1) * per_page
    q = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    company = request.args.get('company', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if q:
        conditions.append("Job_Title LIKE ?")
        params.append(f'%{q}%')
    if location:
        conditions.append("Location LIKE ?")
        params.append(f'%{location}%')
    if company:
        conditions.append("The_company LIKE ?")
        params.append(f'%{company}%')


    if conditions:
        query = "SELECT * FROM jobs WHERE " + " AND ".join(conditions)
        count_query = "SELECT COUNT(*) FROM jobs WHERE " + " AND ".join(conditions)

    else:
        query = "SELECT * FROM jobs"
        count_query = "SELECT COUNT(*) FROM jobs"

    cursor.execute(count_query, params)

    total_jobs = cursor.fetchone()[0]
    total_pages = (total_jobs + per_page - 1) // per_page

    cursor.execute(query+" LIMIT ? OFFSET ?", params + [per_page , offset])
    rows = cursor.fetchall()
    conn.close()  # إغلاق واحد فقط هنا

    dectionary_search = [
        {
            'Job_Title': row[0],
            'The_company': row[1],
            'Description': row[2],
            'Location': row[3],
            'Published_date': row[4],
            'job_url': row[5],
            'job_id': row[6]
        }
        for row in rows
    ]

    return render_template(
        'index.html', 
        jobs=dectionary_search, 
        page=page, 
        total_pages=total_pages, 
        total_jobs=total_jobs,
        search_query=q, 
        location=location, 
        company=company
    )

@app.route('/update' , methods=['GET','POST'])
def update_jobs() :
    if request.method == 'POST' :
        job_title = request.form.get('job_title','python').strip()
        if not job_title :
            flash('❌ الرجاء إدخال اسم وظيفة صحيح.', 'danger')
            return redirect(url_for('jobsinfo'))
        
    if run_scraper(job_title):
        flash(f'✅ تم تحديث البيانات للوظيفة: "{job_title}" بنجاح.', 'success')
    else:
        flash(f'❌ فشل تحديث البيانات للوظيفة: "{job_title}".', 'danger')

    return redirect(url_for('jobsinfo'))

@app.route('/status')
def get_status():
    status_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'status.text')
    status_errors_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'status_errors_file.text')

    try :
        with open(status_errors_file_path,'r',encoding='utf-8') as f :
            status_no_fond_jobs = f.read().strip()
            if "We don't have any jobs" in status_no_fond_jobs :
                return 'no_jobs'
           
    except FileNotFoundError :
        pass

    try :
        with open(status_file_path,'r',encoding='utf-8') as f :
            status = f.read().strip()
            return status
    except FileNotFoundError :
        return 'idle'
    
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=10000)


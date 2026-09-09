from flask import Flask, render_template, request
import os
import sqlite3
import subprocess
from flask import flash, redirect, url_for
import subprocess

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
        
    try:
        # تشغيل السكربت في الخلفية مع تمرير اسم الوظيفة
        subprocess.Popen(['python', scraper_path, job_title], shell=True)
        flash(f'✅ بدأ تحديث البيانات للوظيفة: "{job_title}" في الخلفية.', 'success')
    except Exception as e:
        flash(f'❌ فشل تشغيل التحديث: {e}', 'danger')

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

subprocess
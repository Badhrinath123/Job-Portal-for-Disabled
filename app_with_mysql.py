from mailbox import Message
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
import smtplib
from email.mime.text import MIMEText
import os
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'secret_key_here'  # Add a secret key for session

def get_db_connection():
    print("Establishing database connection") 
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='employer'
    )
    return connection


def send_otp(email, otp):
    sender = 'tillureddy382@gmail.com'
    password = 'pxov hsqt ywca wuar'
    subject = 'Your OTP Code'
    body = f'Your OTP code is {otp}'
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

@app.route('/sendotp', methods=['POST', 'GET'])
def sendotp():
    if request.method == 'POST':
        print(f"Form data received: {request.form}")
        email = request.form.get('email')  # Use .get() to avoid KeyError
        if email:
            otp = generate_otp()
            print(f"Generated OTP: {otp}")
            send_otp(email, otp)
            session['otp'] = otp
            session['email'] = email
            flash('OTP sent to your email address.', 'success')
            return redirect(url_for('verifyotp'))
        else:
            flash('Please enter a valid email address.', 'error')
    return render_template('forgot password.html')
    
def send_otp_email(email, otp):
    msg = Message('Your OTP', sender='tillureddy382@gmail.com', recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    try:
        email.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}") 

# Route for verifying OTP
@app.route('/verifyotp', methods=['GET', 'POST'])
def verifyotp():
    if request.method == 'POST':
        try:
            otp1 = request.form['otp1']
            otp2 = request.form['otp2']
            otp3 = request.form['otp3']
            otp4 = request.form['otp4']
            otp5 = request.form['otp5']
            otp6 = request.form['otp6']
            
            # Concatenate OTP parts into a single OTP string
            otp = otp1 + otp2 + otp3 + otp4 + otp5 + otp6
            
            stored_otp = session.get('otp')
            
            if otp == stored_otp:
                flash('OTP verified successfully.', 'success')
                return redirect(url_for('newpassword'))
            else:
                flash('Invalid OTP. Please try again.', 'danger')
        
        except KeyError:
            flash('Invalid form submission. Please enter OTP.', 'danger')
    
    return render_template('email.html')

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.json.get('otp')
        
        user_email = session.get('email')  # Assuming user email is stored in session
        stored_otp = session.get('otp')    # Get the OTP from session
        
        if stored_otp and entered_otp == stored_otp:
            # OTP matched, perform further actions (e.g., mark email as verified)
            session.pop('otp', None)  # Clear OTP from session after successful verification
            
            return jsonify(success=True, message='OTP verified successfully')
        
        # Handle case where OTP does not match
        return jsonify(success=False, error='Invalid OTP')

    return jsonify(success=False, error='Method not allowed'), 405

@app.route('/resend_otp', methods=['GET', 'POST'])
def resend_otp():
    if 'email' in session:
        email = session['email']
        print(email)
        otp = generate_otp()
        
        # Send the OTP via email
        msg = Message('Your OTP Code', sender='tillureddy382@gmail.com', recipients=[email])
        msg.body = f'Your OTP code is {otp}'
        email.send(msg)  # Assuming mail is your Flask-Mail instance
        
        # Update OTP in session
        session['otp'] = otp

        flash('A new OTP has been sent to your email.', 'success')
        return redirect(url_for('verifyotp'))  # Assuming you have a verifyotp endpoint

    flash('You need to log in first.', 'danger')
    return redirect(url_for('login'))

def validate_user(email, password):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET']) 
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')
        user = validate_user(email, password)
        if user:
            session['email'] = user['email']  # Store user email in session
            if user['user_type'] == 'employee':
                return jsonify(success=True, redirect_url=url_for('employeedashboard'))
            elif user['user_type'] == 'employer':
                return jsonify(success=True, redirect_url=url_for('employerdashboard'))
        else:
            return jsonify(success=False, error='Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def dashboardsignup():
    return render_template("dashboardsignup.html")

@app.route('/forgotpassword', methods=['GET'])
def forgotpassword():
    return render_template("forgot password.html")

@app.route('/employersignup', methods=['GET', 'POST'])
def employersignup():
    if request.method == 'POST':
        company_name = request.form.get('CompanyName')
        company_contact = request.form.get('mobileNumber')
        company_email = request.form.get('email')
        company_size = request.form.get('company_size')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        if password != confirm_password:
            return "Passwords do not match", 400

        password_hash = generate_password_hash(password)

        # Connect to MySQL and insert data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (
                email, password_hash, user_type, first_name, last_name,
                mobile_number, country, state, address,
                company_name, company_contact, company_size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (company_email, password_hash, 'employer', first_name, last_name,
              company_contact, '', '', '', company_name, company_contact, company_size))
        conn.commit()
        cursor.close()
        conn.close()
        
        otp = generate_otp()
        print(f"Generated OTP: {otp}")
        send_otp(company_email, otp)
        
        session['otp'] = otp  # Store OTP in session for verification
        session['email'] = company_email  # Store email in session for verification
        
        return redirect(url_for('emailverificationforsignup'))

    return render_template("employer signup.html")

@app.route('/employersignupb', methods=['GET'])
def employersignupb():
    return redirect(url_for('employersignup'))

@app.route('/employeesignup', methods=['GET','POST'])
def employeesignup():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        mobile_number = request.form.get('mobileNumber')
        country = request.form.get('country')
        state = request.form.get('state')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        if password != confirm_password:
            return "Passwords do not match", 400

        password_hash = generate_password_hash(password)

        # Connect to MySQL and insert data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (
                email, password_hash, user_type, first_name, last_name,
                mobile_number, country, state, address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, password_hash, 'employee', first_name, last_name,
              mobile_number, country, state, address))
        conn.commit()
        cursor.close()
        conn.close()
        
        otp = generate_otp()
        send_otp(email, otp)
        
        session['otp'] = otp  # Store OTP in session for verification
        session['email'] = email  # Store email in session for verification
        
        return redirect(url_for('emailverificationforsignup'))

    return render_template("signup.html")

@app.route('/employeesignupb', methods=['GET'])
def signupb():
    return redirect(url_for('employeesignup'))

@app.route('/newpassword', methods=['GET'])
def newpassword():
    return render_template('new password.html')


@app.route('/newpassword', methods=['POST','GET'])
def newpasswordp():

    if 'email' in session:
        flash('Email is stored in session: ' + session['email'], 'info')
        print("Email in session:", session['email'])
    else:
        flash('Email is not stored in session', 'danger')
        print("Email is not in session")

    if request.method == 'POST':
        print("Form data received:", request.form)
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password is None or confirm_password is None:
            flash('Please enter both new password and confirm password', 'danger')
            return redirect(url_for('newpassword'))
        
        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('newpassword'))
        
        hashed_password = generate_password_hash(new_password)
        email = session.get('email')
        if email:
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                cursor.execute('UPDATE users SET password_hash = %s WHERE email = %s', (hashed_password, email))
                connection.commit()
                flash('Your new password has been set successfully. Please login with your new password.', 'success')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'danger')
            finally:
                cursor.close()
                connection.close()
                session.pop('email', None)
                return redirect(url_for('login'))
        else:
            flash('Session expired. Please try again.', 'danger')
            return redirect(url_for('forgotpassword'))

    return render_template('new password.html')

@app.route('/resetpassword', methods=['POST'])
def resetpassword():
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']
    
    if new_password and new_password == confirm_password:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('newpasswordp'))



@app.route('/companies')
def companiesb():
    return render_template('companies.html')

@app.route('/companiesb', methods=['GET'])
def companies():
    return redirect(url_for('companiesb'))

@app.route('/jobs')
def jobsb():
    return render_template('jobs.html')

@app.route('/jobsb', methods=['GET'])
def jobs():
    return redirect(url_for('jobsb'))

@app.route('/services')
def servicesb():
    return render_template('services.html')

@app.route('/servicesb', methods=['GET'])
def services():
    return redirect(url_for('servicesb'))

@app.route('/contactus')
def contactusb():
    return render_template("contact.html")

@app.route('/employercontactus')
def contactus():
    return render_template("contactus.html")

@app.route('/feedback')
def feedback():
    return render_template("feedback.html")

@app.route('/email')
def email():
    return redirect(url_for('emailverification'))

@app.route('/emailverification')
def emailverification():
    return render_template("email.html")

@app.route('/emailforsignup')
def emailforsignup():
    return redirect(url_for('emailverificationforsignup'))

@app.route('/emailverificationforsignup', methods=['GET', 'POST'])
def emailverificationforsignup():
    if request.method == 'POST':
        # Combine the OTP parts from the form
        otp = ''.join([request.form.get(f'otp{i}') for i in range(1, 7)])
        
        print(f"Entered OTP: {otp}")
        
        # Retrieve the correct OTP stored in session
        correct_otp = session.get('otp')
        
        print(f"Correct OTP: {correct_otp}")
        
        # Validate OTP
        if otp.strip() == correct_otp:
            flash('Successfully verified!', 'success')
            session.pop('otp')  # Remove OTP from session after verification
            return redirect(url_for('login'))
        else:
            flash('Incorrect OTP. Please try again.', 'error')
            print('OTP validation failed:', otp, correct_otp)  # Debugging output

    # Resend OTP functionality
    if request.form.get('resend_otp'):
        email = session.get('email')
        otp = generate_otp()
        print(f"Resent OTP: {otp}")
        send_otp(email, otp)
        session['otp'] = otp  # Update OTP in session
        flash('OTP resent successfully!', 'success')

    return render_template('emailforsignup.html')

@app.route('/submit-job', methods=['POST'])
def submit_job():
    company_name = request.form['company-name']
    job_role = request.form['job-role']
    experience_years = request.form['experience-years']
    experience_months = request.form['experience-months']
    salary = request.form['salary']
    mode = request.form['mode']
    technology_stack = request.form['technology-stack']
    comp_loc = request.form['comp-loc']
    job_description = request.form['job-description']
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert data into the table
    insert_query = '''
        INSERT INTO job_posts (company_name, job_role, experience_years, experience_months, salary, mode, technology_stack, company_location, job_description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (company_name, job_role, experience_years, experience_months, salary, mode, technology_stack, comp_loc, job_description))

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('employerdashboard'))

# 2 means employer

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/employerabout')
def employerabout():
    return render_template('employerabout.html')

@app.route('/searchresults')
def searchresults():
   return render_template('searchresults.html')

@app.route('/searchresultsb',methods=['GET'])
def searchresultsb():
   return redirect(url_for('searchresults'))

@app.route('/employerdashboard', methods=['GET'])
def employerdashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('employerdb.html', email=session['email'])

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/employerpostjob',methods=['GET'])
def employerpostjob():
   return render_template('postjob.html')

@app.route('/employerjobposted',methods=['GET'])
def employerjobposted():
    job_posts = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_posts")
        job_posts = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error: ", e)
    return render_template('jobsposted.html', job_posts=job_posts)

@app.route('/employerreports',methods=['GET'])
def employerreports():
   return render_template('reports.html')

@app.route('/employershortlisted')
def employershortlisted():
    db_connection = get_db_connection()
    cursor = db_connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM shortlisted_candidates")
    shortlisted = cursor.fetchall()
    
    cursor.close()
    db_connection.close()
    
    return render_template('shortlisted.html', shortlisted=shortlisted)

@app.route('/employeedashboard',methods=['GET'])
def employeedashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('employeedb.html', email=session['email'])


@app.route('/employeefindjobs')
def employeefindjobs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT company_name, job_role, company_location, technology_stack, experience_years, salary FROM job_posts')
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('findjobs.html', job_posts=job_posts)


@app.route('/employeejobsapplied',methods=['GET'])
def employeejobsapplied():
   return render_template('jobsapplied.html')

@app.route('/employeejobsstatus',methods=['GET'])
def employeejobsstatus():
   return render_template('jobsstatus.html')




@app.route('/employeecontactus',methods=['GET'])
def employeecontactus():
   return render_template('employeecontactus.html')

@app.route('/jobcard1',methods=['GET'])
def employeejobcard1():
   return render_template('jobcard1.html')

@app.route('/jobcard2',methods=['GET'])
def employeejobcard2():
   return render_template('jobcard2.html')

@app.route('/jobcard3',methods=['GET'])
def employeejobcard3():
   return render_template('jobcard3.html')

@app.route('/jobcard4',methods=['GET'])
def employeejobcard4():
   return render_template('jobcard4.html')

@app.route('/jobcard5',methods=['GET'])
def employeejobcard5():
   return render_template('jobcard5.html')

@app.route('/employeeprofile', methods=['GET'])
def employeeprofile():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user:
        cursor.execute('SELECT * FROM profile WHERE id = %s', (user['id'],))
        profile = cursor.fetchone()
    else:
        profile = None

    cursor.close()
    conn.close()

    if not user:
        return redirect(url_for('login'))  # Redirect to login if user is not found

    return render_template('profile.html', user=user, profile=profile)

@app.route('/updateprofile', methods=['POST', 'GET'])
def updateprofile():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = session['email']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    
    if not user:
        return redirect(url_for('login'))  # Redirect to login if user is not found
    
    user_id = user['id']

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        experience = request.form.get('experience')
        skills = request.form.get('skills')

        try:
            # Update users table
            update_user_query = '''
            UPDATE users
            SET first_name = %s, last_name = %s, email = %s, mobile_number = %s
            WHERE id = %s
            '''
            cursor.execute(update_user_query, (first_name, last_name, email, mobile_number, user_id))

            # Check if profile exists for the user
            cursor.execute('SELECT COUNT(*) FROM profile WHERE id = %s', (user_id,))
            profile_exists = cursor.fetchone()['COUNT(*)']

            if profile_exists:
                # Update profile table
                update_profile_query = '''
                UPDATE profile
                SET experience = %s, skills = %s
                WHERE id = %s
                '''
                cursor.execute(update_profile_query, (experience, skills, user_id))
            else:
                # If profile does not exist, insert a new record
                insert_profile_query = '''
                INSERT INTO profile (id, experience, skills)
                VALUES (%s, %s, %s)
                '''
                cursor.execute(insert_profile_query, (user_id, experience, skills))

            # Commit the transaction
            conn.commit()
            return redirect(url_for('employeeprofile'))

        except Exception as e:
            conn.rollback()
            print(f"Error updating profile: {str(e)}")
            return "An error occurred while updating the profile", 500

        finally:
            cursor.close()
            conn.close()

    # Fetch existing data to pre-fill the form
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.execute('SELECT * FROM profile WHERE id = %s', (user_id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('updateprofile.html', user=user, profile=profile)

@app.route('/delete_job', methods=['POST'])
def delete_job():
    job_id = request.json.get('id')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Delete related rows in job_log1 table
            delete_related_query = "DELETE FROM job_log2 WHERE job_id = %s"
            cursor.execute(delete_related_query, (job_id,))
            
            # Delete the job post
            delete_query = "DELETE FROM job_posts WHERE id = %s"
            cursor.execute(delete_query, (job_id,))
            conn.commit()
            print(f"Job with id {job_id} deleted successfully")
            return jsonify({'status': 'success'})
        except mysql.connector.Error as e:
            print(f"Error deleting data: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

@app.route('/update_job', methods=['POST'])
def update_job():
    data = request.json
    job_id = data.get('id')
    company_name = data.get('company_name')
    job_role = data.get('job_role')
    experience_years = data.get('experience_years')
    experience_months = data.get('experience_months')
    salary = data.get('salary')
    mode = data.get('mode')
    technology_stack = data.get('technology_stack')
    company_location = data.get('company_location')
    job_description = data.get('job_description')

    print("Received data for update:", data)

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            update_query = '''
                UPDATE job_posts
                SET company_name = %s, job_role = %s, experience_years = %s, experience_months = %s, salary = %s, mode = %s,
                    technology_stack = %s, company_location = %s, job_description = %s
                WHERE id = %s
            '''
            cursor.execute(update_query, (company_name, job_role, experience_years, experience_months, salary, mode,
                                          technology_stack, company_location, job_description, job_id))
            conn.commit()
            print("Update query executed successfully")
        except Error as e:
            print(f"Error updating data: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'status': 'error', 'message': 'Failed to connect to the database'})

    return jsonify({'status': 'success'})

def get_job_postings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM job_posts")
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return jobs

@app.route('/api/jobposted', methods=['GET'])
def jobsposted():
    jobs = get_job_postings()
    return jsonify(jobs)



if __name__ == '__main__':
    app.run(debug=True)



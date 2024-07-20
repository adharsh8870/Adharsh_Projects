from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your secret key'

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Avanthi@8870',
        database='hospital'
    )
    return connection

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name= request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        sex = request.form['sex']
        date = request.form['date']
        message = request.form['message']

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO appointment (first_name, last_name, email_id, mobile_no, sex, appointment_date, reason) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, mobile, sex, date, message)
            )
            connection.commit()
            flash('Appointment added successfully!')
            return redirect(url_for('index'))
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            flash('An error occurred. Please try again later.')
        finally:
            cursor.close()
            connection.close()
    return render_template('add_appointment.html')

@app.route('/appointments')
def appointments():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointment")
    appointments = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('display.html', appointments=appointments)

@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointment WHERE appointment_id = %s", (appointment_id,))
    appointment = cursor.fetchone()
    cursor.close()
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        sex = request.form['sex']
        date = request.form['date']
        message = request.form['message']

        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE appointment SET first_name = %s, last_name = %s, email_id = %s, mobile_no = %s, sex = %s, appointment_date = %s, reason = %s WHERE appointment_id = %s",
                (first_name, last_name, email, mobile, sex, date, message, appointment_id)
            )
            connection.commit()
            
            flash('Appointment updated successfully!')
            return redirect(url_for('display_appointments'))
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            flash('An error occurred. Please try again later.')
        finally:
            cursor.close()
            connection.close()

    return render_template('edit_appointment.html', appointment=appointment)

@app.route('/delete_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def delete_appointment(appointment_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM appointment WHERE appointment_id = %s", (appointment_id,))
        connection.commit()
        flash('Appointment deleted successfully!')
    except mysql.connector.Error as e:
        print("Error executing SQL query:", e)
        flash('An error occurred. Please try again later.')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('display_appointments'))

if __name__ == '__main__':
    app.run(debug=True)

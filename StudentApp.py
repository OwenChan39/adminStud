from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymysql import connections
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from config import *
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")
app.secret_key = "123456"

# AWS S3 configuration
bucket = custombucket
region = customregion
s3 = boto3.resource("s3")

# Database configuration
db_conn = connections.Connection(
    host=customhost, port=3306, user=customuser, password=custompass, db=customdb
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


# Define a route for student sign-up
@app.route("/student_sign_up", methods=["GET", "POST"])
def student_sign_up():
    if request.method == "POST":
        # Get form data from the POST request
        student_name = request.form["Stud_name"]
        student_id = request.form["Stud_ID"]
        nric_no = request.form["NRIC_Number"]
        gender = request.form["Gender"]
        programme = request.form["Programme_of_Study"]
        cgpa = request.form["CGPA"]
        student_email = request.form["TARUMT_emailAddress"]
        mobile_num = request.form["Mobile_number"]
        intern_batch = request.form["Intern_batch"]
        home_address = request.form["Home_Address"]
        personal_email = request.form["Personal_emailAddress"]
        student_image_file = request.files["studentImage"]

        # Insert student data into the database
        insert_sql = "INSERT INTO Student (Stud_name, Stud_ID, NRIC_Number, Gender, Programme_of_Study, CGPA, TARUMT_emailAddress, Mobile_number, Intern_batch, Home_Address, Personal_emailAddress) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(
                insert_sql,
                (
                    student_name,
                    student_id,
                    nric_no,
                    gender,
                    programme,
                    cgpa,
                    student_email,
                    mobile_num,
                    intern_batch,
                    home_address,
                    personal_email,
                ),
            )
            db_conn.commit()

            # Upload student image to S3
            if student_image_file.filename != "":
                student_image_file_name_in_s3 = (
                    "student-id-" + str(student_id) + "_image_file"
                )
                s3.Bucket(bucket).put_object(
                    Key=student_image_file_name_in_s3, Body=student_image_file
                )

            return render_template("signup_success.html", name=student_name)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    return render_template("student_sign_up.html")


@app.route("/lecturer_sign_up", methods=["GET", "POST"])
def lecturer_sign_up():
    if request.method == "POST":
        # Get form data from the POST request
        full_name = request.form["full_name"]
        staff_id = request.form["staff_id"]
        email = request.form["email"]
        ic = request.form["ic"]
        position = request.form["position"]

        # Insert lecturer data into the database
        insert_sql = "INSERT INTO Lecturer (Lect_name, Lect_ID, Lect_emailAddress, Lect_IC, Lect_Position) VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (full_name, staff_id, email, ic, position))
            db_conn.commit()

            return render_template("signup_success.html", name=full_name)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    return render_template("lecturer_sign_up.html")


@app.route("/company_signup", methods=["GET", "POST"])
def company_signup():
    if request.method == "POST":
        # Get form data from the POST request
        company_name = request.form["company_name"]
        industry = request.form["industry"]
        total_staff = request.form["total_staff"]
        product_service = request.form["product_service"]
        company_website = request.form["company_website"]
        nature_of_job = request.form["job-possition"]
        ot_claim = request.form["ot_claim"]
        company_address = request.form["company_address"]
        state = request.form["state"]
        remarks = request.form["remarks"]
        person_in_charge = request.form["person_in_charge"]
        contact_number = request.form["contact_number"]
        email = request.form["email"]

        certificate_upload = request.files["certificate_upload"]
        logo_upload = request.files["logo_upload"]

        # Insert company data into the database
        insert_sql = "INSERT INTO Company (Comp_name, Comp_website, State, Contact_number, Person_in_charge, EmailAddress, Comp_industry, Comp_address, Total_staff, Product_or_service, Job_offer, OT_claim, Remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(
                insert_sql,
                (
                    company_name,
                    company_website,
                    state,
                    contact_number,
                    person_in_charge,
                    email,
                    industry,
                    company_address,
                    total_staff,
                    product_service,
                    nature_of_job,
                    ot_claim,
                    remarks,
                ),
            )
            db_conn.commit()

            # Upload company documents to S3
            if certificate_upload.filename != "":
                certificate_s3 = "company-" + str(company_name) + "-certificate"
                s3.upload_fileobj(certificate_upload, bucket, certificate_s3)

            if logo_upload.filename != "":
                company_logo_s3 = "company-" + str(company_name) + "-logo"
                s3.upload_fileobj(logo_upload, bucket, company_logo_s3)

            return render_template("signup_success.html", name=company_name)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    return render_template("company_signup.html")


@app.route("/admin_signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        admin_name = request.form["admin_name"]
        admin_username = request.form["admin_username"]
        admin_password = request.form["admin_password"]

        insert_sql = "INSERT INTO Admin (admin_name, admin_username, admin_password) VALUES (%s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (admin_name, admin_username, admin_password))
            db_conn.commit()

            return render_template("signup_success.html", name=admin_name)

        finally:
            cursor.close()
    
    return render_template("adminSignup.html")


@app.route("/login", methods=["POST"], endpoint="login_role")
def login():
    if request.method == "POST":
        # Get the entered role, username, and password from the form
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        # Query the database to check if the username and password match for the selected role
        cursor = db_conn.cursor()

        if role == "student":
            # Check if it's a student login
            cursor.execute(
                "SELECT * FROM Student WHERE Stud_ID = %s AND NRIC_Number = %s",
                (username, password),
            )
            student = cursor.fetchone()

            if student:
                # Student credentials are valid, redirect to the student dashboard
                session["student_id"] = username
                session["role"] = "student"
                return redirect(url_for("student_dashboard"))

        elif role == "lecturer":
            # Check if it's a lecturer login
            cursor.execute(
                "SELECT * FROM Lecturer WHERE Lect_ID = %s AND Lect_IC = %s",
                (username, password),
            )
            lecturer = cursor.fetchone()

            if lecturer:
                # Lecturer credentials are valid, redirect to the lecturer dashboard
                session["lecturer_id"] = username
                session["role"] = "lecturer"
                return redirect(url_for("lecturer_dashboard"))

        elif role == "admin":
            cursor.execute(
                "SELECT * FROM Admin WHERE admin_username = %s AND admin_password = %s",
                (username, password)
            )
            admin = cursor.fetchone()

            if admin:
                session["admin_username"] = username
                session["role"] = "admin"
                return redirect(url_for("adminLanding"))

        cursor.close()

        # Invalid credentials or role, display an error message
        flash("Invalid username, password, or role", "error")

    return render_template("login.html")


@app.route("/lecturer_dashboard", methods=["GET", "POST"])
def lecturer_dashboard():
    if "lecturer_id" in session and "role" in session and session["role"] == "lecturer":
        lecturer_id = session["lecturer_id"]
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Lecturer WHERE Lect_ID = %s", (lecturer_id,))
        lecturer = cursor.fetchone()

        if lecturer:
            lecturer_name = lecturer[0]
        else:
            lecturer_name = "Unknown Lecturer"  # Default if lecturer not found

        cursor.close()

        # Pass the lecturer_name to the template
        return render_template("lecturer_dashboard.html", lecturer_name=lecturer_name)


@app.route("/student_dashboard", methods=["GET", "POST"])
def student_dashboard():
    if "student_id" in session:
        student_id = session["student_id"]
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student:
            # Access the elements of the tuple by their indices
            Stud_name = student[0]
            Stud_ID = student[1]
            NRIC_Number = student[2]
            Gender = student[3]
            Programme_of_Study = student[4]
            CGPA = student[5]
            TARUMT_emailAddress = student[6]
            Mobile_number = student[7]
            Intern_batch = student[8]
            Home_Address = student[9]
            Personal_emailAddress = student[10]

            student_image_file_name_in_s3 = (
                "student-id-" + str(student_id) + "_image_file"
            )
            student_image_url = s3.meta.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": student_image_file_name_in_s3},
                ExpiresIn=3600,
            )

            # Check if a resume file exists in S3
            resume_filename = f"student-{student_id}-resume.pdf"  # Adjust the filename format as needed
            student_resume_url = None

            try:
                s3.Object(bucket, resume_filename).load()
                student_resume_url = s3.meta.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": resume_filename},
                    ExpiresIn=3600,
                )
            except Exception as e:
                pass

            if request.method == "POST" and "resume_file" in request.files:
                student_resume_file = request.files["resume_file"]

                # Ensure a file was selected for upload
                if student_resume_file and student_resume_file.filename != "":
                    resume_filename = f"student-{student_id}-resume.pdf"  # Adjust the filename format as needed

                    try:
                        s3.Bucket(bucket).put_object(
                            Key=resume_filename, Body=student_resume_file
                        )

                        student_resume_url = s3.meta.client.generate_presigned_url(
                            "get_object",
                            Params={"Bucket": bucket, "Key": resume_filename},
                            ExpiresIn=3600,
                        )

                        flash("Resume uploaded successfully", "success")
                    except NoCredentialsError:
                        flash(
                            "S3 credentials are missing or incorrect. Unable to upload resume.",
                            "error",
                        )
                    except Exception as e:
                        flash(f"Error uploading resume: {str(e)}", "error")
                else:
                    flash("No resume file selected for upload", "error")

            if student_resume_url:
                resume_button_text = "View Resume"
            else:
                resume_button_text = "Upload Resume"

            return render_template(
                "student_dashboard.html",
                Stud_name=Stud_name,
                Stud_ID=Stud_ID,
                NRIC_Number=NRIC_Number,
                Gender=Gender,
                Programme_of_Study=Programme_of_Study,
                CGPA=CGPA,
                TARUMT_emailAddress=TARUMT_emailAddress,
                Mobile_number=Mobile_number,
                Intern_batch=Intern_batch,
                Home_Address=Home_Address,
                Personal_emailAddress=Personal_emailAddress,
                student_image_url=student_image_url,
                student_resume_url=student_resume_url,
                resume_button_text=resume_button_text,
            )

    # If the student is not logged in, redirect to the login page
    return redirect(url_for("login"))

@app.route("/adminLanding")
def adminLanding():
    return render_template("adminLanding.html")
    
@app.route("/adminProfile", methods=["GET", "POST"])
def adminProfile():
    if "admin_username" in session and "role" in session and session["role"] == "admin":
        admin_username = session["admin_username"]
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Admin WHERE admin_username = %s", (admin_username,))
        admin = cursor.fetchone()

        if admin:
            admin_name = admin[0]
            admin_username = admin[1]
            admin_password = admin[2]
        else:
            admin_name = "Unknown Admin"  # Default if lecturer not found

        cursor.close()

        # Pass the lecturer_name to the template
        return render_template("adminProfile.html", admin=admin)

@app.route("/adminLecturer")
def admin_lecturer_page():
    return render_template("adminLecturer.html")

@app.route("/adminCompany")
def admin_company_page():
    return render_template("adminCompany.html")

def update_student_profile(student_id, updates):
    cursor = db_conn.cursor()
    update_sql = "UPDATE Student SET "
    update_values = []

    for field, value in updates.items():
        if value is not None:
            update_sql += f"{field} = %s, "
            update_values.append(value)

    # Remove the trailing comma and space
    update_sql = update_sql.rstrip(", ")

    update_sql += " WHERE Stud_ID = %s"
    update_values.append(student_id)

    try:
        cursor.execute(update_sql, tuple(update_values))
        db_conn.commit()
        return True  # Profile updated successfully
    except Exception as e:
        db_conn.rollback()
        return str(e)  # Error updating profile
    finally:
        cursor.close()


@app.route("/student_profile_edit", methods=["GET", "POST"])
def student_profile_edit():
    if "student_id" in session:
        student_id = session["student_id"]
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student:
            if request.method == "POST":
                updated_fields = request.form.getlist("update_fields[]")
                updates = {}

                if "cgpa" in updated_fields:
                    new_cgpa = request.form.get("cgpa")
                    updates["CGPA"] = new_cgpa

                if "mobile" in updated_fields:
                    new_mobile_number = request.form.get("mobileNumber")
                    updates["Mobile_number"] = new_mobile_number

                if "address" in updated_fields:
                    new_home_address = request.form.get("homeAddress")
                    updates["Home_Address"] = new_home_address

                if "email" in updated_fields:
                    new_personal_email = request.form.get("personalEmail")
                    updates["Personal_emailAddress"] = new_personal_email

                if update_student_profile(student_id, updates) is True:
                    flash("Profile updated successfully", "success")
                else:
                    flash("Error updating profile", "error")

                return redirect(url_for("student_dashboard"))

            return render_template("try_student_update.html", student=student)

    return redirect(url_for("login"))


# Define a route for uploading the resume
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "student_id" in session:
        student_id = session["student_id"]
        student_resume_file = request.files["resume_file"]

        # Ensure a file was selected for upload
        if student_resume_file and student_resume_file.filename != "":
            # Generate a unique filename for the resume, e.g., using the student's ID
            resume_filename = f"student-{student_id}-resume.pdf"  # Adjust the filename format as needed

            # Upload the resume file to your S3 bucket
            try:
                s3.Bucket(bucket).put_object(
                    Key=resume_filename, Body=student_resume_file
                )

                # Update the database to store the resume information
                update_sql = "UPDATE Student SET ResumeFileName = %s WHERE Stud_ID = %s"
                cursor = db_conn.cursor()
                cursor.execute(update_sql, (resume_filename, student_id))
                db_conn.commit()

                flash("Resume uploaded successfully", "success")
            except NoCredentialsError:
                flash(
                    "S3 credentials are missing or incorrect. Unable to upload resume.",
                    "error",
                )
            except Exception as e:
                flash(f"Error uploading resume: {str(e)}", "error")
        else:
            flash("No resume file selected for upload", "error")

    return redirect(url_for("student_dashboard"))


@app.route("/student_upload_documents_page")
def student_upload_documents_page():
    return render_template("Student_Upload_Documents.html")


@app.route("/student_upload_documents", methods=["POST"])
def upload_documents():
    if request.method == "POST":
        if "student_id" in session:
            student_id = session["student_id"]

        # Handle combined submission (Letter of Indemnity, Company Acceptance Letter, Parent's Acknowledgment Form)
        for field_name in [
            "letter_of_indemnity",
            "company_acceptance_letter",
            "parents_acknowledgment_form",
        ]:
            if field_name in request.files:
                file = request.files[field_name]
                if file.filename != "":
                    # Construct the S3 object key with the desired naming convention
                    s3_object_key = f"student-{student_id}-{field_name}.pdf"
                    s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        # Redirect to a success page or render a success message
        return redirect(url_for("student_upload_documents_page"))


@app.route("/student_upload_documents_progress", methods=["POST"])
def upload_progress_report():
    if request.method == "POST":
        if "student_id" in session:
            student_id = session["student_id"]

        # Handle progress report submission
        if "progress_report" in request.files:
            file = request.files["progress_report"]
            if file.filename != "":
                # Construct the S3 object key with the desired naming convention
                s3_object_key = f"student-{student_id}-progress-report.pdf"
                s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        # Redirect to a success page or render a success message
        return redirect(url_for("student_upload_documents_page"))


@app.route("/student_upload_documents_final", methods=["POST"])
def upload_final_report():
    if request.method == "POST":
        if "student_id" in session:
            student_id = session["student_id"]

        # Handle final report submission
        if "final_report" in request.files:
            file = request.files["final_report"]
            if file.filename != "":
                # Construct the S3 object key with the desired naming convention
                s3_object_key = f"student-{student_id}-final-report.pdf"
                s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        # Redirect to a success page or render a success message
        return redirect(url_for("student_upload_documents_page"))


@app.route("/studentdatabase", methods=["GET"])
def student_database():
    cursor = db_conn.cursor()

    # Get the search query from the URL parameter
    query = request.args.get("query", "")

    # Use the search query to filter the student data
    if query:
        # Execute a SQL query to retrieve matching students
        cursor.execute(
            "SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student WHERE Stud_name LIKE %s OR Stud_ID LIKE %s",
            ("%" + query + "%", "%" + query + "%"),
        )
    else:
        # If no query provided, retrieve all students
        cursor.execute(
            "SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student"
        )

    students = cursor.fetchall()
    cursor.close()

    return render_template("studentdatabase.html", students=students)

@app.route("/adminStudent", methods=["GET"])
def adminStudent():
    cursor = db_conn.cursor()

    # Get the search query from the URL parameter
    query = request.args.get("query", "")

    # Use the search query to filter the student data
    if query:
        # Execute a SQL query to retrieve matching students
        cursor.execute(
            "SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student WHERE Stud_name LIKE %s OR Stud_ID LIKE %s",
            ("%" + query + "%", "%" + query + "%"),
        )
    else:
        # If no query provided, retrieve all students
        cursor.execute(
            "SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student"
        )

    students = cursor.fetchall()
    number_of_students = len(students)
    enumerated_students = enumerate(students)
    cursor.close()

    return render_template("adminStudent.html", students=enumerated_students, number_of_students=number_of_students)

@app.route('/adminDeleteStudent/<string:student_id>', methods=["GET"])
def admin_delete_student(student_id):
    # Implement code to delete the student with the given student_id from the database or list
    # You can use a database ORM or manipulate the list directly
    cursor = db_conn.cursor()

    # Example using a list:
    delete_query = "DELETE FROM Student WHERE Stud_ID = %s"
    cursor.execute(delete_query, (student_id,))
    db_conn.commit()

    cursor.close()
    return redirect(url_for("adminStudent"))

@app.route("/view_student_progress", methods=["GET"])
def view_student_progress():
    if "lecturer_id" in session and session["role"] == "lecturer":
        # Retrieve student data and file status from your database
        cursor = db_conn.cursor()
        cursor.execute("SELECT Stud_ID, Stud_name FROM Student")
        students = cursor.fetchall()

        # Dictionary to store file status and presigned URLs
        student_files = {}

        for student in students:
            student_id = student[0]

            # Initialize the file status as 'Completed' (green color)
            status = {"text": "Completed", "status": "completed"}
            all_files_found = True  # Flag to track if all files are found

            # Generate presigned URLs for each file (if they exist)
            for file_name in [
                "letter_of_indemnity",
                "company_acceptance_letter",
                "parents_acknowledgment_form",
                "progress-report",
                "final-report",
            ]:
                file_key = f"student-{student_id}-{file_name}.pdf"
                presigned_url = None

                try:
                    s3_client = boto3.client("s3", region_name=region)
                    s3_object = s3_client.head_object(Bucket=bucket, Key=file_key)

                    if "ContentLength" in s3_object:
                        # File exists, generate a presigned URL
                        presigned_url = s3_client.generate_presigned_url(
                            "get_object",
                            Params={"Bucket": bucket, "Key": file_key},
                            ExpiresIn=3600,
                        )
                    else:
                        # File does not exist, set the flag to False
                        all_files_found = False
                except NoCredentialsError:
                    flash("S3 credentials are missing or incorrect.", "error")
                except ClientError as e:
                    if e.response["Error"]["Code"] == "404":
                        # File does not exist, set the flag to False
                        all_files_found = False

                student_files.setdefault(student_id, {})[file_name] = {
                    "url": presigned_url
                }

            # Update the status to 'Completed' only if all files are found
            if not all_files_found:
                status["text"] = "Pending"
                status["status"] = "pending"

            # Store the status in the student_files dictionary
            student_files[student_id]["Status"] = status

        cursor.close()

        return render_template(
            "view_progress_reports.html", students=students, student_files=student_files
        )

    return redirect(url_for("login"))

@app.route('/company_database', methods=["GET"])
def company_database():
    cursor = db_conn.cursor()

    # Retrieve data for new applications
    cursor.execute(
        "SELECT Comp_name, EmailAddress, Contact_number, Comp_address, Person_in_charge, Status FROM Company WHERE Status = 'Pending' ORDER BY Comp_name"
    )
    new_applications = cursor.fetchall()
    num_of_new = len(new_applications)
    enumerated_new = enumerate(new_applications)

    # Retrieve data for approved companies
    cursor.execute(
        "SELECT Comp_name, EmailAddress, Contact_number, Comp_address, Person_in_charge, Status FROM Company WHERE Status = 'Approved' ORDER BY Comp_name"
    )
    approved_companies = cursor.fetchall()
    num_of_approved = len(approved_companies)
    enumerated_approved = enumerate(approved_companies)

    # Retrieve data for rejected companies
    cursor.execute(
        "SELECT Comp_name, EmailAddress, Contact_number, Comp_address, Person_in_charge, Status FROM Company WHERE Status = 'Rejected' ORDER BY Comp_name"
    )
    rejected_companies = cursor.fetchall()
    num_of_rejected = len(rejected_companies)
    enumerated_rejected = enumerate(rejected_companies)

    cursor.close()

    return render_template("adminCompany.html",
                           new_applications=enumerated_new,
                           num_of_new=num_of_new,
                           approved_companies=enumerated_approved,
                           num_of_approved=num_of_approved,
                           rejected_companies=enumerated_rejected,
                           num_of_rejected=num_of_rejected)

@app.route('/adminDeleteCompany/<string:company_name>', methods=["GET"])
def admin_delete_company(company_name):
    # Implement code to delete the student with the given student_id from the database or list
    # You can use a database ORM or manipulate the list directly
    cursor = db_conn.cursor()

    # Example using a list:
    delete_query = "DELETE FROM Company WHERE Comp_name = %s"
    cursor.execute(delete_query, (company_name,))
    db_conn.commit()

    cursor.close()
    return redirect(url_for("company_database"))

@app.route('/update_company_status', methods=['POST'])
def update_company_status():
    cursor = db_conn.cursor()
    # Get the company ID from the submitted form
    company_name = str(request.form.get('company_name'))
    action = str(request.form.get('action'))

    if action == 'approve':
        cursor.execute("UPDATE Company SET Status = 'Approved' WHERE Comp_name = %s", (company_name,))
    elif action == 'reject':
        cursor.execute("UPDATE Company SET Status = 'Rejected' WHERE Comp_name = %s", (company_name,))
    
    db_conn.commit()
    cursor.close()
    return redirect(url_for("company_database"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)

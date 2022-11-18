from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None
current_caregiver = None

def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    
    # checking password security
    number = 0
    letter = 0
    for p in password:
        if p.isalpha():
            letter += 1
        elif p.isnumeric():
            number += 1

    if len(password) < 8:
        print("Password did not reach 8 characters")
        return
    elif password.isupper() or password.islower():
        print("Password needs to have a mixture of lower and uppercase")
        return
    elif number <= 0 or letter <= 0:
        print("Password needs to have a mixture of numbers and letters")
        return
    elif password.count('!') == 0 and password.count('@') == 0 and password.count('#') == 0 and password.count('?') == 0:
        print("Password needs to have special characters")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed, Cannot save")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        return
    print(" *** Account created successfully *** ")

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    
    # checking password security
    number = 0
    letter = 0
    for p in password:
        if p.isalpha():
            letter += 1
        elif p.isnumeric():
            number += 1
    
    if len(password) < 8:
        print("Password did not reach 8 characters")
        return
    elif password.isupper() or password.islower():
        print("Password needs to have a mixture of lower and uppercase")
        return
    elif number <= 0 or letter <= 0:
        print("Password needs to have a mixture of numbers and letters")
        return
    elif password.count('!') == 0 and password.count('@') == 0 and password.count('#') == 0 and password.count('?') == 0:
        print("Password needs to have special characters")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Create caregiver failed, Cannot save")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        return
    print(" *** Account created successfully *** ")

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in! Please logout first.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login caregiver failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when logging in. Please try again!")
        print("Error:", e)
        return
    
    # check if the login was successful
    if patient is None:
        print("Error occurred when logging in. Please try again!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient

def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login caregiver failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when logging in. Please try again!")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Error occurred when logging in. Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver

def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_availability = "SELECT * FROM Availabilities WHERE Time = %s"
    select_vaccine = "SELECT * FROM Vaccines"

    if len(tokens) != 2:
        print("Please try again!")
        return
    
    # the input must be written in the format of mm-dd-yyyy
    date = tokens[1].split("-")
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])

    # get the available caregivers on that date
    try:
        d = datetime.date(year, month, day)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availability, d)

        if cursor.rowcount == 0:
            print("No available caregivers. Please try again.")
        else:
            print("Available Caregivers: ")
            for row in cursor:
                print(row['Username'])

    except ValueError as e:
        print("Invalid date! Please try again.")
        return
    except pymssql.Error as e:
        print("Cannot retrieve caregiver schedule")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occured. Please try again!")
        print("Error:", e)
        return
   
    # get the availability of the vaccines         
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_vaccine)

        print("Vaccine Availability: ")
        for row in cursor:
            print(row['Name'], ":", row['Doses'])
 
    # throw exception
    except pymssql.Error as e:
        print("Cannot retrieve vaccines")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occured. Please try again!")
        print("Error:", e)
        return

def reserve(tokens):
    # reserve <date> <vaccine>
    global current_patient

    cm = ConnectionManager()
    conn = cm.create_connection()

    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    # check 2: check if the current logged-in user is a patient
    if current_patient is None:
        print("Please login as a patient first!")
        return
    
    # check the vaccine availability
    vaccine = None
    try:
        available_doses = 0
        try:
            # create vaccine
            vaccine = Vaccine(tokens[2], available_doses).get()
        except:
            print("Error occured! Cannot get vaccine.")
            return
        if vaccine is None or vaccine.get_available_doses() <= 0:
            print("There are no available vaccines, please try again")
            return
    # throw exception
    except pymssql.Error as e:
        print("Cannot retrieve vaccine availability")
        print("Db-Error:", e)
        quit()

    select_availability = "SELECT * FROM Availabilities WHERE Time = %s"
    # the input must be written in the format of mm-dd-yyyy
    date = tokens[1].split("-")
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])

    # get a random caregiver
    chosen_caregiver = None
    try:
        d = datetime.date(year, month, day)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availability, d)

        if cursor.rowcount == 0:
            print("No available caregivers. Please try again.")
            return
        else:
            all_caregivers= []
            for row in cursor:
                all_caregivers.append(row['Username'])
            chosen_caregiver = all_caregivers[random.randint(0,len(all_caregivers)-1)]
    except ValueError as e:
        print("Invalid date! Please try again.")
        return
    except pymssql.Error as e:
        print("Cannot retrieve caregiver schedule")
        print("Db-Error:", e)
        quit()
    
    # uploading a reservation, delete caregiver availability, and reduce vaccine dose
    try:
        d = datetime.date(year, month, day)

        # uploading reservation
        try:
            current_patient.make_appointment(d, chosen_caregiver, tokens[2])
        except:
            print("Error uploading reservation. Please try again")
            return

        # reducing vaccine dose
        try:
            vaccine.decrease_available_doses(1)
        except:
            print("Error reducing vaccine dose. Please try again")
            return

        # delete caregiver availability
        del_availability = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
        try:
            cursor.execute(del_availability, (d, chosen_caregiver))
            conn.commit()
        except pymssql.Error:
            print("Error occurred when deleting availability")
            cm.close_connection()
        cm.close_connection()
        
        print("Assigned Caregiver: ", chosen_caregiver)
        # print("Appointment ID: ")

    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error making reservation")  

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")

def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Failed to get Vaccine information")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to get Vaccine information")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Failed to add new Vaccine to database")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to add new Vaccine to database")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Failed to increase available doses for Vaccine")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to increase available doses for Vaccine")
            print("Error:", e)
            return
    print("Doses updated!")

def show_appointments(tokens):
    global current_caregiver
    global current_patient

    cm = ConnectionManager()
    conn = cm.create_connection()

    if current_patient is None and current_caregiver is None:
        print("Please log in before proceeding.")
        return

    if current_patient is None: # caregiver
        select_appointment = "SELECT * FROM Appointments WHERE caregiver_username = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointment, current_caregiver.get_username())

            if cursor.rowcount == 0:
                print("You currently have no appointments.")
            else:
                print('Appointments: ')
                for row in cursor:
                    print("ID: ", row['AppointmentID'], "|| Assigned Patient: ", row['patient_username'], 
                    "|| Vaccine: ", row['vaccine_name'], "|| Date: ", row['Time'])
        except pymssql.Error:
            print("Error occured, please try again.")
    else: # patient
        select_appointment = "SELECT * FROM Appointments WHERE patient_username = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointment, current_patient.get_username())

            if cursor.rowcount == 0:
                print("You currently have no appointments.")
            else:
                print('Appointments: ')
                for row in cursor:
                    print("ID: ", row['AppointmentID'], "|| Assigned Caregiver: ", row['caregiver_username'], 
                    "|| Vaccine: ", row['vaccine_name'], "|| Date: ", row['Time'])
        except pymssql.Error:
            print("Error occured, please try again.")

def logout(tokens):
    global current_patient
    global current_caregiver
    
    if current_patient is None and current_caregiver is None:
        print("Please log in before proceeding")
    elif current_patient is None:
        print("Success! Logged out of " + current_caregiver.get_username())
        current_caregiver = None
    else:
        print("Success! Logged out of " + current_patient.get_username())
        current_patient = None

def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  #// TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  #// TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") #// TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") #// TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  #// TODO: implement show_appointments (Part 2)
        print("> logout") #// TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        # response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")

if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''
    
    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()

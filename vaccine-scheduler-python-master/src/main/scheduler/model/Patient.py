import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import random

class Patient:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT Salt, Hash FROM Patients WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            print("Error occurred when fetching current caregiver")
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_patient = "INSERT INTO Patients VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_patient, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    # get appointment ID
    def get_id(self):
            cm = ConnectionManager()
            conn = cm.create_connection()
            cursor = conn.cursor()

            select_appointment = "SELECT * FROM Appointments"
            try:
                cursor.execute(select_appointment)
                conn.commit()
                all_id = []
                for row in cursor:
                    result.append(row['AppointmentID'])
            except pymssql.Error:
                print("Error occurred when getting appointments")
                cm.close_connection()
            cm.close_connection()
            return all_id

    # reserving an appointment with parameter d: date, c: desired caregiver, v: desired vaccine
    def make_appointment(self, d, c, v):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        takenID = self.get_id()

        add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
        try:
            id = random.choice([t for t in range(1000000,9999999) if t not in takenID]) # need to make it unique
            cursor.execute(add_appointment, (id, v, c, self.username, d))
            conn.commit()
            print("Appointment ID: ", id)
        except pymssql.Error:
            print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()


   


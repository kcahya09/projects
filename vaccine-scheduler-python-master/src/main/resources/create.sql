CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    AppointmentID int,
    vaccine_name varchar(255),
    caregiver_username varchar(255),
    patient_username varchar(255),
    Time date,
    PRIMARY KEY (AppointmentID),
    FOREIGN KEY (vaccine_name) REFERENCES Vaccines(name),
    FOREIGN KEY (caregiver_username) REFERENCES Caregivers(username),
    FOREIGN KEY (patient_username) REFERENCES Patients(username)
);
import sqlite3
from flask_restful import Resource
import json
import pandas as pd
import controllers.db_constants as db_constants


class User():

    def __init__(self, _id, firstname, lastname, license_number, age, city):
        self.id = _id
        self.firstname = firstname
        self.lastname = lastname
        self.license_number = license_number
        self.age = age
        self.city = city

    @classmethod
    def find_by_license_number(cls, license_number):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        print ("----------licenese number to fetch------------")
        print (license_number)
        query = "SELECT * FROM {table} WHERE license_number= ?".format(table=db_constants.TABLE_NAME)
        result = cursor.execute(query, license_number)
        print ("--------result----------")
        print (result)
        row = result.fetchone()
        print ("--------row----------")
        print (row)
        if row:
            user = {}
            user['firstname'] = row[1]
            user['lastname'] = row[2]
            user['license_number'] = row[3]
            user['age'] = row[4]
            user['city'] = row[5]
        else:
            user = None

        connection.close()
        return user


class UserRegister(Resource):
    conn = None

    def check_database():
        ''' Check if the database exists or not '''
        try:
            print(f'Checking if {db_constants.DB_NAME} exists or not...')
            UserRegister.conn = sqlite3.connect(db_constants.DB_NAME, uri=True)
            print(f'Database exists. Succesfully connected to {db_constants.DB_NAME}')

        except sqlite3.OperationalError as err:
            print('Database does not exist')
            print(err)

    def create_database():
        connection = sqlite3.connect(db_constants.DB_NAME)
        cursor = connection.cursor()
        create_table = "CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, firstname text, lastname text, license_number text, age int, city text)".format(table=db_constants.TABLE_NAME)
        cursor.execute(create_table)
        connection.commit()

    def upload_batch(filename):
        batch = pd.read_csv(filename)
        license_data = json.loads(batch.to_json(orient="records"))
        return license_data

    def insert_data(data):
        for row in data:

            if User.find_by_license_number(row['license_number']):
                return {"message": "User with that license_number already exists."}, 400

            connection = sqlite3.connect(db_constants.DB_NAME)
            cursor = connection.cursor()


            query = "INSERT INTO {table} VALUES (NULL, ?, ?, ?)".format(table=db_constants.TABLE_NAME)
            cursor.execute(query, (row['firstname'], row['lastname'], row['license_number']))

            connection.commit()
            connection.close()

            return {"message": "User created successfully."}, 201



    def post(filename):
        
        data = UserRegister.upload_batch(filename)
        if UserRegister.check_database():
            UserRegister.insert_data(data)
        else:
            UserRegister.create_database()
            UserRegister.insert_data(data)


 

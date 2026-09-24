import unittest
import datetime
import os
import sqlite3

# Import modules to test
import validators
import database
import operations
import config
from seed import setup_base_data

class TestValidators(unittest.TestCase):
    def test_validate_dni(self):
        self.assertTrue(validators.validate_dni("1234567"))
        self.assertTrue(validators.validate_dni("12345678"))
        self.assertFalse(validators.validate_dni("123456"))
        self.assertFalse(validators.validate_dni("123456789"))
        self.assertFalse(validators.validate_dni("abcdefgh"))

    def test_validate_date(self):
        self.assertTrue(validators.validate_date("2020-01-01"))
        self.assertFalse(validators.validate_date("2050-01-01")) # Future
        self.assertFalse(validators.validate_date("invalid"))

    def test_validate_minimum_age(self):
        # Assuming MINIMUM_AGE is 16
        today = datetime.date.today()
        # exactly 16 years ago
        valid_date = datetime.date(today.year - config.MINIMUM_AGE, today.month, today.day)
        self.assertTrue(validators.validate_minimum_age(valid_date.strftime("%Y-%m-%d")))
        
        # 16 years minus 1 day ago (15 years old)
        invalid_date = valid_date + datetime.timedelta(days=1)
        self.assertFalse(validators.validate_minimum_age(invalid_date.strftime("%Y-%m-%d")))

    def test_validate_email(self):
        self.assertTrue(validators.validate_email("test@test.com"))
        self.assertFalse(validators.validate_email("testtest.com"))

    def test_validate_not_empty(self):
        self.assertTrue(validators.validate_not_empty(" a "))
        self.assertFalse(validators.validate_not_empty("   "))
        self.assertFalse(validators.validate_not_empty(""))

class TestOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We will use a test database file for testing
        cls.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_system.db")
        
    @classmethod
    def tearDownClass(cls):
        database.DB_PATH = cls.original_db_path
        if os.path.exists(database.DB_PATH):
            try:
                os.remove(database.DB_PATH)
            except:
                pass

    def setUp(self):
        # Drop all tables if exist from previous run
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        # Create tables and initial data before each test
        database.create_tables()
        conn = database.connect_db()
        cursor = conn.cursor()
        setup_base_data(cursor)
        conn.commit()
        database.disconnect_db(conn)

    def tearDown(self):
        pass

    def test_insert_person(self):
        operations.insert_person("11111111", "Juan", "Perez", "2000-01-01", "Calle 1", "La Plata", "1234", "a@a.com")
        person = operations.get_person_by_dni("11111111")
        self.assertIsNotNone(person)
        self.assertEqual(person[0][2], "Juan")

    def test_register_applicant_underage(self):
        # Underage person (born 10 years ago)
        today = datetime.date.today()
        birth_date = f"{today.year - 10}-01-01"
        operations.insert_person("22222222", "Menor", "Perez", birth_date, "Calle 1", "La Plata", "1234", "a@a.com")
        person = operations.get_person_by_dni("22222222")
        person_id = person[0][0]
        
        success, msg = operations.register_applicant(person_id, 1) # Comision 1
        self.assertFalse(success)
        self.assertIn("edad mínima", msg.lower())

    def test_register_applicant_success_and_duplicate(self):
        operations.insert_person("33333333", "Mayor", "Perez", "1990-01-01", "Calle 1", "La Plata", "1234", "a@a.com")
        person = operations.get_person_by_dni("33333333")
        person_id = person[0][0]
        
        # First registration should succeed
        success, msg = operations.register_applicant(person_id, 1)
        self.assertTrue(success)
        
        # Second registration should fail
        success, msg = operations.register_applicant(person_id, 2)
        self.assertFalse(success)
        self.assertIn("ya posee un curso asignado", msg.lower())

if __name__ == '__main__':
    unittest.main()

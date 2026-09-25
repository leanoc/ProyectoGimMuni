import unittest
import datetime
import os
import sqlite3
import tempfile

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
        test_db_fd, cls.test_db_path = tempfile.mkstemp(suffix=".db")
        os.close(test_db_fd)
        database.DB_PATH = cls.test_db_path
        
    @classmethod
    def tearDownClass(cls):
        database.DB_PATH = cls.original_db_path
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

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

    def test_register_new_applicant(self):
        success, msg = operations.register_new_applicant(
            "11111111", "Juan", "Perez", "2000-01-01",
            "Calle 1", "La Plata", "1234", "a@a.com", 1
        )
        self.assertTrue(success, msg)
        person = operations.get_person_by_dni("11111111")
        self.assertIsNotNone(person)
        self.assertEqual(person[0][2], "Juan")
        self.assertEqual(
            database.execute_query(
                "SELECT COUNT(*) FROM Inscripcion WHERE id_persona = ?",
                (person[0][0],),
                fetch=True
            )[0][0],
            1
        )

    def test_register_applicant_underage(self):
        # Underage person (born 10 years ago)
        today = datetime.date.today()
        birth_date = f"{today.year - 10}-01-01"
        success, msg = operations.register_new_applicant(
            "22222222", "Menor", "Perez", birth_date,
            "Calle 1", "La Plata", "1234", "a@a.com", 1
        )
        self.assertFalse(success)
        self.assertIn("edad mínima", msg.lower())
        self.assertFalse(operations.get_person_by_dni("22222222"))

    def test_register_applicant_success_and_duplicate(self):
        success, msg = operations.register_new_applicant(
            "33333333", "Mayor", "Perez", "1990-01-01",
            "Calle 1", "La Plata", "1234", "a@a.com", 1
        )
        self.assertTrue(success, msg)
        person = operations.get_person_by_dni("33333333")
        person_id = person[0][0]
        
        # Second registration should fail
        success, msg = operations.register_applicant(person_id, 2)
        self.assertFalse(success)
        self.assertIn("ya posee un curso asignado", msg.lower())

    def test_failed_enrollment_does_not_create_person(self):
        success, msg = operations.register_new_applicant(
            "44444444", "Ana", "Lopez", "1990-01-01",
            "Calle 1", "La Plata", "1234", "a@a.com", 999
        )
        self.assertFalse(success)
        self.assertIn("comisión indicada no existe", msg.lower())
        self.assertFalse(operations.get_person_by_dni("44444444"))

    def test_deregister_promotes_earliest_waitlisted_in_same_commission(self):
        applicants = [
            ("55555551", "Admitida", 1, "2026-01-01 08:00:00"),
            ("55555552", "Primera", 1, "2026-01-01 09:00:00"),
            ("55555553", "Segunda", 1, "2026-01-01 10:00:00"),
            ("55555554", "OtraComision", 2, "2026-01-01 07:00:00"),
        ]
        for dni, name, commission_id, enrolled_at in applicants:
            success, msg = operations.register_new_applicant(
                dni, name, "Test", "1990-01-01",
                "Calle 1", "La Plata", "1234", "a@a.com", commission_id
            )
            self.assertTrue(success, msg)
            database.execute_query(
                """
                UPDATE Inscripcion
                SET fecha_hora = ?, estado = ?
                WHERE id_persona = (SELECT id_persona FROM Persona WHERE dni = ?)
                """,
                (enrolled_at, 1 if dni == "55555551" else 0, dni)
            )

        success, msg = operations.deregister_admitted_applicant("55555551")

        self.assertTrue(success, msg)
        self.assertIn("Primera Test", msg)
        self.assertFalse(operations.get_person_by_dni("55555551"))
        self.assertEqual(
            database.execute_query(
                """
                SELECT i.estado FROM Inscripcion i
                JOIN Persona p ON p.id_persona = i.id_persona
                WHERE p.dni = ?
                """,
                ("55555552",),
                fetch=True
            )[0][0],
            1
        )
        self.assertEqual(
            database.execute_query(
                """
                SELECT i.estado FROM Inscripcion i
                JOIN Persona p ON p.id_persona = i.id_persona
                WHERE p.dni = ?
                """,
                ("55555553",),
                fetch=True
            )[0][0],
            0
        )
        self.assertEqual(
            database.execute_query(
                """
                SELECT i.estado FROM Inscripcion i
                JOIN Persona p ON p.id_persona = i.id_persona
                WHERE p.dni = ?
                """,
                ("55555554",),
                fetch=True
            )[0][0],
            0
        )
        commission = next(c for c in operations.get_all_commissions() if c[0] == 1)
        self.assertEqual(commission[6], 2)
        self.assertEqual(commission[7], 1)
        self.assertEqual(commission[8], 1)

    def test_deregister_rejects_person_not_admitted(self):
        success, msg = operations.register_new_applicant(
            "66666666", "Pendiente", "Test", "1990-01-01",
            "Calle 1", "La Plata", "1234", "a@a.com", 1
        )
        self.assertTrue(success, msg)

        success, msg = operations.deregister_admitted_applicant("66666666")

        self.assertFalse(success)
        self.assertIn("no se encontró una inscripción admitida", msg.lower())
        self.assertTrue(operations.get_person_by_dni("66666666"))

    def test_deregister_without_waitlist_keeps_commission_vacant(self):
        success, msg = operations.register_new_applicant(
            "77777777", "Admitido", "Test", "1990-01-01",
            "Calle 1", "La Plata", "1234", "a@a.com", 1
        )
        self.assertTrue(success, msg)
        person_id = operations.get_person_by_dni("77777777")[0][0]
        database.execute_query(
            "UPDATE Inscripcion SET estado = 1 WHERE id_persona = ?",
            (person_id,)
        )

        success, msg = operations.deregister_admitted_applicant("77777777")

        self.assertTrue(success, msg)
        self.assertIn("no había inscriptos pendientes", msg.lower())
        self.assertEqual(
            database.execute_query(
                "SELECT COUNT(*) FROM Inscripcion WHERE id_comision = 1 AND estado = 1",
                fetch=True
            )[0][0],
            0
        )

if __name__ == '__main__':
    unittest.main()

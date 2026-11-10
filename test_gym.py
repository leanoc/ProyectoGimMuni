import unittest
import datetime
import os
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch

# Import modules to test
import validators
import database
import operations
import reports
import config
import notifications
from seed import setup_base_data


class TestNotifications(unittest.TestCase):
    def test_build_mailto_url(self):
        url = notifications.build_mailto_url(
            "persona@example.com", "Asunto Prueba", "Hola Mundo\nLínea 2"
        )
        self.assertTrue(url.startswith("mailto:persona@example.com?"))
        self.assertIn("subject=Asunto%20Prueba", url)
        self.assertIn("body=Hola%20Mundo%0AL%C3%ADnea%202", url)

    def test_send_email_opens_mailto(self):
        with patch("notifications.webbrowser.open", return_value=True) as mock_open:
            sent, detail = notifications.send_email(
                "person@example.com", "Asunto", "Mensaje"
            )

        self.assertTrue(sent, detail)
        mock_open.assert_called_once()
        self.assertTrue(mock_open.call_args[0][0].startswith("mailto:person@example.com?"))

    def test_send_email_invalid_recipient(self):
        sent, detail = notifications.send_email("invalido", "Asunto", "Mensaje")
        self.assertFalse(sent)
        self.assertIn("destinatario no es válida", detail)


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

    def test_registration_sends_receipt_email(self):
        with patch(
            "operations.notifications.send_email",
            return_value=(True, "Correo enviado."),
        ) as send_email:
            success, message = operations.register_new_applicant(
                "11111112", "Ana", "Prueba", "2000-01-01",
                "Calle 1", "Berisso", "1234", "ana@example.com", 1
            )

        self.assertTrue(success, message)
        self.assertIn("Correo de inscripción enviado", message)
        self.assertEqual(send_email.call_args.args[0], "ana@example.com")
        self.assertIn("inscripción", send_email.call_args.args[1].lower())

    def test_export_data_returns_only_selected_columns(self):
        headers, rows = operations.get_export_data("Curso", ("nombre", "criterio"))

        self.assertEqual(headers, ("nombre", "criterio"))
        self.assertTrue(rows)
        self.assertEqual(len(rows[0]), 2)

        with self.assertRaises(ValueError):
            operations.get_export_data("Persona", ("password",))

    def test_movements_are_recorded_and_exportable(self):
        created, message = operations.create_course("Curso historial", "Sorteo", 16, 1)
        self.assertTrue(created, message)
        course_id = database.execute_query(
            "SELECT id_curso FROM Curso WHERE nombre = ?",
            ("Curso historial",),
            fetch=True,
        )[0][0]
        updated, message = operations.update_course(course_id, "Curso historial editado", "Sorteo", 16, 1)
        self.assertTrue(updated, message)
        deleted, message = operations.delete_course(course_id)
        self.assertTrue(deleted, message)

        success, message = operations.register_new_applicant(
            "76543210", "Historial", "Prueba", "1990-01-01",
            "Calle 1", "Berisso", "1234", "history@example.com", 1,
        )
        self.assertTrue(success, message)
        history = operations.get_movement_history()
        self.assertTrue(any(row[1] == "Inscripción" and row[2] == "Alta" for row in history))

        with tempfile.TemporaryDirectory() as directory:
            csv_path = os.path.join(directory, "historial.csv")
            pdf_path = os.path.join(directory, "historial.pdf")
            reports.export_history_csv(csv_path, history)
            reports.export_history_pdf(pdf_path, history * 6)

            with open(csv_path, encoding="utf-8-sig", newline="") as csv_file:
                self.assertIn("Fecha y hora", csv_file.readline())
            with open(pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            self.assertTrue(pdf_data.startswith(b"%PDF-1.4"))
            self.assertTrue(pdf_data.endswith(b"%%EOF\n"))
            xref_offset = int(pdf_data.rsplit(b"startxref\n", 1)[1].splitlines()[0])
            self.assertEqual(pdf_data[xref_offset:xref_offset + 5], b"xref\n")
            self.assertIn(b"/Count 2", pdf_data)

    def test_backup_copies_a_readable_database(self):
        with tempfile.TemporaryDirectory() as directory:
            backup_path = os.path.join(directory, "respaldo.db")
            self.assertEqual(operations.backup_database(backup_path), backup_path)
            backup = sqlite3.connect(backup_path)
            try:
                course_count = backup.execute("SELECT COUNT(*) FROM Curso").fetchone()[0]
            finally:
                backup.close()
            self.assertGreater(course_count, 0)

        with self.assertRaises(ValueError):
            operations.backup_database(database.DB_PATH)

    def test_course_statistics_count_commissions_and_registrations(self):
        success, message = operations.register_new_applicant(
            "76543211", "Estadistica", "Prueba", "1990-01-01",
            "Calle 1", "Berisso", "1234", "stats@example.com", 1, "Mujer",
        )
        self.assertTrue(success, message)
        statistics = {row[0]: row[1:] for row in operations.get_course_statistics()}
        self.assertIn("Natación", statistics)
        enrolled, admitted, waiting, commissions, seats, course_limit, commission_limit = statistics["Natación"]
        self.assertGreaterEqual(enrolled, 1)
        self.assertEqual(admitted + waiting, enrolled)
        self.assertGreater(commissions, 0)
        self.assertGreater(seats, 0)
        self.assertGreater(course_limit, 0)
        self.assertGreater(commission_limit, 0)
        self.assertEqual(
            dict(operations.get_gender_statistics()),
            {"Hombre": 0, "Mujer": 1, "Sin especificar": 0},
        )

    def test_existing_database_migration_adds_unspecified_gender(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_path = os.path.join(directory, "legacy.db")
            original_path = database.DB_PATH
            database.DB_PATH = legacy_path
            try:
                conn = sqlite3.connect(legacy_path)
                conn.execute(
                    """
                    CREATE TABLE Persona (
                        id_persona INTEGER PRIMARY KEY,
                        dni TEXT UNIQUE NOT NULL,
                        nombre TEXT NOT NULL,
                        apellido TEXT NOT NULL,
                        fecha_nac DATE NOT NULL,
                        direccion TEXT,
                        localidad TEXT,
                        telefono TEXT,
                        email TEXT
                    )
                    """
                )
                conn.execute(
                    "INSERT INTO Persona (dni, nombre, apellido, fecha_nac) VALUES ('12345678', 'Ana', 'Ejemplo', '1990-01-01')"
                )
                conn.commit()
                conn.close()

                database.create_tables()
                migrated_gender = database.execute_query(
                    "SELECT sexo FROM Persona WHERE dni = '12345678'",
                    fetch=True,
                )[0][0]
                self.assertEqual(migrated_gender, "Sin especificar")
            finally:
                database.DB_PATH = original_path

    def test_assignments_send_confirmation_to_new_admitted_people(self):
        with patch(
            "operations.notifications.send_email",
            return_value=(True, "Correo enviado."),
        ) as send_email:
            lottery_ok, lottery_message = operations.register_new_applicant(
                "11111113", "Loteria", "Prueba", "1990-01-01",
                "Calle 1", "Berisso", "1234", "lottery@example.com", 1
            )
            fifo_ok, fifo_message = operations.register_new_applicant(
                "11111114", "Llegada", "Prueba", "1950-01-01",
                "Calle 1", "Berisso", "1234", "fifo@example.com", 3
            )
            self.assertTrue(lottery_ok, lottery_message)
            self.assertTrue(fifo_ok, fifo_message)
            send_email.reset_mock()

            lottery_count, lottery_details = operations.run_lottery_assignment()
            fifo_count, fifo_details = operations.run_fifo_assignment()

        self.assertEqual(lottery_count, 1)
        self.assertEqual(fifo_count, 1)
        self.assertIn("Correo de confirmación enviado", "\n".join(lottery_details))
        self.assertIn("Correo de confirmación enviado", "\n".join(fifo_details))
        self.assertEqual(send_email.call_count, 2)
        self.assertEqual(
            {call.args[0] for call in send_email.call_args_list},
            {"lottery@example.com", "fifo@example.com"},
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

        with patch(
            "operations.notifications.send_email",
            return_value=(True, "Correo enviado."),
        ) as send_email:
            success, msg = operations.deregister_admitted_applicant("55555551")

        self.assertTrue(success, msg)
        self.assertIn("Primera Test", msg)
        self.assertIn("Correo de confirmación enviado", msg)
        send_email.assert_called_once()
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

    def test_quota_verification_prevents_insert_when_full(self):
        # Commission 1 has cupo_total = 30 in base data
        # Fill it up to 30
        for i in range(30):
            dni = f"800000{i:02d}"
            ok, _ = operations.register_new_applicant(
                dni, f"Nom{i}", f"Ape{i}", "1995-05-10",
                "Calle X", "La Plata", "221444", f"{dni}@test.com", 1
            )
            self.assertTrue(ok)

        # Now commission 1 is at maximum (30/30)
        has_quota, quota_msg = operations.check_commission_availability(1)
        self.assertFalse(has_quota)
        self.assertIn("cupo completo", quota_msg.lower())

        # Attempt to register 31st applicant must be rejected
        ok, msg = operations.register_new_applicant(
            "89999999", "Excedente", "Test", "1995-05-10",
            "Calle X", "La Plata", "221444", "exc@test.com", 1
        )
        self.assertFalse(ok)
        self.assertIn("cupo completo", msg.lower())
        # Verify the applicant was NOT created in Persona table either
        self.assertFalse(operations.get_person_by_dni("89999999"))

    def test_course_crud(self):
        # Create
        ok, msg = operations.create_course("Yoga Acuático", "Orden de llegada")
        self.assertTrue(ok, msg)

        courses = operations.get_all_courses()
        course_yoga = next((c for c in courses if c[1] == "Yoga Acuático"), None)
        self.assertIsNotNone(course_yoga)
        course_id = course_yoga[0]

        # Update
        ok, msg = operations.update_course(course_id, "Yoga Acuático Pro", "Sorteo")
        self.assertTrue(ok, msg)
        updated = operations.get_course_by_id(course_id)[0]
        self.assertEqual(updated[1], "Yoga Acuático Pro")
        self.assertEqual(updated[2], "Sorteo")

        # Delete
        ok, msg = operations.delete_course(course_id)
        self.assertTrue(ok, msg)
        self.assertFalse(operations.get_course_by_id(course_id))

    def test_commission_crud(self):
        # Create commission for course 1
        ok, msg = operations.create_commission("C3-TEST", 20, 15, 1)
        self.assertTrue(ok, msg)

        comms = operations.get_all_commissions()
        c3 = next((c for c in comms if c[1] == "C3-TEST"), None)
        self.assertIsNotNone(c3)
        c3_id = c3[0]

        # Update commission (expand quota)
        ok, msg = operations.update_commission(c3_id, "C3-TEST-MOD", 25, 20, 1)
        self.assertTrue(ok, msg)
        comm_info = operations.get_commission_by_id(c3_id)[0]
        self.assertEqual(comm_info[1], "C3-TEST-MOD")
        self.assertEqual(comm_info[2], 25)
        self.assertEqual(comm_info[3], 20)

        # Delete commission
        ok, msg = operations.delete_commission(c3_id)
        self.assertTrue(ok, msg)
        self.assertFalse(operations.get_commission_by_id(c3_id))

    def test_update_person_and_unique_dni(self):
        ok, _ = operations.register_new_applicant(
            "90000001", "Ana", "Gomez", "1998-04-12",
            "Calle 10", "Tolosa", "221111", "ana@test.com", 1
        )
        self.assertTrue(ok)
        ok, _ = operations.register_new_applicant(
            "90000002", "Beto", "Lopez", "1997-03-10",
            "Calle 12", "Tolosa", "221222", "beto@test.com", 1
        )
        self.assertTrue(ok)

        person1 = operations.get_person_by_dni("90000001")[0]
        person1_id = person1[0]

        # Attempt to change person 1's DNI to person 2's DNI (collision)
        ok, msg = operations.update_person(
            person1_id, "90000002", "Ana Mod", "Gomez Mod", "1998-04-12",
            "Calle Nueva", "Tolosa", "221999", "ana_mod@test.com"
        )
        self.assertFalse(ok)
        self.assertIn("ya se encuentra registrado", msg.lower())

        # Update person 1 with a valid unique new DNI and new address
        ok, msg = operations.update_person(
            person1_id, "90000099", "Ana Mod", "Gomez Mod", "1998-04-12",
            "Calle Nueva 456", "La Plata", "221999", "ana_mod@test.com", "Mujer"
        )
        self.assertTrue(ok, msg)
        updated_p1 = operations.get_person_by_id(person1_id)[0]
        self.assertEqual(updated_p1[1], "90000099")
        self.assertEqual(updated_p1[2], "Ana Mod")
        self.assertEqual(updated_p1[5], "Calle Nueva 456")
        self.assertEqual(updated_p1[9], "Mujer")

    def test_waiting_list_and_change_commission(self):
        # Register two applicants in commission 1
        ok1, _ = operations.register_new_applicant(
            "91000001", "Postulante1", "Uno", "1995-01-01",
            "Calle A", "La Plata", "111", "p1@test.com", 1
        )
        ok2, _ = operations.register_new_applicant(
            "91000002", "Postulante2", "Dos", "1995-01-01",
            "Calle B", "La Plata", "222", "p2@test.com", 1
        )
        self.assertTrue(ok1 and ok2)

        # Check waiting list for commission 1
        wl = operations.get_waiting_list_by_commission(1)
        dnis_in_wl = [item[0] for item in wl]
        self.assertIn("91000001", dnis_in_wl)
        self.assertIn("91000002", dnis_in_wl)

        # Change commission for applicant 1 to commission 2
        ok_change, msg_change = operations.change_commission_registration("91000001", 2)
        self.assertTrue(ok_change, msg_change)

        wl_c2 = operations.get_waiting_list_by_commission(2)
        dnis_c2 = [item[0] for item in wl_c2]
        self.assertIn("91000001", dnis_c2)

        # Cancel registration for applicant 2
        ok_cancel, msg_cancel = operations.cancel_registration_by_dni("91000002")
        self.assertTrue(ok_cancel, msg_cancel)
        wl_after = operations.get_waiting_list_by_commission(1)
        dnis_after = [item[0] for item in wl_after]
        self.assertNotIn("91000002", dnis_after)

if __name__ == '__main__':
    unittest.main()

import database
import menuprincipal

def main():
    """Punto de entrada: genera estructura en base de datos e inicia CLI."""
    database.create_tables()
    menuprincipal.display_main_menu()

if __name__ == "__main__":
    main()
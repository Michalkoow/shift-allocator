# Shift Allocator

Aplikacja Django do sprawiedliwego przydzielania pracowników do działów na zmianie. Projekt stworzony jako projekt końcowy na bootcampie Python Developer w CodersLab.

##  Funkcjonalności

-  Lista pracowników z filtrowaniem, sortowaniem i paginacją
-  Dodawanie nowych pracowników
-  Edytowanie danych pracownika
-  Usuwanie pracowników
-  Automatyczny przydział pracowników do działów na podstawie dostępności i pojemności działu
-  Wyszukiwanie po imieniu, nazwisku i dziale
-  Widoki dostępne tylko dla zalogowanych (planowane)
-  Rejestracja i logowanie użytkownika (planowane)

##  Technologie

- Python 3.12
- Django 5.1
- PostgreSQL
- HTML5 + Bootstrap 5
- Pytest

## 🔧 Jak uruchomić projekt lokalnie?
1. Sklonuj repozytorium:


git clone https://github.com/Michalkoow/shift-allocator.git
cd shift-allocator

2. Utwórz i aktywuj środowisko wirtualne:
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows

3. Zainstaluj wymagane pakiety:

pip install -r requirements.txt

4.Skonfiguruj połączenie z bazą PostgreSQL w pliku settings.py.

5. Wykonaj migracje:

python manage.py migrate

6.Uruchom serwer:

python manage.py runserver

7.(Opcjonalnie) Utwórz użytkownika admina:

python manage.py createsuperuser

Zostaniesz poproszony o:

    nazwę użytkownika

    adres e-mail

    hasło

Po utworzeniu konta wejdź w przeglądarce na:

http://127.0.0.1:8000/admin/

i zaloguj się, by zarządzać pracownikami, działami i innymi modelami! :)


Autor

Michał Kowalski – GitHub






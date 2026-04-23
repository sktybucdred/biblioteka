# Biblioteka - wersja podstawowa (programowanie strukturalne)

# --- Dane poczatkowe ---

# Katalog ksiazek - lista slownikow
ksiazki = [
    {"tytul": "Pan Tadeusz", "autor": "Adam Mickiewicz", "sztuki": 3},
    {"tytul": "Lalka", "autor": "Boleslaw Prus", "sztuki": 2},
    {"tytul": "Wesele", "autor": "Stanislaw Wyspianski", "sztuki": 1},
    {"tytul": "Quo Vadis", "autor": "Henryk Sienkiewicz", "sztuki": 4},
    {"tytul": "Ferdydurke", "autor": "Witold Gombrowicz", "sztuki": 2},
]

# Uzytkownicy - slownik: login -> dane
uzytkownicy = {
    "anna":   {"haslo": "haslo123", "rola": "czytelnik"},
    "jan":    {"haslo": "tajne1",   "rola": "czytelnik"},
    "marta":  {"haslo": "qwerty",   "rola": "czytelnik"},
}

# Wypozyczenia - slownik: login -> lista tytulow
wypozyczenia = {
    "anna": [],
    "jan": [],
    "marta": [],
}


# --- Funkcje ---

def zaloguj():
    """Proba logowania - max 3 proby. Zwraca login lub None."""
    proby = 3
    while proby > 0:
        print("\n=== LOGOWANIE ===")
        login = input("Login: ").strip().lower()
        haslo = input("Haslo: ").strip()

        if login in uzytkownicy and uzytkownicy[login]["haslo"] == haslo:
            print(f"\nWitaj, {login}!")
            return login

        proby -= 1
        if proby > 0:
            print(f"Bledny login lub haslo. Pozostalo prob: {proby}")
        else:
            print("Przekroczono limit prob. Program zakonczony.")
    return None


def pokaz_menu():
    """Wyswietla menu glowne."""
    print("\n=== MENU ===")
    print("1. Przegladaj katalog")
    print("2. Wypozycz ksiazke")
    print("3. Moje wypozyczenia")
    print("4. Wyloguj")


def przegladaj_katalog():
    """Wyswietla wszystkie ksiazki z autorem i liczba sztuk."""
    print("\n=== KATALOG KSIAZEK ===")
    for i, ksiazka in enumerate(ksiazki, start=1):
        print(f"{i}. \"{ksiazka['tytul']}\" - {ksiazka['autor']} "
              f"(dostepne: {ksiazka['sztuki']} szt.)")


def znajdz_ksiazke(tytul):
    """Zwraca slownik ksiazki po tytule (ignoruje wielkosc liter) lub None."""
    tytul = tytul.strip().lower()
    for ksiazka in ksiazki:
        if ksiazka["tytul"].lower() == tytul:
            return ksiazka
    return None


def wypozycz_ksiazke(login):
    """Wypozycza ksiazke zalogowanemu uzytkownikowi."""
    print("\n=== WYPOZYCZENIE ===")
    tytul = input("Podaj tytul ksiazki: ")
    ksiazka = znajdz_ksiazke(tytul)

    if ksiazka is None:
        print("Nie znaleziono ksiazki o takim tytule.")
        return

    if ksiazka["sztuki"] <= 0:
        print(f"Brak dostepnych sztuk ksiazki \"{ksiazka['tytul']}\".")
        return

    # Zmniejszamy liczbe dostepnych sztuk i dodajemy do wypozyczen
    ksiazka["sztuki"] -= 1
    wypozyczenia[login].append(ksiazka["tytul"])
    print(f"Wypozyczono: \"{ksiazka['tytul']}\". Milej lektury!")


def moje_wypozyczenia(login):
    """Wyswietla ksiazki wypozyczone przez zalogowanego uzytkownika."""
    print("\n=== MOJE WYPOZYCZENIA ===")
    lista = wypozyczenia[login]

    if not lista:
        print("Nie masz zadnych wypozyczonych ksiazek.")
        return

    for i, tytul in enumerate(lista, start=1):
        print(f"{i}. {tytul}")


def uruchom_aplikacje():
    """Glowna petla aplikacji."""
    login = zaloguj()
    if login is None:
        return

    # Petla menu - az do wybrania "Wyloguj"
    while True:
        pokaz_menu()
        wybor = input("Wybierz opcje (1-4): ").strip()

        if wybor == "1":
            przegladaj_katalog()
        elif wybor == "2":
            wypozycz_ksiazke(login)
        elif wybor == "3":
            moje_wypozyczenia(login)
        elif wybor == "4":
            print(f"Do zobaczenia, {login}!")
            break
        else:
            print("Nieprawidlowy wybor. Wpisz liczbe 1-4.")


# --- Uruchomienie ---
uruchom_aplikacje()

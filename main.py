# Biblioteka - wersja OOP (Praca projektowa cz. 2)


class Book:
    """Reprezentuje ksiazke w bibliotece."""

    def __init__(self, title, author, total_copies):
        self._title = title
        self._author = author
        self._total_copies = total_copies
        self._available_copies = total_copies

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def total_copies(self):
        return self._total_copies

    @property
    def available_copies(self):
        return self._available_copies

    def borrow(self):
        """Wypozycza jeden egzemplarz. Zwraca True jesli sie udalo."""
        if self._available_copies > 0:
            self._available_copies -= 1
            return True
        return False

    def __str__(self):
        return (f'"{self._title}" - {self._author} '
                f'(dostepne: {self._available_copies}/{self._total_copies})')


class User:
    """Bazowa klasa uzytkownika."""

    def __init__(self, login, password, role):
        self._login = login
        self.__password = password  # name mangling - prawdziwa prywatnosc
        self._role = role

    @property
    def login(self):
        return self._login

    @property
    def role(self):
        return self._role

    def check_password(self, password):
        """Sprawdza haslo bez ujawniania go na zewnatrz."""
        return self.__password == password

    def __str__(self):
        return f"{self._login} ({self._role})"


class Reader(User):
    """Czytelnik - wypozycza ksiazki i prosi o przedluzenia."""

    def __init__(self, login, password):
        super().__init__(login, password, "czytelnik")
        self._borrowed_books = []          # lista referencji do Book
        self._pending_extensions = set()   # tytuly z aktywna prosba

    @property
    def borrowed_books(self):
        # zwracamy kopie, zeby nie mozna bylo modyfikowac listy z zewnatrz
        return list(self._borrowed_books)

    def add_borrowed(self, book):
        self._borrowed_books.append(book)

    def has_borrowed(self, title):
        return any(b.title.lower() == title.lower() for b in self._borrowed_books)

    def find_borrowed(self, title):
        for book in self._borrowed_books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_extension_pending(self, title):
        self._pending_extensions.add(title.lower())

    def has_pending_extension(self, title):
        return title.lower() in self._pending_extensions

    def clear_extension(self, title):
        self._pending_extensions.discard(title.lower())


class Librarian(User):
    """Bibliotekarz - zarzadza wypozyczeniami i prosbami."""

    def __init__(self, login, password):
        super().__init__(login, password, "bibliotekarz")


class ExtensionRequest:
    """Prosba o przedluzenie wypozyczenia."""

    def __init__(self, reader_login, book_title):
        self._reader_login = reader_login
        self._book_title = book_title

    @property
    def reader_login(self):
        return self._reader_login

    @property
    def book_title(self):
        return self._book_title

    def __str__(self):
        return f'{self._reader_login} -> "{self._book_title}"'


class Library:
    """Biblioteka - przechowuje ksiazki, uzytkownikow i obsluguje logike."""

    def __init__(self):
        self._books = []
        self._users = {}  # login -> User
        self._extension_requests = []

    # --- zarzadzanie kolekcjami ---

    def add_book(self, book):
        self._books.append(book)

    def add_user(self, user):
        self._users[user.login] = user

    def list_catalog(self):
        return list(self._books)

    def find_book(self, title):
        title_lower = title.strip().lower()
        for book in self._books:
            if book.title.lower() == title_lower:
                return book
        return None

    # --- autoryzacja ---

    def authenticate(self, login, password):
        """Zwraca uzytkownika jesli dane sa poprawne, inaczej None."""
        user = self._users.get(login.strip().lower())
        if user and user.check_password(password):
            return user
        return None

    # --- logika dla czytelnika ---

    def lend_book(self, reader, title):
        book = self.find_book(title)
        if book is None:
            return "Nie znaleziono ksiazki o takim tytule."
        if reader.has_borrowed(book.title):
            return f'Masz juz wypozyczona ksiazke "{book.title}".'
        if not book.borrow():
            return f'Brak dostepnych sztuk ksiazki "{book.title}".'
        reader.add_borrowed(book)
        return f'Wypozyczono: "{book.title}". Milej lektury!'

    def request_extension(self, reader, title):
        book = reader.find_borrowed(title)
        if book is None:
            return "Nie masz wypozyczonej takiej ksiazki."
        if reader.has_pending_extension(book.title):
            return f'Prosba dla "{book.title}" juz oczekuje na rozpatrzenie.'
        reader.mark_extension_pending(book.title)
        self._extension_requests.append(ExtensionRequest(reader.login, book.title))
        return f'Wyslano prosbe o przedluzenie "{book.title}".'

    # --- logika dla bibliotekarza ---

    def list_all_loans(self):
        """Lista krotek (login, ksiazka) dla wszystkich aktywnych wypozyczen."""
        loans = []
        for user in self._users.values():
            if isinstance(user, Reader):
                for book in user.borrowed_books:
                    loans.append((user.login, book))
        return loans

    def list_extension_requests(self):
        return list(self._extension_requests)

    def handle_extension_request(self, index, accept):
        """Akceptuje (accept=True) lub odrzuca prosbe. Zwraca komunikat lub None."""
        if index < 0 or index >= len(self._extension_requests):
            return None
        request = self._extension_requests.pop(index)
        # zdejmujemy flage "pending" u czytelnika
        reader = self._users.get(request.reader_login)
        if isinstance(reader, Reader):
            reader.clear_extension(request.book_title)
        decision = "zaakceptowana" if accept else "odrzucona"
        return f'Prosba {request} - {decision}.'


# === UI / petla glowna ===


def show_catalog(library):
    print("\n=== KATALOG KSIAZEK ===")
    for i, book in enumerate(library.list_catalog(), start=1):
        print(f"{i}. {book}")


def reader_borrow(library, reader):
    print("\n=== WYPOZYCZENIE ===")
    title = input("Podaj tytul ksiazki: ")
    print(library.lend_book(reader, title))


def reader_show_loans(reader):
    print("\n=== MOJE WYPOZYCZENIA ===")
    books = reader.borrowed_books
    if not books:
        print("Nie masz zadnych wypozyczonych ksiazek.")
        return
    for i, book in enumerate(books, start=1):
        marker = " [prosba o przedluzenie]" if reader.has_pending_extension(book.title) else ""
        print(f'{i}. "{book.title}" - {book.author}{marker}')


def reader_request_extension(library, reader):
    print("\n=== PROSBA O PRZEDLUZENIE ===")
    books = reader.borrowed_books
    if not books:
        print("Nie masz zadnych wypozyczonych ksiazek.")
        return
    for i, book in enumerate(books, start=1):
        print(f'{i}. "{book.title}"')
    title = input("Podaj tytul ksiazki: ")
    print(library.request_extension(reader, title))


def librarian_show_loans(library):
    print("\n=== WSZYSTKIE WYPOZYCZENIA ===")
    loans = library.list_all_loans()
    if not loans:
        print("Brak aktywnych wypozyczen.")
        return
    for i, (login, book) in enumerate(loans, start=1):
        print(f'{i}. {login} -> "{book.title}" ({book.author})')


def librarian_handle_requests(library):
    print("\n=== PROSBY O PRZEDLUZENIE ===")
    while True:
        requests = library.list_extension_requests()
        if not requests:
            print("Brak prosb do rozpatrzenia.")
            return
        for i, req in enumerate(requests, start=1):
            print(f"{i}. {req}")
        wybor = input("\nPodaj numer prosby (Enter = powrot): ").strip()
        if wybor == "":
            return
        if not wybor.isdigit():
            print("Nieprawidlowy numer.")
            continue
        index = int(wybor) - 1
        decyzja = input("Akceptujesz? (t/n): ").strip().lower()
        if decyzja not in ("t", "n"):
            print("Nieprawidlowa decyzja.")
            continue
        result = library.handle_extension_request(index, decyzja == "t")
        if result is None:
            print("Nieprawidlowy numer prosby.")
        else:
            print(result)


def show_reader_menu():
    print("\n=== MENU CZYTELNIKA ===")
    print("1. Przegladaj katalog")
    print("2. Wypozycz ksiazke")
    print("3. Moje wypozyczenia")
    print("4. Prosba o przedluzenie")
    print("5. Wyloguj")


def show_librarian_menu():
    print("\n=== MENU BIBLIOTEKARZA ===")
    print("1. Przegladaj katalog")
    print("2. Wszystkie wypozyczenia")
    print("3. Prosby o przedluzenie")
    print("4. Wyloguj")


def reader_loop(library, reader):
    while True:
        show_reader_menu()
        wybor = input("Wybierz opcje (1-5): ").strip()
        if wybor == "1":
            show_catalog(library)
        elif wybor == "2":
            reader_borrow(library, reader)
        elif wybor == "3":
            reader_show_loans(reader)
        elif wybor == "4":
            reader_request_extension(library, reader)
        elif wybor == "5":
            print(f"Do zobaczenia, {reader.login}!")
            return
        else:
            print("Nieprawidlowy wybor.")


def librarian_loop(library, librarian):
    while True:
        show_librarian_menu()
        wybor = input("Wybierz opcje (1-4): ").strip()
        if wybor == "1":
            show_catalog(library)
        elif wybor == "2":
            librarian_show_loans(library)
        elif wybor == "3":
            librarian_handle_requests(library)
        elif wybor == "4":
            print(f"Do zobaczenia, {librarian.login}!")
            return
        else:
            print("Nieprawidlowy wybor.")


def login_flow(library):
    """Logowanie - max 3 proby. Zwraca uzytkownika lub None."""
    proby = 3
    while proby > 0:
        print("\n=== LOGOWANIE ===")
        login = input("Login: ")
        haslo = input("Haslo: ")
        user = library.authenticate(login, haslo)
        if user:
            print(f"\nWitaj, {user.login}! Twoja rola: {user.role}")
            return user
        proby -= 1
        if proby > 0:
            print(f"Bledny login lub haslo. Pozostalo prob: {proby}")
        else:
            print("Przekroczono limit prob. Program zakonczony.")
    return None


def build_library():
    """Buduje biblioteke z poczatkowymi danymi (instancje klas)."""
    library = Library()

    # ksiazki
    library.add_book(Book("Pan Tadeusz", "Adam Mickiewicz", 3))
    library.add_book(Book("Lalka", "Boleslaw Prus", 2))
    library.add_book(Book("Wesele", "Stanislaw Wyspianski", 1))
    library.add_book(Book("Quo Vadis", "Henryk Sienkiewicz", 4))
    library.add_book(Book("Ferdydurke", "Witold Gombrowicz", 2))

    # czytelnicy
    library.add_user(Reader("anna", "haslo123"))
    library.add_user(Reader("jan", "tajne1"))
    library.add_user(Reader("marta", "qwerty"))

    # bibliotekarz
    library.add_user(Librarian("admin", "admin"))

    return library


def main():
    library = build_library()
    user = login_flow(library)
    if user is None:
        return
    # menu zalezne od roli (dziedziczenie + isinstance)
    if isinstance(user, Librarian):
        librarian_loop(library, user)
    elif isinstance(user, Reader):
        reader_loop(library, user)


main()

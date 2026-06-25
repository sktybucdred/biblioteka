# Biblioteka - wersja OOP + programowanie funkcyjne (Praca projektowa cz. 3)
# Styl: dataclasses + type hints + map/filter/lambda/comprehension

from dataclasses import dataclass, field


@dataclass
class Book:
    """Ksiazka w bibliotece - dataclass z automatycznym __init__/__repr__/__eq__."""

    title: str
    author: str
    total_copies: int
    available_copies: int = field(init=False)

    def __post_init__(self) -> None:
        self.available_copies = self.total_copies

    @property
    def borrowed_count(self) -> int:
        """Liczba aktualnie wypozyczonych egzemplarzy."""
        return self.total_copies - self.available_copies

    def borrow(self) -> bool:
        """Wypozycza jeden egzemplarz. Zwraca True jesli sie udalo."""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False

    def __str__(self) -> str:
        return (f'"{self.title}" - {self.author} '
                f'(dostepne: {self.available_copies}/{self.total_copies})')


@dataclass
class User:
    """Bazowy uzytkownik - haslo ukryte przed __repr__."""

    login: str
    password: str = field(repr=False)
    role: str

    def check_password(self, password: str) -> bool:
        return self.password == password


@dataclass
class Reader(User):
    """Czytelnik - wypozycza ksiazki i prosi o przedluzenia."""

    role: str = "czytelnik"
    borrowed_books: list[Book] = field(default_factory=list)
    pending_extensions: set[str] = field(default_factory=set)

    def has_borrowed(self, title: str) -> bool:
        return any(b.title.lower() == title.lower() for b in self.borrowed_books)

    def find_borrowed(self, title: str) -> Book | None:
        title_lower = title.lower()
        return next(
            (b for b in self.borrowed_books if b.title.lower() == title_lower),
            None,
        )

    def mark_extension_pending(self, title: str) -> None:
        self.pending_extensions.add(title.lower())

    def has_pending_extension(self, title: str) -> bool:
        return title.lower() in self.pending_extensions

    def clear_extension(self, title: str) -> None:
        self.pending_extensions.discard(title.lower())


@dataclass
class Librarian(User):
    """Bibliotekarz - zarzadza wypozyczeniami i prosbami."""

    role: str = "bibliotekarz"


@dataclass(frozen=True)
class ExtensionRequest:
    """Niezmienna prosba o przedluzenie (frozen=True -> hashable, auto __eq__)."""

    reader_login: str
    book_title: str

    def __str__(self) -> str:
        return f'{self.reader_login} -> "{self.book_title}"'


@dataclass(frozen=True)
class Reservation:
    """Niezmienna rezerwacja na niedostepna ksiazke."""

    reader_login: str
    book_title: str

    def __str__(self) -> str:
        return f'{self.reader_login} czeka na "{self.book_title}"'


@dataclass
class Library:
    """Biblioteka - przechowuje ksiazki, uzytkownikow i obsluguje logike."""

    books: list[Book] = field(default_factory=list)
    users: dict[str, User] = field(default_factory=dict)
    extension_requests: list[ExtensionRequest] = field(default_factory=list)
    reservations: list[Reservation] = field(default_factory=list)

    # --- zarzadzanie kolekcjami ---

    def add_book(self, book: Book) -> None:
        self.books.append(book)

    def add_user(self, user: User) -> None:
        self.users[user.login] = user

    def find_book(self, title: str) -> Book | None:
        title_lower = title.strip().lower()
        return next(
            (b for b in self.books if b.title.lower() == title_lower),
            None,
        )

    # --- programowanie funkcyjne: filtrowanie i sortowanie ---

    def filter_books(self, predicate) -> list[Book]:
        """Funkcja wyzszego rzedu - zwraca ksiazki spelniajace predykat."""
        return list(filter(predicate, self.books))

    def sorted_catalog(self, key_func, reverse: bool = False) -> list[Book]:
        """Funkcja wyzszego rzedu - zwraca katalog posortowany wg key_func."""
        return sorted(self.books, key=key_func, reverse=reverse)

    # --- autoryzacja ---

    def authenticate(self, login: str, password: str) -> User | None:
        user = self.users.get(login.strip().lower())
        if user and user.check_password(password):
            return user
        return None

    # --- logika dla czytelnika ---

    def lend_book(self, reader: Reader, title: str) -> str:
        book = self.find_book(title)
        if book is None:
            return "Nie znaleziono ksiazki o takim tytule."
        if reader.has_borrowed(book.title):
            return f'Masz juz wypozyczona ksiazke "{book.title}".'
        if not book.borrow():
            return (f'Brak dostepnych sztuk ksiazki "{book.title}". '
                    f'Mozesz ja zarezerwowac w menu rezerwacji.')
        reader.borrowed_books.append(book)
        return f'Wypozyczono: "{book.title}". Milej lektury!'

    def request_extension(self, reader: Reader, title: str) -> str:
        book = reader.find_borrowed(title)
        if book is None:
            return "Nie masz wypozyczonej takiej ksiazki."
        if reader.has_pending_extension(book.title):
            return f'Prosba dla "{book.title}" juz oczekuje na rozpatrzenie.'
        reader.mark_extension_pending(book.title)
        self.extension_requests.append(ExtensionRequest(reader.login, book.title))
        return f'Wyslano prosbe o przedluzenie "{book.title}".'

    def reserve_book(self, reader: Reader, title: str) -> str:
        book = self.find_book(title)
        if book is None:
            return "Nie znaleziono ksiazki o takim tytule."
        if book.available_copies > 0:
            return (f'Ksiazka "{book.title}" jest dostepna - '
                    f'mozesz ja od razu wypozyczyc.')
        # frozen dataclass -> mozna porownywac przez ==
        new_reservation = Reservation(reader.login, book.title.lower())
        already = any(
            r.reader_login == new_reservation.reader_login
            and r.book_title.lower() == new_reservation.book_title
            for r in self.reservations
        )
        if already:
            return f'Juz masz aktywna rezerwacje na "{book.title}".'
        self.reservations.append(Reservation(reader.login, book.title))
        return (f'Zarezerwowano "{book.title}". '
                f'Powiadomimy gdy bedzie dostepna.')

    def has_reservation(self, title: str) -> bool:
        """Czy na dany tytul istnieje aktywna rezerwacja."""
        title_lower = title.lower()
        return any(r.book_title.lower() == title_lower for r in self.reservations)

    # --- logika dla bibliotekarza ---

    def list_all_loans(self) -> list[tuple[str, Book]]:
        """Wszystkie aktywne wypozyczenia (nested list comprehension)."""
        return [
            (user.login, book)
            for user in self.users.values()
            if isinstance(user, Reader)
            for book in user.borrowed_books
        ]

    def handle_extension_request(self, index: int, accept: bool) -> str | None:
        if index < 0 or index >= len(self.extension_requests):
            return None
        request = self.extension_requests.pop(index)
        reader = self.users.get(request.reader_login)
        if isinstance(reader, Reader):
            reader.clear_extension(request.book_title)
        decision = "zaakceptowana" if accept else "odrzucona"
        return f'Prosba {request} - {decision}.'

    def get_statistics(self) -> dict:
        """Statystyki - styl funkcyjny (map/filter/comprehension, bez akumulacji)."""
        readers = [u for u in self.users.values() if isinstance(u, Reader)]
        return {
            "most_popular": (
                max(self.books, key=lambda b: b.borrowed_count) if self.books else None
            ),
            "total_loans": sum(map(lambda r: len(r.borrowed_books), readers)),
            "readers_ranking": [
                (r.login, len(r.borrowed_books))
                for r in sorted(readers, key=lambda r: len(r.borrowed_books), reverse=True)
            ],
        }


# === UI / petla glowna ===


def show_filtered_catalog(library: Library, predicate, header: str) -> None:
    """Funkcja wyzszego rzedu - wyswietla katalog przefiltrowany podanym predykatem."""
    print(f"\n=== {header} ===")
    books = library.filter_books(predicate)
    if not books:
        print("Brak ksiazek spelniajacych kryteria.")
        return
    for i, book in enumerate(books, start=1):
        print(f"{i}. {book}")


def show_sorted_catalog(library: Library) -> None:
    print("\n=== SORTUJ WG ===")
    print("1. Tytulu (A-Z)")
    print("2. Autora (A-Z)")
    print("3. Liczby dostepnych sztuk (malejaco)")
    print("4. Powrot")
    wybor = input("Wybierz opcje: ").strip()
    if wybor == "4":
        return
    # slownik konfiguracji sortowania - kazdy klucz: (etykieta, key_func, reverse)
    sort_options = {
        "1": ("TYTUL", lambda b: b.title.lower(), False),
        "2": ("AUTOR", lambda b: b.author.lower(), False),
        "3": ("DOSTEPNE SZTUKI", lambda b: b.available_copies, True),
    }
    if wybor not in sort_options:
        print("Nieprawidlowy wybor.")
        return
    label, key_func, reverse = sort_options[wybor]
    books = library.sorted_catalog(key_func, reverse=reverse)
    print(f"\n=== KATALOG (sort: {label}) ===")
    for i, book in enumerate(books, start=1):
        print(f"{i}. {book}")


def catalog_menu(library: Library) -> None:
    """Sub-menu przegladania katalogu - rozne tryby filtrowania i sortowania."""
    while True:
        print("\n=== KATALOG - WIDOK ===")
        print("1. Wszystkie ksiazki")
        print("2. Tylko dostepne (sztuki > 0)")
        print("3. Wyszukaj po frazie (tytul/autor)")
        print("4. Sortowanie")
        print("5. Powrot")
        wybor = input("Wybierz opcje: ").strip()
        if wybor == "1":
            show_filtered_catalog(library, lambda _: True, "WSZYSTKIE KSIAZKI")
        elif wybor == "2":
            show_filtered_catalog(
                library,
                lambda b: b.available_copies > 0,
                "DOSTEPNE KSIAZKI",
            )
        elif wybor == "3":
            phrase = input("Podaj fraze: ").strip().lower()
            if not phrase:
                print("Pusta fraza - anulowano.")
                continue
            show_filtered_catalog(
                library,
                lambda b: phrase in b.title.lower() or phrase in b.author.lower(),
                f"WYNIKI WYSZUKIWANIA: '{phrase}'",
            )
        elif wybor == "4":
            show_sorted_catalog(library)
        elif wybor == "5":
            return
        else:
            print("Nieprawidlowy wybor.")


def reader_borrow(library: Library, reader: Reader) -> None:
    print("\n=== WYPOZYCZENIE ===")
    title = input("Podaj tytul ksiazki: ")
    print(library.lend_book(reader, title))


def reader_reserve(library: Library, reader: Reader) -> None:
    print("\n=== REZERWACJA NIEDOSTEPNEJ KSIAZKI ===")
    unavailable = library.filter_books(lambda b: b.available_copies == 0)
    if not unavailable:
        print("Wszystkie ksiazki sa aktualnie dostepne - mozesz je wypozyczyc.")
        return
    print("Ksiazki aktualnie niedostepne:")
    for i, book in enumerate(unavailable, start=1):
        print(f'{i}. "{book.title}" - {book.author}')
    title = input("\nPodaj tytul do rezerwacji: ")
    print(library.reserve_book(reader, title))


def reader_show_loans(reader: Reader) -> None:
    print("\n=== MOJE WYPOZYCZENIA ===")
    books = reader.borrowed_books
    if not books:
        print("Nie masz zadnych wypozyczonych ksiazek.")
        return
    for i, book in enumerate(books, start=1):
        marker = " [prosba o przedluzenie]" if reader.has_pending_extension(book.title) else ""
        print(f'{i}. "{book.title}" - {book.author}{marker}')


def reader_request_extension(library: Library, reader: Reader) -> None:
    print("\n=== PROSBA O PRZEDLUZENIE ===")
    books = reader.borrowed_books
    if not books:
        print("Nie masz zadnych wypozyczonych ksiazek.")
        return
    for i, book in enumerate(books, start=1):
        print(f'{i}. "{book.title}"')
    title = input("Podaj tytul ksiazki: ")
    print(library.request_extension(reader, title))


def librarian_show_loans(library: Library) -> None:
    print("\n=== WSZYSTKIE WYPOZYCZENIA ===")
    loans = library.list_all_loans()
    if not loans:
        print("Brak aktywnych wypozyczen.")
        return
    for i, (login, book) in enumerate(loans, start=1):
        print(f'{i}. {login} -> "{book.title}" ({book.author})')


def librarian_handle_requests(library: Library) -> None:
    print("\n=== PROSBY O PRZEDLUZENIE ===")
    while True:
        requests = library.extension_requests
        if not requests:
            print("Brak prosb do rozpatrzenia.")
            return
        for i, req in enumerate(requests, start=1):
            marker = (
                " [REZERWACJA na ta ksiazke]"
                if library.has_reservation(req.book_title)
                else ""
            )
            print(f"{i}. {req}{marker}")
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


def librarian_show_statistics(library: Library) -> None:
    print("\n=== STATYSTYKI BIBLIOTEKI ===")
    stats = library.get_statistics()

    pop = stats["most_popular"]
    if pop is None:
        print("Brak ksiazek w bazie.")
    else:
        print(f'Najpopularniejsza ksiazka: "{pop.title}" - {pop.author}')
        print(f'  Wypozyczonych egzemplarzy: {pop.borrowed_count}/{pop.total_copies}')

    print(f"\nLaczna liczba aktywnych wypozyczen: {stats['total_loans']}")

    print("\nRanking czytelnikow (wg liczby wypozyczen):")
    ranking = stats["readers_ranking"]
    if not ranking:
        print("  (brak czytelnikow)")
        return
    for i, (login, count) in enumerate(ranking, start=1):
        print(f"  {i}. {login} - {count} ksiazek")


def show_reader_menu() -> None:
    print("\n=== MENU CZYTELNIKA ===")
    print("1. Przegladaj katalog")
    print("2. Wypozycz ksiazke")
    print("3. Zarezerwuj niedostepna ksiazke")
    print("4. Moje wypozyczenia")
    print("5. Prosba o przedluzenie")
    print("6. Wyloguj")


def show_librarian_menu() -> None:
    print("\n=== MENU BIBLIOTEKARZA ===")
    print("1. Przegladaj katalog")
    print("2. Wszystkie wypozyczenia")
    print("3. Prosby o przedluzenie")
    print("4. Statystyki")
    print("5. Wyloguj")


def reader_loop(library: Library, reader: Reader) -> None:
    while True:
        show_reader_menu()
        wybor = input("Wybierz opcje (1-6): ").strip()
        if wybor == "1":
            catalog_menu(library)
        elif wybor == "2":
            reader_borrow(library, reader)
        elif wybor == "3":
            reader_reserve(library, reader)
        elif wybor == "4":
            reader_show_loans(reader)
        elif wybor == "5":
            reader_request_extension(library, reader)
        elif wybor == "6":
            print(f"Do zobaczenia, {reader.login}!")
            return
        else:
            print("Nieprawidlowy wybor.")


def librarian_loop(library: Library, librarian: Librarian) -> None:
    while True:
        show_librarian_menu()
        wybor = input("Wybierz opcje (1-5): ").strip()
        if wybor == "1":
            catalog_menu(library)
        elif wybor == "2":
            librarian_show_loans(library)
        elif wybor == "3":
            librarian_handle_requests(library)
        elif wybor == "4":
            librarian_show_statistics(library)
        elif wybor == "5":
            print(f"Do zobaczenia, {librarian.login}!")
            return
        else:
            print("Nieprawidlowy wybor.")


def login_flow(library: Library) -> User | str | None:
    """Logowanie - max 3 proby. Zwraca uzytkownika, None po 3 bledach, lub 'EXIT'."""
    proby = 3
    while proby > 0:
        print("\n=== LOGOWANIE ===")
        print("(wpisz 'q' jako login aby zakonczyc program)")
        login = input("Login: ")
        if login.strip().lower() == "q":
            return "EXIT"
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


def build_library() -> Library:
    library = Library()

    library.add_book(Book("Pan Tadeusz", "Adam Mickiewicz", 3))
    library.add_book(Book("Lalka", "Boleslaw Prus", 2))
    library.add_book(Book("Wesele", "Stanislaw Wyspianski", 1))
    library.add_book(Book("Quo Vadis", "Henryk Sienkiewicz", 4))
    library.add_book(Book("Ferdydurke", "Witold Gombrowicz", 2))

    library.add_user(Reader("anna", "haslo123"))
    library.add_user(Reader("jan", "tajne1"))
    library.add_user(Reader("marta", "qwerty"))

    library.add_user(Librarian("admin", "admin"))

    return library


def main() -> None:
    library = build_library()
    while True:
        user = login_flow(library)
        if user is None or user == "EXIT":
            print("Do widzenia!")
            return
        if isinstance(user, Librarian):
            librarian_loop(library, user)
        elif isinstance(user, Reader):
            reader_loop(library, user)
        # po wylogowaniu wracamy do ekranu logowania


main()

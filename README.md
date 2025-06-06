# Bot Discordowy do Śledzenia Druków Sejmowych

Ten bot Discordowy dostarcza informacji o drukach Sejmu oraz pozwala użytkownikom śledzić konkretne druki pod kątem zmian a także generuje raporty o ostatnich drukach.

## Funkcje

*   **!druk [numer]**: Wyświetla szczegółowe informacje o druku sejmowym na podstawie jego numeru.
*   **!obserwuj [numer]**: Dodaje druk do Twojej listy obserwowanych. Otrzymasz powiadomienia, gdy `changeDate` druku zostanie zaktualizowane.
*   **!anuluj [numer]**: Usuwa druk z Twojej listy obserwowanych.
*   **!moje_druki**: Wyświetla listę wszystkich druków, które aktualnie obserwujesz.
*   **!raport [dni=7]**: Generuje raport druków sejmowych z ostatnich X dni (domyślnie 7 dni).
*   **!ustaw_kanał**: (Tylko dla administratorów) Ustawia bieżący kanał jako kanał do raportów tygodniowych.
*   **!pomoc**: Wyświetla listę dostępnych komend.

## Konfiguracja

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/kingbrucelee/sejm-print-bot.git
    cd sejm-print-bot
    ```

2.  **Utwórz wirtualne środowisko (zalecane):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Na Windowsie: `venv\Scripts\activate`
    ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Formatowanie kodu (Black):**
    Projekt używa [Black](https://github.com/psf/black) do automatycznego formatowania kodu. Zaleca się uruchomienie Black na swoim kodzie przed przesłaniem zmian, aby zapewnić spójny styl. Możesz zainstalować Black za pomocą pip:
    ```bash
    pip install black
    ```
    A następnie uruchomić go w katalogu głównym projektu:
    ```bash
    black .
    ```

5.  **Skonfiguruj zmienne środowiskowe:**
    Utwórz plik `.env` w głównym katalogu projektu i dodaj token swojego bota Discordowego:
    ```
    DISCORD_TOKEN=TWÓJ_TOKEN_BOTA_DISCORD
    ```
    Zastąp `TWÓJ_TOKEN_BOTA_DISCORD` rzeczywistym tokenem bota.

5.  **Uruchom bota:**
    ```bash
    python src/main.py
    ```

## Struktura Projektu

*   `src/`: Zawiera główny kod aplikacji.
    *   `main.py`: Główny punkt wejścia dla bota.
    *   `config.py`: Ustawienia konfiguracyjne dla punktów końcowych API, ścieżek plików i harmonogramów zadań.
    *   `cogs/`: Moduły (cogs) Discord.py do organizacji komend.
        *   `prints_info.py`: Komendy związane z pobieraniem informacji o drukach.
        *   `prints_watch.py`: Komendy do zarządzania obserwowanymi drukami.
        *   `reports.py`: Komendy do generowania i wysyłania raportów.
        *   `print_watcher.py`: Zadanie w tle do sprawdzania obserwowanych druków.
    *   `tasks/`: Zadania w tle dla bota.
        *   `print_watcher.py`: Inicjuje i uruchamia zadanie obserwowania druków.
        *   `weekly_report.py`: Inicjuje i uruchamia zadanie raportu tygodniowego.
    *   `utils/`: Funkcje pomocnicze.
        *   `file_operations.py`: Funkcje do odczytu i zapisu pliku `watched_prints.json`.
*   `data/`: Przechowuje trwałe dane, takie jak `watched_prints.json`.
*   `tests/`: Katalog na testy jednostkowe.
*   `.env`: Zmienne środowiskowe (np. `DISCORD_TOKEN`).
*   `requirements.txt`: Lista zależności Pythona.
*   `.gitignore`: Określa pliki i katalogi ignorowane przez Git.

## Referencje API

Ten bot komunikuje się z API Sejmu 10 kadencji: `https://api.sejm.gov.pl/sejm/term10`

*   **Endpoint Druków:** `/prints`
*   **Endpoint Procesów:** `/processes`

## Wskazówki dla Współtwórców

Chętnie przyjmujemy wszelkie wkłady w rozwój bota! Oto kilka wskazówek na początek:

*   Zapoznaj się ze strukturą projektu (`Struktura Projektu` powyżej), aby zrozumieć, gdzie znajdują się poszczególne części kodu.
*   Jeśli chcesz dodać nową komendę, rozważ utworzenie nowego "cog" w katalogu `src/cogs/`.
*   Dla zadań działających w tle, zajrzyj do katalogu `src/tasks/`.
*   Funkcje pomocnicze, które mogą być używane w wielu miejscach, powinny znaleźć się w `src/utils/`.
*   Pamiętaj o dodawaniu docstringów do swojego kodu, aby wyjaśnić jego działanie.
*   Użyj formattera Black (`Formatowanie kodu (Black)` powyżej), aby Twój kod był spójny ze stylem projektu.
*   Jeśli masz pytania lub potrzebujesz pomocy, nie wahaj się otworzyć zgłoszenie (issue) w repozytorium.

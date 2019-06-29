# Zaawansowane techniki integracji systemów
```Temat 8: Środowisko do pobierania i przechowywania informacji z portalu blogowego salon24```

W ramach zadania eksplorowane były dane z serwisu blogowego salon24. Pierwszym krokiem wykonania projektu było przygotowanie aplikacji pobierającej dane ze strony serwisu (tzw. web scrapera). Portal blogowy oferuje możliwość przeglądnięcia wszystkich blogów z odpowiednim sortowaniem. Po otworzeniu danego bloga jest możliwość przejrzenia wszystkich notek oraz sprawdzenia właściciela bloga, komentarzy oraz ilości udostępnień na popularnych serwisach społecznościowych. Program pobrał te wszystkie dane i zapisał je do bazy danych MySQL.

### Zależności

- requests
- MySQLdb
- BeautifulSoup4
- html2text
- json

### Uruchomienie

Pobieranie linków do blogów

```
python download_blog_urls.py
```

Pobieranie danych

```
python run.py
```

### Baza danych

https://www.dropbox.com/s/zc5t6fg18ma6nbi/salon24_db.7z?dl=0

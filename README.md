# Mini Platforma Danych w Kontenerach Docker

## Przegląd
Projekt ten stanowi kompletną, skonteneryzowaną platformę danych typu End-to-End, która służy jako cyfrowy symulator sklepu muzycznego sprzedającego płyty CD. System odwzorowuje realny obieg informacji w przedsiębiorstwie: od momentu rejestracji sprzedaży, przez przetwarzanie strumieniowe, aż po analityczne składowanie danych w chmurze (Data Lake).

Projekt jest strukturalnie podzielony na 6 zadań, każde budujące na poprzednim. Ten README zawiera objaśnienie instrukcji niezbędnych do korzystania z projektu, omówienie poszczególnych warstw oraz metod sprawdzania, jak każda z tych warstw działa.

## Wymagania wstępne
- Zainstalowane Dockera
- Zainstalowanie Pythona (najlepiej w wersji 3.13)

## Struktura projektu
- `criteria/`: Formalne wymagania projektu
- `data/`: Pliki danych CSV (albumy.csv, klienci.csv, zamowienia.csv)
- `data_scripts/`: Skrypty Python dla operacji PostgreSQL
- `kafka/`: Skrypt Python uruchamiający konsumera Kafki
- `misc/`: Folder na pliki różnorodne (np. analiza pobranego pliku .parquet, z minio)
- `spark/`: Skrypty przetwarzania Spark
- `.env-example`: Szablon wartości wrażliwych wywoływanych przez projekt, służącego do stworzenia pliku .env
- `docker-compose.yml`: Konfiguracja usług Docker
- `init.sql`: Skrypt inicjalizacji PostgreSQL
- `requirements.txt`: Zależności Python wymaganych do projektu

## Wstępne przygotowanie projektu
Aby przygotowac projekt, polecane jest wytworzenie środowiska wirtualnego Python 3.13, instalując zależności z pliku requirements.txt.
   ```bash
   python3.13 -m venv .venv # Utworzenie środowiska wirtualnego w Pythonie 3.13
   .venv\Scripts\Activate # Uruchomienie środowiska wirtualnego
   pip install -r requirements.txt # Pobranie zależności do środowiska
   ```
Następnie, nalezy przygotować plik .env, uzupełniając wszystkie istotnego wartości. Plik .env można wytworzyć na podstawie szablonu zawartego w .env-example. Gdy zależności zostaną zainstalowane oraz gdy plik .env zostanie utworzony (z zdefiniowanymi polami), należy uruchomić Dockerowy projekt korzystając z pliku docker-compose.yml.
   ```bash
   docker-compose up -d # Zbudowanie projektu Dockerowego
   ```

## Zadania

### Zadanie 1: Symulacja procesu biznesowego z Pythonem
**Cel**: Utworzenie skryptu Python, który czyta trzy pliki CSV, tworzy tabele w PostgreSQL dynamicznie i wprowadza dane.

**Objaśnienie**:
Docker buduje kontekst bazy danych w PostgreSQL automatycznie, przy użyciu poniżego skryptu:
   ```bash
   python data_scripts/r_generuj_kontekst_bd.py # Wywoływana jednorazowo przy zastosowaniu 'docker-compuse up -d'
   ```
Uruchom skrypt Python wstawiający pojednyńczy rekord do kontekstu, symulując proces biznesowy:
   ```bash
   python data_scripts/r_wstaw_album.py # Wstawienie nowego albumu
   python data_scripts/r_wstaw_klienta.py # Wstawienie nowego klienta
   python data_scripts/r_wstaw_zamowienie.py # Wstawienie nowego zamówienia
   ```
Zweryfikuj proces wprowadzenia danych, łącząc się z PostgreSQL, sprawdzając tabele w kontekście:
   ```bash
    python data_scripta/r_wyswietl_kontekst_bd.py # Wyświetlenie kontekstu bd
   ```

### Zadanie 2: Łączenie Debezium do przechwytywania zmian w PostgreSQL
**Cel**: Skonfigurowanie Debezium do monitorowania zmian w PostgreSQL i wysyłania ich do Kafka w formacie JSON.

**Objaśnienie**:
Docker buduje warstwę Debezium oraz jej łącznik z PostgreSQL automatycznie (wywoływując odpowiednie kontenery, w docker-compose.yml). Aby zobaczyć jak działa warstwa Debezium, należy dokonać podglądu logów który można wykonać bezpośrednio w Dockerze lub stosując odpowiednie polecenie w terminu:
   ```bash
   docker logs -f trp_debezium --tail 10 # Wyświetlenie logów kontenera Debezium
   ```
   Przykładowy payload, wykrywający zmianę dotyczącą wstawiania nowego rekordu do PostgreSQL
   ```
   1 records sent during previous 00:04:40.561, last recorded offset of {server=dbserver1} partition is {transaction_id=null, lsn_proc=26912888, messageType=INSERT, lsn_commit=26912600, lsn=26912888, txId=741, ts_usec=1776152625703676}
   ```

### Zadanie 3: Ustawienie Kafki i strumieniowanie zdarzeń w formacie JSON
**Cel**: Ustawienie klastra Kafka z serializacją JSON i Schema Registry oraz utworzenia konsumera Kafki, do nadzorowania zmian.

**Objaśnienie**:
Docker łączy warstwę Debezium z Kafką, wstawiając wszystkie zmiany wykryte przez Debezium do topików (tabeli) Kafki. Aby mieć podgląd do zmian należy wywołać konsumera kafki, który wykrywa wszelkie zmiany na topikach Kafki. Docker automatycznie buduje oddzielny kontener zarówno dla Kafki jak i dla konsumera. Kontener Kafki buduje na postawie pliku docker-compose.yml, a konsumera kafki buduje korzystając z skryptu Python:
   ```bash
   python kafka/kafka_consumer.py # Utworzenie konsumera kafki, monitorującego zmiany w zdefiniowanych topikach
   docker logs -f trp_kafka-consumer # Wyświetlenie logów konsumera kafki
   ```
Przykładowy Payload:
   ```
   [2026-04-14T07:43:46.399] [klienci] INSERT
   key   : {'idKlienta': 9}
   record: {
    "idKlienta": 9,
    "imie": "Johnny",
    "nazwisko": "Test",
    "telefon": "909909909",
    "email": "jt@gmail.com"
   }
   ```
Zmiany w topikach można równiez wyświetlić w KafkaUI (specjalny interfejs przeznaczony do Kafki), dostępny na witrynie http://localhost:8080/

### Zadanie 4: Integracja Spark z Kafką do przetwarzania danych
**Cel**: Użycie Spark Structured Streaming do czytania wiadomości JSON z Kafki i wykonywania transformacji.

**Objaśnienie**: 
Zmiany wewnątrz topików Kafki są przekształcane przez sesje (jobs) Sparka, aby przekształcić dane do odpowiedniego formatu i przekazać ja do dalszych warstw. Sesje te działają w trybie stałym, wykrywając zmiany takie jak dodawanie, usuwanie lub aktualizowanie danych. Docker automatycznie tworzy kontener łączący warstwę Kafki ze Sparkiem. Następnie generuje sesje Spark, operujące osobno na poszczególnym topiku Kafki. Programy są generowane ze skryptów Python: 
```bash
   python spark/process_album.py # Sesja wykyrwająca zmiany na tabeli topika Kafki dotyczącego albumów.
   python spark/process_klientów.py # Sesja wykyrwająca zmiany na tabeli topika Kafki dotyczącego albumów.
   python spark/process_zamówień.py # Sesja wykyrwająca zmiany na tabeli topika Kafki dotyczącego albumów.
   docker logs -f trp_spark-klienci-job # Wyświetlenie logów danego kontenera Sesji (w tym wypadku topika 'Klienci')   
   ```
Przykładowy payload wykrycia zmiany w topiku Kafki przez Spark:
```
   26/04/14 09:06:01 INFO MicroBatchExecution: Streaming query made progress: {
  "id" : "0e500ad1-f55f-4f2e-8af9-c6a61c57f9a4",
  "runId" : "0a08f919-2408-4100-bcc9-9ff12026dfb5",
  "name" : null,
  "timestamp" : "2026-04-14T09:06:00.001Z",
  "batchId" : 3,
  "numInputRows" : 1, # Wprowadzony nowy rekord
  "inputRowsPerSecond" : 0.09999000099990002,
  "processedRowsPerSecond" : 0.6169031462060457....
```

### Zadanie 5: Przechowywanie przetworzonych danych w MinIO używając Delta Lake
**Cel**: Skonfigurowanie MinIO i zapisywanie DataFrames Spark w formacie Delta.

**Objaśnienie**:
Spark po przekształceniu danych następnie wysyła dane do Minio, serwisu tworzącego chmurę służącą do przechowywania danych w sieci. Docker automatycznie łączy warstwy Spark z Minio korzystając z pliku docker-compose.yml:

Wprowadzone dane są dostępne na http://localhost:9090/. Należy wprowadzić dane konta zdefiniowanego w pliku .env

### Zadanie 6: Automatyzacja wdrażania i zapewnienie niezawodności
**Cel**: Pełna automatyzacja procesu wdrażania za pomocą docker-compose.

**Objaśnienie**:
Docker buduje cały projekt automatycznie, wykorzystując plik docker-compose.yml. Poniższe polecenia pomagają w konstrukcji, usunięciu lub restarcie Dockerowego projektu.
```bash
   docker-compose up -d # Zbudowanie projektu
   docker-compose down -v # Usunięcie projektu
   docker-compose down -v && docker-compose up -d # Reset projektu
   ```

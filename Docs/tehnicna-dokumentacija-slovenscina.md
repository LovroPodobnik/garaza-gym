# Tehnična dokumentacija za integracijo Cardskipper in IVMS

## Pregled sistema

Integracijska rešitev omogoča samodejno sinhronizacijo datumov veljavnosti članstva med sistemom Cardskipper za upravljanje članov in sistemom IVMS za nadzor dostopa. Ko člani podaljšajo svoje članstvo v Cardskipperju, se njihovi dostopni privilegiji v IVMS sistemu samodejno posodobijo.

## Arhitektura sistema

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Cardskipper │         │   Vmesna     │         │     IVMS    │
│    API      │◄────────┤  aplikacija   ├────────►│   Sistem    │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │   Lokalna    │
                        │  podatkovna  │
                        │     baza     │
                        └──────────────┘
```

### Komponente sistema

1. **Cardskipper API Odjemalec**
   - Avtentikacija s Cardskipper API-jem
   - Pridobivanje seznama aktivnih članov
   - Pridobivanje informacij o datumih veljavnosti

2. **IVMS API Odjemalec**
   - Avtentikacija z IVMS sistemom
   - Iskanje uporabnikov po e-poštnih naslovih
   - Posodabljanje datumov veljavnosti uporabnikov

3. **Lokalna podatkovna baza**
   - Spremljanje zadnjega znanega stanja članov
   - Zaznavanje sprememb v datumih veljavnosti
   - Revizijska sled vseh sinhronizacij

4. **Sinhronizacijska storitev**
   - Orkestracija procesa sinhronizacije
   - Izvajanje v ozadju kot sistemska storitev
   - Obravnavanje napak in ponovni poskusi

## Tehnične specifikacije

### Cardskipper API

**Osnovni URL-ji:**
- Produkcija: `https://api.cardskipper.se`
- Test: `https://api-test.cardskipper.se`

**Avtentikacija:**
- Osnovna avtentikacija (uporabniško ime/geslo)
- Potreben je administratorski račun z API dostopom

**Ključni končni točki:**

1. **Pridobivanje informacij o organizaciji**
   - Pot: `/Organisation/Info/`
   - Metoda: GET
   - Namen: Pridobivanje informacij o organizaciji in vlogah

2. **Iskanje članov**
   - Pot: `/Member/Export/`
   - Metoda: POST z XML vsebino
   - Namen: Pridobivanje aktivnih članov z datumi veljavnosti
   - Zahtevana XML oblika:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <SearchCriteriaMember xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
       <OrganisationId>[ID_VAŠE_ORGANIZACIJE]</OrganisationId>
       <OnlyActive>true</OnlyActive>
   </SearchCriteriaMember>
   ```

### IVMS API

**Osnovni URL:**
- `http://<ip_naprave>:<vrata>/ISAPI/`

**Avtentikacija:**
- Osnovna avtentikacija (uporabniško ime:geslo v Base64 kodiranju)
- Glave:
  - Content-Type: application/xml
  - Authorization: Basic [base64-kodirani-podatki]

**Ključni končni točki:**

1. **Iskanje uporabnikov**
   - Pot: `/ISAPI/AccessControl/UserInfo/search`
   - Metoda: POST
   - XML vsebina:
   ```xml
   <UserInfoSearch>
     <searchID>1</searchID>
     <searchResultPosition>0</searchResultPosition>
     <maxResults>100</maxResults>
   </UserInfoSearch>
   ```
   - Odgovor: Seznam uporabnikov z njihovimi ID-ji, imeni in e-poštnimi naslovi

2. **Posodobitev veljavnosti uporabnika**
   - Pot: `/ISAPI/AccessControl/UserInfo/modify`
   - Metoda: PUT
   - XML vsebina:
   ```xml
   <UserInfo>
     <employeeNo>[ID_UPORABNIKA]</employeeNo>
     <Valid>
       <enable>true</enable>
       <beginTime>[ZAČETNI_DATUM]</beginTime>
       <endTime>[KONČNI_DATUM]</endTime>
     </Valid>
   </UserInfo>
   ```
   - Format datuma: YYYY-MM-DDThh:mm:ss (npr. 2025-02-04T00:00:00)

### Podatkovna baza

Lokalna podatkovna baza hrani naslednje informacije:

```sql
CREATE TABLE members (
    email TEXT PRIMARY KEY,
    organization_member_id TEXT,
    start_date TEXT,
    end_date TEXT,
    first_name TEXT,
    last_name TEXT,
    ivms_employee_no TEXT,
    member_code TEXT,
    role_id TEXT,
    role_name TEXT,
    phone TEXT
);

CREATE TABLE sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    cardskipper_id TEXT NOT NULL,
    ivms_id TEXT NOT NULL,
    previous_end_date TEXT,
    new_end_date TEXT,
    sync_status TEXT,
    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sync_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    error_message TEXT,
    error_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);
```

## Algoritem sinhronizacije

Sinhronizacijski proces poteka na naslednji način:

1. **Pridobivanje podatkov iz Cardskipperja**
   - Pridobi vse aktivne člane preko API klica
   - Izlušči e-poštne naslove in datume veljavnosti

2. **Pridobivanje podatkov iz IVMS**
   - Pridobi vse uporabnike preko API klica
   - Ustvari preslikavo e-poštnih naslovov v ID-je uporabnikov

3. **Primerjava in zaznavanje sprememb**
   - Pridobi zadnje znano stanje iz lokalne baze
   - Primerjaj nove datume veljavnosti s shranjenimi datumi
   - Identificiraj člane, ki potrebujejo posodobitev

4. **Posodobitev IVMS uporabnikov**
   - Za vsakega člana, ki potrebuje posodobitev:
     - Najdi ustrezni IVMS ID preko e-poštnega naslova
     - Pošlji zahtevo za posodobitev datuma veljavnosti
     - Zabeleži rezultat sinhronizacije

5. **Posodobitev lokalne baze**
   - Posodobi zapise članov z novimi datumi
   - Zabeleži vse operacije v zgodovino sinhronizacij

## Obravnavanje napak

1. **Ponovno poskušanje**
   - Začasne napake (npr. omrežne težave) se ponovno poskusijo do 3-krat
   - Progresivno povečevanje časa med poskusi

2. **Beleženje napak**
   - Vse napake se beležijo v tabelo `sync_errors`
   - Zapisi vključujejo e-poštni naslov, sporočilo napake in časovni žig

3. **Obveščanje o napakah**
   - Kritične napake sprožijo e-poštno obvestilo (opcijsko)
   - Dnevnik napak je na voljo za pregled v administratorskem vmesniku

## Varnostni vidiki

1. **Varno shranjevanje poverilnic**
   - Poverilnice API-jev se shranjujejo v okoljskih spremenljivkah
   - Ne shranjujemo poverilnic v izvorni kodi

2. **Šifrirana komunikacija**
   - Uporaba HTTPS za Cardskipper API
   - Omejen IP dostop do IVMS API-ja, kjer je to mogoče

3. **Logiranje in revizijska sled**
   - Beleženje vseh operacij za revizijske namene
   - Beleženje samo nujno potrebnih podatkov za delovanje

## Možnosti namestitve

### 1. Linux sistemska storitev

```bash
# Ustvarjanje sistemske storitve
sudo nano /etc/systemd/system/cardskipper-ivms.service

# Vsebina datoteke
[Unit]
Description=Cardskipper to IVMS Synchronization Service
After=network.target

[Service]
User=uporabnik
WorkingDirectory=/pot/do/aplikacije
ExecStart=/pot/do/aplikacije/venv/bin/python /pot/do/aplikacije/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Aktiviranje in zagon storitve
sudo systemctl enable cardskipper-ivms.service
sudo systemctl start cardskipper-ivms.service
```

### 2. Docker namestitev

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Zagon Docker kontejnerja:

```bash
docker build -t cardskipper-ivms-sync .
docker run -d \
  --name cardskipper-ivms \
  --restart unless-stopped \
  -e CARDSKIPPER_API_URL=https://api.cardskipper.se \
  -e CARDSKIPPER_USERNAME=uporabnisko_ime \
  -e CARDSKIPPER_PASSWORD=geslo \
  -e CARDSKIPPER_ORGANIZATION_ID=123 \
  -e IVMS_DEVICE_IP=192.168.1.100 \
  -e IVMS_PORT=80 \
  -e IVMS_USERNAME=admin \
  -e IVMS_PASSWORD=geslo \
  -e SYNC_INTERVAL_MINUTES=15 \
  -v $(pwd)/data:/app/data \
  cardskipper-ivms-sync
```

## Konfiguracija

Nastavitve aplikacije se lahko konfigurirajo preko okoljskih spremenljivk ali konfiguracijske datoteke:

```ini
[Cardskipper]
API_URL = https://api.cardskipper.se
USERNAME = uporabnisko_ime
PASSWORD = geslo
ORGANIZATION_ID = 123

[IVMS]
DEVICE_IP = 192.168.1.100
PORT = 80
USERNAME = admin
PASSWORD = geslo

[Sync]
INTERVAL_MINUTES = 15
EMAIL_NOTIFICATIONS = true
NOTIFICATION_EMAIL = admin@primer.si
```

## Vzdrževanje in nadzor

### Dnevniške datoteke

Aplikacija zapisuje aktivnosti v dnevniške datoteke:

- `app.log`: Splošne operacije aplikacije
- `error.log`: Podrobnosti o napakah
- `sync.log`: Podrobnosti o sinhronizacijskih operacijah

### Nadzorna plošča

Opcijsko lahko namestite spletno nadzorno ploščo, ki omogoča:

- Pregled stanja sinhronizacije
- Ročno proženje sinhronizacije
- Pregled zgodovine sinhronizacij in napak
- Reševanje problematičnih primerov

### Redno vzdrževanje

Priporočene aktivnosti rednega vzdrževanja:

1. Preverjanje dnevniških datotek za morebitne napake
2. Preverjanje prostora na disku za podatkovno bazo
3. Periodično varnostno kopiranje podatkovne baze
4. Preverjanje dostopnosti Cardskipper in IVMS API-jev

## Zaključek

Ta tehnična dokumentacija opisuje zasnovo in delovanje integracijske rešitve med sistemoma Cardskipper in IVMS. Implementacija sledi najboljšim praksam za varnost, zanesljivost in vzdrževanje, hkrati pa omogoča fleksibilnost pri namestitvi in konfiguraciji.

Za dodatna vprašanja ali podporo se obrnite na: [kontaktni e-naslov]
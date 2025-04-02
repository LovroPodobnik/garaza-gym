# Ponudba za integracijo Cardskipper in IVMS

## Povzetek rešitve

Predlagamo celovito rešitev za avtomatsko sinhronizacijo datumov veljavnosti članstva med sistemoma Cardskipper in IVMS. S to integracijo bo podaljšanje članstva v Cardskipperju samodejno posodobilo dostopne pravice v sistemu IVMS.

### Ključne prednosti

- **Popolna avtomatizacija**: Brez potrebe po ročnem posodabljanju podatkov v dveh sistemih
- **Zanesljivost**: Odstranitev človeških napak pri prenosu podatkov
- **Hitrost**: Člani takoj pridobijo dostop po podaljšanju članstva
- **Prihranek časa**: Pomembno zmanjšanje administrativnega dela za osebje

## Tehnična zasnova rešitve

### Arhitektura sistema

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

### Delovanje sistema

1. **Pridobivanje podatkov iz Cardskipperja**:
   - Redni API klici za pridobivanje seznama aktivnih članov
   - Beleženje datumov veljavnosti članstva

2. **Primerjava s prejšnjim stanjem**:
   - Zaznavanje sprememb v datumih veljavnosti članstva
   - Identifikacija članov, ki potrebujejo posodobitev v IVMS

3. **Posodobitev IVMS**:
   - Iskanje uporabnikov po e-poštnih naslovih
   - Posodobitev datumov veljavnosti v IVMS
   - Beleženje vseh sprememb v lokalno bazo za revizijsko sled

### Uporabljene tehnologije

- **Python 3.7+**: Robusten in razširljiv programski jezik
- **Requests**: Za komunikacijo z API-ji
- **SQLite/PostgreSQL**: Za shranjevanje stanja in zgodovine sinhronizacij
- **Sistemski demoni**: Za zagotavljanje nenehnega delovanja storitve
- **Docker/kontejnerji**: Za enostavno namestitev in vzdrževanje

## Časovni načrt izvedbe

### Faza 1: Analiza in priprava (1 teden)
- Podrobna analiza API-jev obeh sistemov
- Priprava razvojnega okolja
- Dokončna določitev tehničnih zahtev

### Faza 2: Razvoj osnovne rešitve (2 tedna)
- Implementacija povezav s Cardskipper API
- Implementacija povezav z IVMS API
- Razvoj osnovne logike za sinhronizacijo

### Faza 3: Testiranje in izboljšave (1 teden)
- Testiranje v testnem okolju
- Optimizacija delovanja
- Implementacija naprednega beleženja napak

### Faza 4: Postavitev in predaja (1 teden)
- Namestitev v produkcijsko okolje
- Dokumentacija rešitve
- Usposabljanje osebja za nadzor

**Skupno trajanje projekta**: 5 tednov

## Cenovna ponudba

### Razvoj rešitve

| Postavka | Ure | Cena na uro (EUR) | Skupaj (EUR) |
|----------|-----|-------------------|--------------|
| Analiza in načrtovanje | 20 | 70 | 1.400 |
| Razvoj osnovne rešitve | 60 | 70 | 4.200 |
| Testiranje in izboljšave | 30 | 70 | 2.100 |
| Dokumentacija in usposabljanje | 10 | 70 | 700 |
| **Skupaj za razvoj** | **120** | | **8.400** |

### Mesečno vzdrževanje (opcijsko)

| Storitev | Mesečna cena (EUR) |
|----------|-------------------|
| Osnovno vzdrževanje in nadzor | 200 |
| Razširjeno vzdrževanje z odzivom v 24 urah | 350 |
| Premium vzdrževanje z odzivom v 4 urah | 500 |

### Skupna investicija

- **Začetna investicija**: 8.400 EUR (razvoj rešitve)
- **Mesečni stroški**: od 0 do 500 EUR (odvisno od izbrane ravni vzdrževanja)

*Opomba: Cene so brez DDV. Ponudba velja 30 dni.*

## Možnosti namestitve

Ponujamo tri možnosti namestitve, prilagojene vašim potrebam:

### 1. Namestitev na vaš strežnik

- Namestitev na obstoječo strežniško infrastrukturo
- Manjši mesečni stroški vzdrževanja
- Potrebna je primerna strežniška konfiguracija
- Zagotoviti morate varnost in dostopnost strežnika

**Zahteve**:
- Linux strežnik (priporočeno Ubuntu 20.04 LTS ali novejši)
- Minimalno 2 GB RAM, 20 GB prostora na disku
- Stabilna internetna povezava
- Dostop do obeh API-jev

### 2. Namestitev kot oblačna storitev

- Gostovanje na zanesljivi oblačni platformi (AWS, Azure, DigitalOcean)
- Visoka razpoložljivost in zanesljivost
- Samodejno varnostno kopiranje podatkov
- Enostavno skaliranje po potrebi

**Prednosti**:
- Ni potrebe po lastni strežniški infrastrukturi
- Plačilo po porabi
- Avtomatizirane varnostne kopije
- Večja zanesljivost delovanja

**Ocenjeni mesečni stroški**: 30-50 EUR (odvisno od izbrane platforme in konfiguracije)

### 3. Namestitev v Docker kontejnerju

- Enostavna namestitev v kateremkoli okolju, ki podpira Docker
- Prenosljivost med različnimi sistemi
- Konsistentno delovanje v različnih okoljih
- Poenostavljeno posodabljanje

**Prednosti**:
- Hitrejša namestitev
- Lažje vzdrževanje
- Enostavno posodabljanje
- Izolacija od drugih sistemov

## Demonstracija rešitve

Za boljšo predstavo o delovanju integracije smo pripravili interaktivno demonstracijo, ki prikazuje:

1. Kako poteka sinhronizacija med sistemoma
2. Primer podaljšanja članstva v Cardskipperju
3. Samodejno posodobitev v IVMS sistemu
4. Pregled zgodovine sinhronizacij in statistike

Demonstracijo lahko predstavimo v živo ali vam posredujemo dostop do testnega okolja.

## Naslednji koraki

Predlagamo naslednje korake za začetek projekta:

1. **Začetni sestanek**: Razjasnitev morebitnih vprašanj in podrobna analiza zahtev
2. **Podpis pogodbe**: Formalizacija dogovora o sodelovanju
3. **Začetek razvoja**: Pričetek faze 1 - Analiza in priprava
4. **Redni pregledi napredka**: Tedenski sestanki za pregled napredka in prilagoditve

Za organizacijo začetnega sestanka ali dodatne informacije smo vam na voljo na [kontaktni e-naslov] ali [telefonska številka].

---

## Zaključek

Predstavljena rešitev bo pomembno izboljšala učinkovitost administracije vašega fitnes centra, prihranila čas osebju in izboljšala uporabniško izkušnjo vaših članov. Z avtomatizacijo procesa posodabljanja datumov veljavnosti boste odpravili možnost napak in zagotovili, da bodo člani takoj po podaljšanju članstva imeli dostop do vaših prostorov.

Verjamemo, da naša rešitev predstavlja odlično razmerje med ceno in kakovostjo, z jasno določenim obsegom dela in časovnim okvirom. Veselimo se potencialnega sodelovanja z vami.

S spoštovanjem,

[Ime podjetja/izvajalca]
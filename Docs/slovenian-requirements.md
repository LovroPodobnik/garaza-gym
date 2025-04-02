# Zahteve za integracijo Cardskipper in IVMS

## Namen projekta

Cilj projekta je ustvariti avtomatsko integracijo med sistemom Cardskipper za upravljanje članstva in sistemom IVMS za nadzor dostopa. Ta integracija bo omogočila samodejno sinhronizacijo datumov veljavnosti članstva med obema sistemoma.

## Glavni cilji

1. **Avtomatska sinhronizacija datumov veljavnosti**: Ko član podaljša svoje članstvo v sistemu Cardskipper, se mora datum veljavnosti samodejno posodobiti tudi v sistemu IVMS.

2. **Posodobitev v realnem času**: Spremembe članstva v Cardskipperju se morajo čim hitreje odraziti v IVMS sistemu.

3. **Uporaba e-poštnih naslovov za identifikacijo**: Člane je treba iskati in povezovati med sistemi na podlagi e-poštnih naslovov, saj so ti enaki v obeh sistemih in ne vsebujejo šumnikov.

## Pričakovan potek delovanja

1. Uporabnik v Cardskipperju podaljša svoje članstvo (na primer: nova veljavnost se spremeni iz 1.10.2025 na 1.11.2025).

2. Sistem za integracijo redno preverja in zazna to spremembo v Cardskipperju.

3. Sistem poišče ustreznega uporabnika v IVMS na podlagi e-poštnega naslova.

4. Sistem posodobi datum veljavnosti v IVMS za tega uporabnika.

5. Dostop uporabnika v IVMS sistemu se samodejno podaljša do novega datuma.

## Tehnične zahteve

1. **Povezava s Cardskipper API-jem**: Uporaba obstoječega API-ja za pridobivanje podatkov o aktivnih članih in njihovih datumih veljavnosti.

2. **Povezava z IVMS API-jem**: Uporaba ISAPI vmesnika za posodobitev datumov veljavnosti uporabnikov.

3. **Sinhronizacijski mehanizem**: Implementacija rednega preverjanja za odkrivanje sprememb in njihovo sinhronizacijo.

4. **Lokalna podatkovna baza**: Shranjevanje zgodovine sinhronizacij za revizijo in odpravljanje težav.

5. **Robustno obravnavanje napak**: Implementacija ponovnih poskusov in obveščanja v primeru napak.

## Prednosti rešitve

1. **Avtomatizacija administrativnih nalog**: Ni več potrebe po ročnem posodabljanju članstev v dveh sistemih.

2. **Zmanjšanje možnosti napak**: Odprava neskladij med sistemi, ki bi lahko nastala zaradi ročnega vnosa.

3. **Izboljšana uporabniška izkušnja**: Člani takoj pridobijo dostop po podaljšanju članstva brez dodatnih korakov.

4. **Časovni prihranek**: Zmanjšanje administrativnega dela za osebje.

## Trenutno stanje

V telovadnici se trenutno uporabljata oba sistema, vendar nista povezana. Podatke je treba ročno posodabljati v obeh sistemih, kar je časovno potratno in dovzetno za napake. Podobna integracija že deluje med sistemom Cardskipper in sistemom Ringo door za odpiranje zapornic in vhodnih vrat.

## Pomembne opombe

1. IVMS ima težave s šumniki v imenih, zato je uporaba e-poštnih naslovov za uskladitev uporabnikov najbolj zanesljiva rešitev.

2. IVMS podpira povezavo s tretjimi sistemi preko svojega API-ja, kot je dokumentirano na naslovu: `https://enpinfo.hikvision.com/unzip/20201102205526_84041_doc/GUID-E3DAC3B1-3DF5-467B-AC16-2B8F4DE794F0.html`

Integracija Cardskipper v IVMS

IDEJA: vsem aktivnim uporabnikom v platformi cardskipper se avtomatsko
prenašajo in spreminjajo datumi veljavnosti po tem, ko pride do spremembe.
Seznam aktivnih uporabnikov v Cardskipperju je čisto enostavna tabela, ki izgleda
takole:

Primer: uporabnik v Cardskiperju podaljša karto. Nova veljavnost se spremeni iz
1.10.2025 na 1.11.2025. Podatki se avtomatsko prenesejo v IVMS in se tudi tam
podaljša veljavnost.
Cardskipper:

Ivms:

O Cardskipperju si lahko pogledaš tukaj in tudi zaprosiš za demo verzijo. Če je
potrebno se lahko pomoje jaz zmenim, da mi dajo en testni račun:
https://www.cardskipper.com/
Vse kar vem je to da imajo open API, ne vem pa kako dostopaš do njega. Če ti
morajo oni kaj odobriti mi javi in se lahko dogovorim z njimi. Vem pa, da ta zadeva
deluje, ker imamo čisto po enaki logiki povezan Cardskiper in Ringo door za
odpiranje zapornice in vhodnih vrat. Se pravi, ko pride do spremembe veljavnosti v
cardskipperju se avtomatsko podaljša Ringo ključ. In, kot vem se tudi oni vežejo na
seznam aktivnih članov v cardskipperju.
Imam pa jaz v IVMS programu možnost tudi, da se k uporabniku doda njegov email.
Ker mislim, da bi bilo to najbolje za povezavo obeh, ker so mejli vedno isti v obeh
“aplikacijah”. Ker če se vežemo na imena, je problem že v tem, da IVMS ne podpira
šumnikov in je že tukaj problem.
IVMS si lahko preneseš tukaj:
https://www.hikvision.com/cis/support/download/software/ivms4200-series/
Spodaj pod “Multilingual language package” imaš tudi slovenski jezik
Ima pa IVMS možnost povezave z “Third-Party Database” samo pojma nimam kako
to deluje. Je pa kar nekaj tega ne netu:
https://enpinfo.hikvision.com/unzip/20201102205526_84041_doc/GUID-E3DA
C3B1-3DF5-467B-AC16-2B8F4DE794F0.html
https://www.youtube.com/watch?v=rP6mT4-8YgA

Tole je pa do sedaj ugotovil en programer, ki je potem obupal:
Ej a je varjanta, da probas, ce bi tole slo (mas tut v screenshotih spodaj):
1. Pejt na https://postman.com, nared acc pa dej tm "New request"
2. V url dej http://<device_ip>:<port>/ISAPI/AccessControl/UserInfo/modify
(device_ip in port (ce mas) dej tistega od tvoje face-AI naprave za zaznavanje
folka, kamor se IVMS-4200 povezuje)
3. Request type das na PUT (levo od urlja)
4. Dodaj headerja za Content-Type pa Authorization (ta je sestavljen iz base64
stringa za username:password tvojega admin accounta za IVMS-4200) (poglej
screenshot)
1. Base64 string sestavi na https://it-tools.tech/base64-string-converter , ne
rabis obkljukat safe, nakonc mora bit =
5. Dodaj body in nastavi na raw in XML
V body dodaj tale XML:
<UserInfo>
<employeeNo>12345</employeeNo>
<Valid>
<beginTime>2024-01-01T00:00:00</beginTime>
<endTime>2024-12-31T23:59:59</endTime>
</Valid>
</UserInfo>
Js bi reku, da je employeeNo enak userId tvojih userjev v IVMS-4200. Mogoce
mal probavej.
beginTime in endTime pa je tist kar ti hocs poupdate-at, ko user podaljsa svoj
subscription.
6. Nared request pa poglej kaj nazaj dobis.
7. Ce sem prav razumu, se te stvari poupdatajo na sami AI napravi. Da vidis
spremembe v IVMS-4200, bos mogu update-at znotraj dashboarda (v kolikor tega
ne naredi sam):
1. Mislm, da force refreshas to tkole:
IVMS-4200 Control Panel → Device Management → Refresh the device
data.
2. Ce na IVMS-4200 ne vidis tega, dej nared se tale request

Dej najprej tole probi s kaksnim testnim userjem. Ce bo slo prek tega API klica, se potem
sam poveze tisto subscription-bazo s tem API klicom;
ko user podaljsa subscription, se naredi API klic na AI napravo, kjer popravi beginTime in
endTime za tega userja.

Ce hocs najdt idje od userjev, lahko naredis tole prej:
1. V url dej http://<device_id>:<port>/ISAPI/AccessControl/UserInfo/search
2. V header spet dodas ContentType pa Authorization
3. Request type das na POST
4. Body nastavis na raw in XML
5. V body das tale XML:
<UserInfoSearch>
<searchID>1</searchID>
<searchResultPosition>0</searchResultPosition>
<maxResults>100</maxResults>
</UserInfoSearch>
6. Nared request
7. Ce ni errorja, bos dobil listo userjev in njihovih id-jev. Id pol uporabis v zgornjem
modify requestu
Ko naredis modify request, mogoce loh se enkrat tale search naredis, da vidis, ce ti je
uspesno userja modifyjalo.
Sm si pa s free ChatGPT pomagu, tko, da loh tut njega vprasas kaj.
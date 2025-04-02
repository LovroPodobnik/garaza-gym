# Prijateljska ponudba za povezavo Cardskipper in IVMS sistema

Hej!

Po najinem pogovoru sem pripravil prijateljsko ponudbo za tvojo telovadnico. Vem, da je manjši fitnes in da je treba paziti na stroške, zato sem pripravil precej bolj dostopno rešitev.

## Zakaj potrebuješ to rešitev - razloženo preprosto

Trenutno se soočaš s tem problemom:
1. Član podaljša članstvo v Cardskipper sistemu.
2. Ti moraš ročno iti v IVMS program in tam spremeniti datum veljavnosti.
3. Če pozabiš to narediti, član ne more vstopiti v telovadnico, čeprav je plačal članarino.
4. To te stane čas in povzroča slabo voljo pri članih.

Naša rešitev to popolnoma avtomatizira:
1. Član podaljša članstvo v Cardskipper sistemu.
2. Naš program to samodejno zazna.
3. Program najde istega člana v IVMS sistemu (preko e-maila).
4. Avtomatsko podaljša dostop v IVMS.
5. Član lahko takoj vstopi v telovadnico brez tvoje intervencije.

**Preprosta primerjava:**

**Brez naše rešitve:**  
Član podaljša -> ✋ Ti ročno prenašaš podatke -> 🕒 Zamuda -> 😠 Član ne more vstopiti -> Kliče tebe -> Ti rešuješ problem

**Z našo rešitvijo:**  
Član podaljša -> 🤖 Avtomatska posodobitev -> 😊 Član takoj lahko vstopi -> Ti imaš več časa za druge stvari

## Kaj bomo naredili

Naredil bom povezavo med tvojim Cardskipper sistemom za članstvo in IVMS sistemom za dostop do telovadnice. Ko nekdo podaljša članstvo v Cardskipperju, se bo avtomatsko podaljšal tudi dostop v IVMS sistemu - brez ročnega dela, brez napak, vse deluje samodejno.

## Kako bo to delovalo

Na kratko:
1. Python skripta bo redno preverjala člane v Cardskipperju
2. Ko se datum veljavnosti spremeni, bo skripta to zaznala
3. Skripta bo našla isti e-mail v IVMS sistemu
4. Avtomatsko bo posodobila datum veljavnosti v IVMS
5. Vse spremembe se bodo beležile v bazo za primer, da bi bilo treba kaj preveriti

## Prednosti za tvojo telovadnico

- **Prihranek časa**: Ne bo več ročnega vnašanja podatkov v dva sistema
- **Brez napak**: Ni možnosti, da bi pozabil posodobiti dostop v IVMS
- **Boljša izkušnja za člane**: Ko nekdo podaljša članstvo, takoj dobi dostop
- **Preprosto za vzdrževanje**: Enkrat nastavimo, potem deluje samo od sebe
- **Manj klicev članov**: Ne bo več pritožb, da nekdo ne more vstopiti, ker si pozabil posodobiti dostop
- **Profesionalen vtis**: Tvoja telovadnica bo delovala bolj organizirano in profesionalno

## Cena

Ker gre za manjšo telovadnico in ker sva prijatelja, sem pripravil posebno ceno:

| Kaj | Opis | Cena |
|-----|------|------|
| **Razvoj in namestitev** | Osnovna verzija z vsemi potrebnimi funkcijami | **1.500 €** |
| Vzdrževanje (opcijsko) | Mesečni pregled, da vse deluje, popravki če je potrebno | **50 €/mesec** |

*Opomba: Cene so brez DDV.*

## Časovnica

Celoten projekt lahko zaključim v **3 tednih**:
- 1. teden: Priprava in razvoj osnovne rešitve
- 2. teden: Testiranje in dodelava
- 3. teden: Namestitev in preizkus v živo

## Kako bi to namestili

Imam tri ideje, izbereva tisto, ki ti najbolj ustreza:

### 1️⃣ Na tvojem obstoječem računalniku

Če imaš računalnik, ki je vedno prižgan (npr. računalnik na recepciji), lahko namestimo tam. To je najcenejša opcija in ne zahteva dodatne strojne opreme.

**Prednosti**: Ni dodatnih stroškov, enostavno za vzdrževanje.

### 2️⃣ Na majhnem, namenskem računalniku

Lahko kupimo mali računalnik (npr. Raspberry Pi za približno 100€), ki bo namenjen samo tej nalogi.

**Prednosti**: Zanesljivo delovanje, nizka poraba energije, ne moti drugih programov.

### 3️⃣ Kot spletno storitev

Lahko postavimo v oblak (npr. DigitalOcean).

**Prednosti**: Deluje tudi, če v telovadnici zmanjka elektrike ali interneta.
**Slabosti**: Mesečni strošek okoli 5-10€ za gostovanje.

## Kaj vse je vključeno

Za to ceno dobiš:
- Celoten razvoj rešitve
- Namestitev sistema
- Začetno testiranje
- Osnovna dokumentacija
- Predstavitev delovanja osebju
- 1 mesec brezplačne podpore po namestitvi

## Demonstracija

Preden se odločiš, ti lahko pokažem demo aplikacijo, ki sem jo pripravil. Demo prikazuje, kako bo izgledala celotna rešitev in kako bo delovala v praksi. Pokliči me in ti vse pokažem v živo ali preko video klica.

## Pogosta vprašanja

**V: Ali bo to vplivalo na delovanje Cardskipperja ali IVMS sistema?**  
O: Ne, naša rešitev samo bere podatke iz Cardskipperja in posodablja podatke v IVMS. Ne spreminja osnovnega delovanja teh sistemov.

**V: Kaj če IVMS ne najde ujemajočega e-maila?**  
O: Program bo to zabeležil in te obvestil, da je potrebno ročno ujemanje za tega člana.

**V: Kaj če nimam vedno vklopljenega računalnika?**  
O: V tem primeru bi bila najboljša rešitev namestitev v oblaku ali na majhnem namenskem računalniku.

**V: Koliko časa prihranim s to rešitvijo?**  
O: Če imaš 200 članov in vsak podaljša članstvo enkrat letno, to pomeni približno 200 ročnih posodobitev. Če za vsako porabiš 2 minuti, je to 400 minut oziroma skoraj 7 ur na leto, ki jih lahko porabiš za druge stvari.

## Kako naprej?

Če ti je ponudba všeč, mi sporoči in se dogovoriva za začetek. Potreboval bom:
1. Dostop do Cardskipper administratorskega računa
2. Dostop do IVMS sistema
3. 50% plačila na začetku, 50% po zaključku

V primeru vprašanj me lahko kadarkoli pokličeš ali mi pišeš!

Lep pozdrav,
[Tvoje ime]
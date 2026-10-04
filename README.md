# pico-clock-lab

Laboratórium na učenie sa hardvéru **Waveshare Pico-Clock-Green** s Raspberry Pi Pico (W).
Žiadne WiFi, MQTT ani hodiny, len ovládanie LED displeja a ďalšej periférie, plus malé testy.

## Hardvér v skratke

| Signál | GPIO | Čo robí |
|---|---|---|
| SDI | 11 | sériové dáta do posuvného registra |
| CLK | 10 | hodiny posunu, dáta sa preberú na **nábežnej hrane** |
| LE | 12 | latch: posuvný register → výstupy (impulz 1 → 0) |
| OE | 13 | zapnutie výstupov, **aktívne v 0** (0 = svieti, 1 = zhasnuté) |
| A0 / A1 / A2 | 16 / 18 / 22 | binárne číslo riadka 0 až 7 (dekodér SM5166P) |
| fotosenzor | 26 (ADC) | vyššia hodnota = tmavšie |
| buzzer | 14 | aktívny, 1 = pípa |
| tlačidlá 1 / 2 / 3 | 2 / 17 / 15 | stlačené = 0 (pull-up) |

Piny sú z pôvodného firmvéru (`pins.py`). Schému si pozri na stránke Waveshare.

### Ako displej funguje

```
              ┌──────────────┐   32 výstupov (24 na LED)
 SDI,CLK,LE ─►│ 2× SM16106   ├───────────────┐
              │ posuvný reg. │               ▼
              │  + latch     │        ┌────────────────┐
 OE ─────────►│              │        │  matica 8 × 24 │
              └──────────────┘        │      LED       │
 A0,A1,A2 ──► SM5166P (dekodér 3→8) ─►│  1 riadok z 8  │
                                      └────────────────┘
```

- **Riadky:** naraz svieti iba jeden z 8 riadkov, vyberie ho dekodér podľa `A0..A2`.
- **Stĺpce:** matica má **24 stĺpcov**, ale dva čipy SM16106 tvoria **32-bitový** posuvný register
  (2 × 16 výstupov), takže sa vždy posúva 32 bitov a 8 výstupov pravdepodobne nie je na LED zapojených
  (ktoré, to ukáže `t02_pixel_walk.py`). Do registra sa posunie obsah riadka. Čip má **latch**, takže
  výstupy držia hodnotu, aj keď sa do registra posúvajú nové bity. Pamäť je ale len na jeden riadok.
- **Multiplexovanie:** 8 riadkov sa strieda tak rýchlo, že oko vidí celý obraz. LED samotné
  pamäť nemajú, svietia len, kým cez ne tečie prúd.
- **Jas** je doba, počas ktorej riadok svieti (`on_us`). Priemerný jas je najviac 1/8 špičkového.
- Riadok 0 je pásik dní v týždni, stĺpce 0 a 1 sú ikony (AM, PM, °C...), text je v riadkoch 1 až 7.

### Dve metódy skenovania (`display.py`)

1. **simple** (pôvodný firmvér): počas tmy posun 32 bitov, latch, adresa, potom sa svieti a čaká.
   Posun je mŕtvy čas, v ktorom nič nesvieti.
2. **pipelined** (hypotéza na otestovanie): kým riadok N svieti, do posuvného registra sa posúva
   riadok N+1. Latch drží výstupy. Posun sa tým prekryje so svietením, čo má dať vyššiu
   obnovovaciu frekvenciu a vyšší jas. Predpokladá, že posuvný register a latch v SM16106 sú nezávislé.
   Test **t04** ukáže, či to funguje: ak je obraz v pipelined režime rozbitý, čip sa tak nesprávi.

## Nahratie na Pico

Všetky `*.py` zo zložky nahraj do koreňa Pico (Thonny: View → Files → pravým *Upload to /*).
Testy spúšťaj otvorením súboru v Thonny a **F5**. Pred nahratím si zálohuj pôvodný program z Pico.

> Obnova displeja beží vo vlákne na druhom jadre. Ak sa Pico po Stop zasekne, stlač Stop
> ešte raz alebo ho odpoj a zapoj.

## Testy

| Súbor | Čo robí | Čo sa naučíš |
|---|---|---|
| `t01_static_pixel.py` | zasvieti jednu LED (`ROW`, `COL`), bez skenovania | riadok + stĺpec + OE sú všetko, čo treba |
| `t02_pixel_walk.py` | jedna LED prejde všetkých 8 × 32 pozícií posuvu | ktorých 24 z 32 pozícií svieti na displeji a smer (vľavo/vpravo) |
| `t03_row_walk.py` | po riadkoch svieti celý riadok | obraz sa skladá po riadkoch |
| `t04_patterns.py` | všetko, šachovnica, rám, uhlopriečka, pruhy | mŕtve LED, zrkadlenie, duchovia (ghosting) |
| `t05_brightness.py` | mení `on_us` | ako sa mení jas a kedy začne blikať |
| `t06_refresh_rate.py` | meria čas posunu a obnovovaciu frekvenciu | mŕtvy čas, čo prináša pipelined, vplyv taktu CPU |
| `t07_scroll_text.py` | posúvaný text (4×7 font) | kreslenie do `frame` a skenovanie |
| `t08_inputs.py` | tlačidlá, fotosenzor, teplota čipu, buzzer | ostatný hardvér a kalibračné hodnoty jasu |

## Pokusy

- Prepni `PIPELINED` v t03, t04, t05 a t07 a porovnaj obraz.
- V t06 skús `CPU_MHZ` 125, 200, 250.
- V t02 zapíš, ktoré `col` sa nezobrazia a kde je `col 0`.
- Zmeň poradie krokov v `scan_frame_simple` (napr. nastav adresu až po `show()`) a pozri sa na duchov.
- Zmeň rýchlosť `clk` pridaním oneskorení a zisti, kedy sa dáta posúvajú nesprávne.

## Čo overuje a čo neoverilo (stav)

Logika skenovania (oba režimy) je overená simuláciou čipu na PC. Na samotnom hardvéri
sa kód ešte nespúšťal. Priraďovanie stĺpcov a správanie pipelined režimu ukážu testy t02 a t04.

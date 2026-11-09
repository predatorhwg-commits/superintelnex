# Fragenliste: Festlegungen für den SuperIntelNex-Token

**Status: Alle Werte sind Vorschläge, nicht Endentscheid.** Sie stehen in
`token/config/token.json` unter `"_status": "NOT-FINAL"` und dürfen erst nach
Ihrer Bestätigung als beschlossen gelten. Der Devnet-Lauf hängt bewusst an
dieser Bestätigung (Details: `DEVNET-RUNBOOK.md`).

Jede Frage braucht Ihre Entscheidung, bevor der Token auf Devnet erstellt
wird — ein Mint-Anlauf ist unwiderruflich und die On-Chain-Metadaten sind
mit `isMutable: false` dauerhaft fixiert.

## Q1 — Token-Kürzel (Symbol)

| | |
|---|---|
| **Vorschlag** | `SIN` |
| **Begründung** | Kurz, aus dem Namen (Sup**I**ntel**N**ex) abgeleitet, 3 Zeichen — gut lesbar in Wallets und im Explorer. Muss A-Z/0-9 sein, 2–10 Zeichen (Regel im Konfig-Test). |
| **Alternativen** | `SNX`, `SINEX`, `SI` |
| **Ihre Entscheidung** | ☐ bestätigt / ☐ geändert zu: ______ |

## Q2 — Gesamtmenge (Total Supply)

| | |
|---|---|
| **Vorschlag** | **1.000.000.000** (eine Milliarde) |
| **Begründung** | Runde, leicht kommunizierbare Zahl; übliche Größenordnung für Community-Tokens. Passt zur Community-Ausrichtung, impliziert aber keine Kursaussage. |
| **Alternativen** | 100.000.000 · 500.000.000 · 1.000.000.000 · 10.000.000.000 |
| **Ihre Entscheidung** | ☐ bestätigt / ☐ geändert zu: ______ |

## Q3 — Nachkommastellen (Decimals)

| | |
|---|---|
| **Vorschlag** | **9** |
| **Begründung** | SPL-Standard (wie SOL); erlaubt feine Beträge bei großer Gesamtmenge. Höher als nötig wäre verschwendeter Platz, weniger als 9 bedeutet weniger Feinheit. |
| **Alternativen** | 6 · 8 · 9 |
| **Ihre Entscheidung** | ☐ bestätigt / ☐ geändert zu: ______ |

## Q4 — Ausgabe-Policy (fest vs. weitere Emissionen)

| | |
|---|---|
| **Vorschlag** | **Feste Menge, keine weiteren Emissionen** (`FIXED-NO-FURTHER-ISSUANCE`) |
| **Begründung** | Höchste Integrität für die Community; zusammen mit dem Entzug der Mint-Vollmacht (Q6) wird die Supply endgültig fixiert. Eine spätere zusätzliche Ausgabe würde das Vertrauen brechen und ist nach Entzug technisch unmöglich. |
| **Alternativen** | Festes Maximum mit kontrollierter Reserve (Mint-Vollmacht behalten) · Zeitfenster für zusätzliche Emission |
| **Ihre Entscheidung** | ☐ bestätigt / ☐ geändert zu: ______ |

## Q5 — Verteilung (Community / Gründer / Entwicklung / Liquidität)

| | |
|---|---|
| **Vorschlag** | **55 % Community · 20 % Gründer · 15 % Entwicklung · 10 % Liquidität** |
| **Begründung** | Community-Fokus passt zur Ausrichtung; die Gründer- und Entwicklungsteile sind moderat gehalten (keine „Dev-Wallet" > 50 %). Liquiditätsanteil ist für den späteren (nicht jetzt!) Handel reserviert. **Hinweis:** Die On-Chain-Distribution (4 getrennte Emissionskonten) ist im Skript erst GEPLANT und erscheint erst nach Bestätigung — aktuell mintet `mint-initial.ts` die Gesamtmenge an eine einweg-Test-Wallet (Reihenfolge: Emission → Verteilung). |
| **Alternativen** | 70/20/5/5 · 50/25/15/10 · eigene Gewichtung |
| **Ihre Entscheidung** | ☐ bestätigt / ☐ geändert zu: ______ |
| **Zusatz** | Sperrfristen (Vesting) für Gründer/Entwicklung? ☐ ja (Dauer: ______) ☐ nein |

## Q6 — Verwaltungsrechte (Mint-/Freeze-Vollmacht)

| | |
|---|---|
| **Vorschlag** | **Beide Vollmachten nach Emission unwiderruflich entziehen** (`revokeMintAuthority: true`, `revokeFreezeAuthority: true`) |
| **Begründung** | Siehe unten, „Mint & Freeze im Detail". Maximale Transparenz: im Explorer sichtbar `mintAuthority = (none)`, `freezeAuthority = (none)`. Kein verstecktes Recht zum Einziehen fremder Token (SPL hat ohnehin keine Blacklist-Logik; Freeze wäre die einzige Sperrmöglichkeit). |
| **Alternativen** | (a) beide behalten (Rekorrektur möglich, aber Vertrauen kostet) · (b) nur Freeze entziehen, Mint behalten (Reserve-Issuance) · (c) nur Mint entziehen, Freeze behalten (Kontensperrung möglich) |
| **Ihre Entscheidung** | ☐ bestätigt (beide weg) / ☐ (a) / ☐ (b) / ☐ (c) |

### Mint & Freeze im Detail (Begründung für Q6)

- **Mint-Vollmacht (erzeugt Token):** Wer sie hat, kann neue Token „aus dem
  Nichts" schaffen und die Gesamtmenge erhöhen. **Entzug** → Supply endgültig
  fix, niemand (auch nicht Sie) kann mehr minten. **Beibehaltung** → flexible
  Reserve, aber dauerhaftes Vertrauensrisiko: die Vollmacht ist im Wallet-Schlüssel
  gebunden; verlorener Schlüssel = blockierte Reserve, kompromittierter Schlüssel
  = unbegrenzte Emission.
- **Freeze-Vollmacht (sperrt/entsperrt Konten):** Wer sie hat, kann den
  Token-Account eines Halters `freeze`n (kein Transfer mehr möglich) bzw. `thaw`.
  Im Standard-SPL ist das die **einzige** Sperrmöglichkeit — es gibt **keine
  Blacklist**, **keine versteckten Gebühren**, **keine Verkaufsbeschränkung** im
  Programm. **Entzug** → kein Konto mehr sperrbar (höchste Freiheit für Halter).
  **Beibehaltung** → Sie können versehentlich eingefrorene Konten auftauen und
  missbräuchliche Konten sperren; dafür bleibt eine permanente, einseitige Macht
  über fremde Wallets bestehen.
- **On-Chain-Metadaten (`isMutable: false`):** Name, Symbol, URI und Creators
  sind zum Anlegezeitpunkt **dauerhaft fixiert** — das Programm lehnt danach
  jede `Update`-Instruktion ab (Details: `METADATEN-SPEICHERUNG.md`). Eine
  Korrektur von Tippfehlern in der Metadaten ist **nicht** möglich; deshalb
  muss Q1/Q2 und die off-Chain-URI vor dem `create-mint.ts`-Aufruf final sein.

## Q7 — Off-Chain-Metadaten-Speicher (URI)

| | |
|---|---|
| **Aktueller Stand** | GitHub Pages (`superintelnex.com/token/metadata/superintelnex-token.json`), **provisorisch** für den Testtoken |
| **Begründung** | Laufend und nachvollziehbar; aber ein Repo-Besitzer kann GitHub Pages jederzeit deaktivieren, was die URI-Datei unerreichbar macht. |
| **Vorschlag für den Launch** | Content-addressed Speicher (IPFS z. B. Pinata/Web3Storage, oder Arweave), damit die URI auf einen Hash zeigt und nicht auf eine manipulierbare Datei-URL |
| **Ihre Entscheidung** | ☐ GitHub Pages bleibt für Devnet reichen / ☐ IPFS-Upload / ☐ Arweave (AO-Format) / ☐ andere: ______ |

## Q8 — Devnet-Erstellung (jetzt ausführen?)

| | |
|---|---|
| **Status** | Code, Konfiguration, Tests (offline + localnet) und Doku stehen. Der **tatsächliche Devnet-Mint** fehlt noch. |
| **Blocker** | Die einweg-Admin-Test-Wallet (`token/wallets/main.json`,
  `EuH4ub45jSCusT54Nw7V359t9xZ1GcTQSeKbAtd4LK44`) braucht **~0,5 Test-SOL**.
  Der öffentliche Devnet-Airdrop war zuletzt **abgeschaltet** (HTTP 410);
  die Web-Faucets erfordern CAPTCHA (wird in diesem Projekt nicht umgangen). |
| **Zufuhr-Wege** | (A) Manuell im Browser: `faucet.solana.com` — Pubkey dort
  kopieren (niemals Schlüssel-Prüf-Code in fremde Felder), ~0,5 Test-SOL
  anfordern · (B) RPC-Endpunkt mit aktiviertem Airdrop (z. B. QuickNode-
  Devnet-URL) als `SIN_RPC` übergeben · (C) Test-SOL von einer eigenen
  Devnet-Wallet per `solana transfer` |
| **Ihre Entscheidung** | ☐ Devnet-Lauf jetzt ausführen (nach Q1–Q7) /
  ☐ Q1–Q7 zuerst festlegen, Devnet-Lauf dann ausführen / ☐ Devnet-Lauf
  vertagen |

## Q9 — Verwaltung der Metadaten-Update-Vollmacht

| | |
|---|---|
| **Status** | Beim Anlegen ist `updateAuthority = Admin-Test-Wallet`. Mit
  `isMutable: false` ist sie **nicht mehr relevant** (keine Updates möglich);
  das Skript kann sie jedoch per `SetAuthority` entziehen (ein einweg-Schritt,
  der kein zusätzlicher Transaktions-Slot braucht). |
| **Ihre Entscheidung** | ☐ Update-Vollmacht nach Devnet-Lauf ebenfalls
  entziehen (empfohlen für maximale Transparenz) / ☐ behalten (irrelevant
  wegen `isMutable: false`) |

---

**Keine Seed-Phrase oder private Schlüssel werden in diesem Projekt
abgefragt. Alle Test-Wallets sind einweg-Test-Artefakte (`token/wallets/`,
gitignoriert), niemals das Tresor-Wallet. Keine Kurs-, Profit- oder
Rechtsaussagen; alle Werte sind Vorschläge bis zur Bestätigung.**

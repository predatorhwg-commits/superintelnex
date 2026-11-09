# Fragenliste: Festlegungen für den SuperIntelNex-Token

**Stand: BESTÄTIGT am 09.11.2026.** Der Betreiber hat die freie Auswahl
übertragen und 100 Billion (10^14) Gesamtmenge vorgegeben. Die Werte
stehen unter `"_status"` in `token/config/token.json` und gelten für den
DEVNET-Testtoken — für Mainnet sind sie erst mit der erneuten
Mainnet-Bestätigung final.

> **Hinweis (technische Bindung):** 100 Billion = 10^14 passt mit den
> üblichen 9 Dezimalstellen (SOL-Standard) **nicht** in die u64-Supply
> der SPL-Programme (10^14 × 10^9 = 10^23 > 1.84·10^19 max). Deshalb:
> **5 Nachkommastellen** — das ist das technische Maximum, bei dem
> 10^14 integer bleibt (1 SIN = 100.000 kleinste Einheiten). Der
> Konfig-Test prüft das automatisch (`config.test.ts`, u64-Guard).

## Q1 — Token-Kürzel (Symbol)

| | |
|---|---|
| **Bestätigt** | `SIN` |
| **Begründung** | Kurz, aus dem Namen (Sup**I**ntel**N**ex) abgeleitet, 3 Zeichen — gut lesbar in Wallets und im Explorer. |

## Q2 — Gesamtmenge (Total Supply)

| | |
|---|---|
| **Bestätigt** | **100.000.000.000.000** (100 Billion = 10^14, deutsche Zählung) |
| **Begründung** | Vom Betreiber vorgegeben (09.11.2026). |

## Q3 — Nachkommastellen (Decimals)

| | |
|---|---|
| **Bestätigt** | **5** |
| **Begründung** | Technisch gebunden an Q2: u64-Supply-Obergrenze erlaubt 10^14 maximal mit 5 Dezimalstellen (Raw-Supply = 10^19, ~54 % der Obergrenze). Mit 9 Dezimalstellen (SOL-Standard) würde 10^14 nicht in den Supply-Wert passen. |

## Q4 — Ausgabe-Policy (fest vs. weitere Emissionen)

| | |
|---|---|
| **Bestätigt** | **Feste Menge, keine weiteren Emissionen** (`FIXED-NO-FURTHER-ISSUANCE`) |
| **Begründung** | Maximale Integrität für die Community; zusammen mit dem Entzug der Mint-Vollmacht (Q6) wird die Supply endgültig fixiert. |

## Q5 — Verteilung (Community / Gründer / Entwicklung / Liquidität)

| | |
|---|---|
| **Bestätigt (Planwert)** | **55 % Community · 20 % Gründer · 15 % Entwicklung · 10 % Liquidität** |
| **Hinweis** | Die On-Chain-Mehrfach-Emission (4 getrennte Emissionskonten) ist GEPLANT und erscheint erst nach Verteilungsbestätigung für den Mainnet-Launch. Aktuell mintet `mint-initial.ts` die Gesamtmenge an die einweg-Admin-ATA — **das ist ein bewusster Prototyp-Entscheid, keine Verkaufs- oder Distributionsumsetzung.** Sperrfristen (Vesting) für Gründer/Entwicklung: offen, siehe Q6-Anhang. |

## Q6 — Verwaltungsrechte (Mint-/Freeze-Vollmacht)

| | |
|---|---|
| **Bestätigt** | **Beide Vollmachten nach Emission unwiderruflich entziehen** (`revokeMintAuthority: true`, `revokeFreezeAuthority: true`) |
| **Begründung** | Maximale Transparenz: im Explorer sichtbar `mintAuthority = (none)`, `freezeAuthority = (none)`. Kein verstecktes Recht zum Einziehen fremder Token (SPL hat ohnehin keine Blacklist-Logik; Freeze wäre die einzige Sperrmöglichkeit). |

### Mint & Freeze im Detail (Begründung für Q6)

- **Mint-Vollmacht (erzeugt Token):** Wer sie hat, kann neue Token „aus dem
  Nichts" schaffen und die Gesamtmenge erhöhen. **Entzug** → Supply endgültig
  fix, niemand kann mehr minten. **Beibehaltung** → flexible Reserve, aber
  dauerhaftes Vertrauensrisiko: kompromittierter Schlüssel = unbegrenzte
  Emission.
- **Freeze-Vollmacht (sperrt/entsperrt Konten):** Wer sie hat, kann den
  Token-Account eines Halters `freeze`n (kein Transfer mehr möglich). Im
  Standard-SPL ist das die **einzige** Sperrmöglichkeit — es gibt **keine
  Blacklist**, **keine versteckten Gebühren**, **keine Verkaufsbeschränkung**
  im Programm. **Entzug** → kein Konto mehr sperrbar (höchste Freiheit für
  Halter). **Beibehaltung** → man kann versehentlich eingefrorene Konten
  auftauen und missbräuchliche Konten sperren; dafür bleibt eine permanente,
  einseitige Macht über fremde Wallets bestehen.
- **On-Chain-Metadaten (`isMutable: false`):** Name, Symbol, URI und Creators
  sind zum Anlegezeitpunkt **dauerhaft fixiert** — das Programm lehnt danach
  jede `Update`-Instruktion ab (Details: `METADATEN-SPEICHERUNG.md`). Eine
  Korrektur von Tippfehlern in der Metadaten ist **nicht** möglich; deshalb
  müssen Q1/Q2 und die off-Chain-URI vor dem `create-mint.ts`-Aufruf final sein.

## Q7 — Off-Chain-Metadaten-Speicher (URI)

| | |
|---|---|
| **Bestätigt (Devnet)** | GitHub Pages (`superintelnex.com/token/metadata/superintelnex-token.json`), **provisorisch** für den Testtoken |
| **Begründung** | Laufend und nachvollziehbar; aber ein Repo-Besitzer kann GitHub Pages jederzeit deaktivieren, was die URI-Datei unerreichbar macht. |
| **Für Mainnet (offen)** | Content-addressed Speicher (IPFS z. B. Pinata/Web3Storage, oder Arweave), damit die URI auf einen Hash zeigt und nicht auf eine manipulierbare Datei-URL |

## Q8 — Devnet-Erstellung (jetzt ausführen?)

| | |
|---|---|
| **Status** | Code, Konfiguration, Tests (offline + localnet) und Doku stehen. Der **tatsächliche Devnet-Mint** fehlt noch. |
| **Blocker** | Die einweg-Admin-Test-Wallet braucht **~0,5 Test-SOL**. Der öffentliche Devnet-Airdrop ist **abgeschaltet** (HTTP 410); die Web-Faucets erfordern CAPTCHA (wird in diesem Projekt nicht umgangen). |
| **Zufuhr-Wege** | (A) Manuell im Browser: `faucet.solana.com` — nur den Pubkey der Test-Wallet eintragen (niemals Schlüssel-Prüf-Code in fremde Felder), ~0,5 Test-SOL anfordern · (B) RPC-Endpunkt mit aktiviertem Airdrop (z. B. QuickNode/Alchemy-Devnet-URL) als `SIN_RPC` übergeben · (C) ~0,1 Test-SOL von einer Ihrer Devnet-Tester-Wallets per `solana transfer` |
| **Ihre Entscheidung** | ☐ Devnet-Lauf jetzt ausführen (nach Q1–Q7) / ☐ Q1–Q7 zuerst festlegen, Devnet-Lauf dann ausführen / ☐ Devnet-Lauf vertagen |

## Q9 — Verwaltung der Metadaten-Update-Vollmacht

| | |
|---|---|
| **Bestätigt** | **Nach dem Devnet-Lauf ebenfalls entziehen** (einweg-Schritt, kein zusätzlicher Transaktions-Slot) |
| **Begründung** | Mit `isMutable: false` ist die Update-Vollmacht bereits nicht mehr relevant (keine Updates möglich); der Entzug macht den Zustand im Explorer sichtbar `updateAuthority = (none)` — maximale Transparenz. |

---

**Keine Seed-Phrase oder private Schlüssel werden in diesem Projekt
abgefragt. Alle Test-Wallets sind einweg-Test-Artefakte (`token/wallets/`,
gitignoriert), niemals das Tresor-Wallet. Keine Kurs-, Profit- oder
Rechtsaussagen; alle Werte sind final für den DEVNET-Testtoken, für
Mainnet erst nach erneuter Bestätigung.**

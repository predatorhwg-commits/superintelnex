# SuperIntelNex (SIN) — Whitepaper

**Version 0.9 (Draft)** · Stand: 09.11.2026 · Projekt: `superintelnex/superintelnex` (GitHub)

> **Wichtige Hinweise vorab**
>
> - SuperIntelNex ist ein **Community-Token-Projekt im Aufbau**. Es besteht **kein Mainnet-Start, kein Verkauf, kein Live-Token mit echtem Geld** — der aktuell existierende Token ist ein **reiner Devnet-Testtoken** ohne wirtschaftlichen Wert.
> - Dieses Dokument ist **keine Anlageberatung, keine Rechtsberatung und keine Empfehlung zum Kauf oder Handel**. Es werden **keine Kurse, Erträge oder Garantien** in Aussicht gestellt.
> - Alle Parameter sind für den **Devnet-Testtoken bestätigt**; sie gelten für den Mainnet-Launch **erst nach erneuter Bestätigung** (siehe [Roadmap](#6-roadmap)).
> - Jede Aussage in diesem Whitepaper ist per Quelle belegt — siehe [Anhang: Quellen](#anhang-quellen-und-nachvollziehbarkeit).

---

## 1. Zusammenfassung

SuperIntelNex (Kürzel: **SIN**) ist ein Community-Token-Projekt mit einer langfristigen Vision für **KI, Superintelligenz und digitale Zahlungen**. Das Projekt wird transparent und nachvollziehbar entwickelt: Alle Token-Parameter, Skripte, Tests und Transaktionsprotokolle liegen öffentlich im GitHub-Repository.

Der aktuelle Stand (09.11.2026):

- Ein **Testtoken SIN auf Solana Devnet** wurde erstellt, vollständig ausgeführt und geprüft — inklusive **unwiderruflichem Entzug aller Verwaltungsvollmachten** (Mint und Freeze). Jede Transaktion ist im öffentlichen Solana-Explorer nachvollziehbar (siehe [Abschnitt 5](#5-devnet-prototyp-nachvollziehbar)).
- Der **Mainnet-Start ist vorbereitet aber nicht erfolgt**. Die dafür offenen Entscheidungen und Schritte sind in der [Roadmap](#6-roadmap) festgehalten.
- Offizielle Kanäle: **X @superintelnex** und **Discord** (Links im Footer der Website `superintelnex.com`).

**Das zentrale Designprinzip:** Standard-SPL-Token mit maximaler Nachvollziehbarkeit — **kein eigenes Smart-Contract-Programm, keine Token-2022-Extensionen, keine versteckten Gebühren, keine Sperr- oder Blacklist-Logik**. Die Kontrolle über die Token-Ausgabe wird nach der Emission unwiderruflich aufgegeben, sodass niemand mehr neue Token erzeugen oder Konten sperren kann.

---

## 2. Die Vision

SuperIntelNex verfolgt eine langfristige Vision entlang dreier Bausteine. Alle Punkte sind **geplante Ziele, keine Zusagen oder umgesetzten Funktionen**:

| Baustein | Ziel (geplant) | Status |
|---|---|---|
| **Übertragungen** | Wallet- zu Wallet-Transfers des Tokens | Technisch im Devnet-Lauf validiert (Checked-Transfer-Test) |
| **Handel** | Später Handelbarkeit auf unterstützten Plattformen | Geplant — **keine Listings zugesagt**, Börsenaufnahmen erfordern separate Anbieter-Prozesse |
| **Bezahlen & KI** | Zahlungen bei teilnehmenden Anbietern; Händlerakzeptanz und KI-Anwendungen als langfristige Ziele | Langfristige Vision, **nicht umgesetzt** |

> Partnerschaften, Audits, Teamangaben und offizielle Social-Media-Links außerhalb des Footers der Website sind **bisher nicht bestätigt**. Dieses Whitepaper hält sich strikt an belegbare Fakten des Projekts.

---

## 3. Technische Architektur

### 3.1 Plattform

Der Token ist ein **Standard-SPL-Token** auf Solana:

| Baustein | Programm-Adresse | Funktion |
|---|---|---|
| SPL Token Program | `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA` | Token-Konten, Transfers, Minting (Standard-SPL) |
| Metaplex Token Metadata v2 | `metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s` | On-Chain-Metadaten (Name, Symbol, URI, Creators) |

**Bewusst nicht vorhanden:**

- Kein eigenes Programm — es wird ausschließlich etablierte, breit eingesetzte Programm-Logik verwendet.
- Keine Token-2022-Extensionen (keine Fees, keine Hooks, keine erweiterte Freeze-Logik).
- Keine Blacklist- und keine Sperr-Logik: Im Standard-SPL ist das Einfrieren von Konten die **einzige** Sperrmöglichkeit — und die dazu notwendige Freeze-Vollmacht wird nach der Emission unwiderruflich entzogen (siehe [Abschnitt 4.3](#43-administration-und-irreversibilität)).
- Keine versteckten Gebühren: `sellerFeeBasisPoints = 0`, Metadaten mit `isMutable = false` (dauerhaft fixiert).

### 3.2 Emissions-Toolchain (Deno)

Die gesamte Token-Erzeugung ist als transparente, getestete Skript-Pipeline im Ordner `token/` des Repositories umgesetzt (Laufzeitumgebung: Deno):

| Schritt | Skript | Zweck |
|---|---|---|
| 1 | `create-mint.ts` | Mint + Associated Token Account + Metaplex-Metadaten in **einer** Transaktion |
| 2 | `mint-initial.ts` | Emission der Gesamtmenge |
| 3 | `transfer-test.ts` | Checked-Transfer-Test (ATA anlegen + 1,234 SIN Transfer) |
| 4 | `verify.ts` | On-Chain-Abgleich: Decimals, Supply, Vollmachten, Metadaten |
| 5 | `revoke-authorities.ts` | Entzug der Mint- und Freeze-Vollmacht (**einweg**) |

Dazu ein **Offline-Test** (`config.test.ts`) mit u64-Supply-Guard (prüft, dass Gesamtmenge × 10^Decimals in die u64-Supply-Obergrenze der SPL-Programme passt) sowie **Integrationstests** gegen einen lokalen Test-Validator (`solana-test-validator` inkl. Devnet-Clone des Metaplex-Programms). Beim Devnet-Lauf am 09.11.2026: **6/6 Tests bestanden**, alle Schritte mit echten Transaktionen an echten RPC-Endpunkte ausgeführt und dokumentiert.

> **Korrekturfähigkeit durch Design:** Vor dem unwiderrufbaren Entzug der Vollmachten prüft `verify.ts` den gesamten On-Chain-Zustand. Erst wenn alle Emissionen und Korrekturen abgeschlossen sind, wird Schritt 5 ausgeführt. Danach ist der Zustand endgültig und öffentlich nachprüfbar.

---

## 4. Token-Design

Bestätigte Parameter aus `token/config/token.json` (09.11.2026, gilt für den Devnet-Testtoken):

### 4.1 Kernparameter

| Parameter | Wert | Anmerkung |
|---|---|---|
| Bezeichnung | SuperIntelNex | On-Chain fixiert (`isMutable: false`) |
| Kürzel | **SIN** | Aus dem Namen abgeleitet (Sup**I**ntel**N**ex), gut lesbar in Wallets |
| Gesamtmenge | **100.000.000.000.000** (100 Billion, 10^14, deutsche Zählung) | Vom Betreiber vorgegeben |
| Nachkommastellen | **5** | Technisch bedingt (siehe unten) |
| Ausgabe-Policy | **feste Menge, keine weiteren Emissionen** (`FIXED-NO-FURTHER-ISSUANCE`) | Maximale Integrität |
| On-Chain-Metadaten | `isMutable: false`, `sellerFeeBasisPoints: 0` | Name/Symbol/URI dauerhaft fixiert |

**Warum 5 Nachkommastellen?** Die SPL-Programme begrenzen die Supply technisch auf u64 (≈ 1,84 × 10^19 kleinste Einheiten). 10^14 Token × 10^5 = 10^19 passt — die üblichen 9 Dezimalstellen des SOL-Standards (10^14 × 10^9 = 10^23) würden die Grenze überschreiten. 5 Dezimalstellen sind das technische Maximum bei vorgegebener Gesamtmenge: 1 SIN = 100.000 kleinste Einheiten. Der Konfig-Test prft das automatisch (u64-Supply-Guard).

### 4.2 Verteilung (Mainnet-Planwert)

| Anteil | % | Zweck |
|---|---|---|
| Community | 81 % | Kern des Community-Projekts |
| Liquidität | 10 % | Initial-Handelspool zum Mainnet-Launch |
| Gründer | 5 % | bewusst klein |
| Marketing-Team | 4 % | — |

> **Status:** Planwert, vom Betreiber bestätigt (09.11.2026). Die mehrstufige Emission (4 getrennte Emissionskonten) ist erst für den **Mainnet-Launch** geplant und wird nach Verteilungsbestätigung umgesetzt. Der Devnet-Lauf emittierte die Gesamtmenge bewusst an ein einweg-Admin-Test-Konto — eine bewusste Prototyp-Entscheidung, keine Verkaufs- oder Distributionsumsetzung. **Sperrfristen (Vesting) für Gründer- und Marketing-Anteile sind noch offen.**

### 4.3 Administration und Irreversibilität

Beide am Mint hängenden Vollmachten wurden nach der Emission **unwiderruflich entzogen** (bestätigt 09.11.2026):

- **Mint-Vollmacht entzogen** → die Gesamtmenge ist endgültig fix; niemand kann mehr Token erzeugen. Kompromittierte Schlüssel können die Supply nicht mehr aufblähen.
- **Freeze-Vollmacht entzogen** → keine Token-Konten können mehr gesperrt werden; höchste Freiheit für Halter, kein einseitiges Machtinstrument.

Der Zustand ist im öffentlichen Solana-Explorer sichtbar: `mintAuthority = (none)`, `freezeAuthority = (none)` — **öffentlich und nachprüfbar**.

**Trade-off (offengelegt):** Nach dem Entzug ist keine Korrektur mehr möglich — kein nachträgliches Minten eines Fehlers, kein Auftauen eines versehentlich eingefrorenen Kontos. Deshalb sind die gesamte Verifikation (`verify.ts`) und alle Korrekturen vor dem Entzug abgeschlossen.

---

## 5. Devnet-Prototyp: Nachvollziehbar

Am **09.11.2026** wurde der Testtoken auf **Solana Devnet** erstellt und ausgeführt. Devnet ist ein **reines Testnetz ohne wirtschaftlichen Wert** — es fließt kein echtes Geld, alle Einträge sind als `DEVNET-TESTTOKEN` gekennzeichnet.

| Feld | Wert |
|---|---|
| Mint-Adresse (Devnet) | `CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf` |
| Supply | 100.000.000.000.000 SIN (10^19 kleinste Einheiten) |
| Test-Transfer | 1.000.000 SIN an eine einweg-Empfänger-Test-Wallet |
| Vollmachten | Mint und Freeze unwiderruflich entzogen |
| Kosten | ~0,5 Test-SOL (Faucet), **keine echten Kosten** |

**Jeder Schritt ist mit Signatur im Solana-Explorer dokumentiert** (vollständige Tabelle: `token/docs/DEVNET-TESTTOKEN-BERICHT.md`):

- Mint: https://explorer.solana.com/address/CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf?cluster=devnet
- Beispiel — Emissions-Transaktion: https://explorer.solana.com/tx/4bemaL978Uupk6PJ4wv3Q7VjzUgtNj7xYVy8NmrW8uuouSM7x2bJwAMAEoz7r4sAoofAbDuUQ4KmcnzdgnLW7mLp?cluster=devnet
- Beispiel — Mint-Vollmacht entzogen: https://explorer.solana.com/tx/4kGskHXLRV48b5AGfFJL4bZzV5JUzvGLUpfK96CyYE3N2n2sCMVFdJJB9myNCMstEquPbDnn31sPPCBqT53xjzpb?cluster=devnet

**Sicherheitslage des Laufs:** Signiert wurde ausschließlich mit lokalen einweg-Test-Wallets. Eine Seed-Phrase oder ein privater Schlüssel des Betreibers wurde nie abgefragt oder verwendet. Nach dem Lauf wurde die Admin-Test-Wallet lokal gesperrt (archiviert) — Minten und Freezen ist On-Chain ohnehin unmöglich, da die Vollmachten entzogen wurden.

---

## 6. Roadmap

Der Mainnet-Launch folgt in drei Phasen. **Nichts davon ist heute bereits erfolgt.**

### Phase 1 — Entscheidungen (vor Mainnet)

- Alle Token-Parameter (Kürzel, Gesamtmenge, Dezimalstellen, Verteilung, Vollmachten) für den Mainnet final bestätigen
- Metadaten-URI auf **content-addressed Speicher** (IPFS z. B. Pinata/Web3Storage oder Arweave) umstellen, statt die provisorische GitHub-URL (s. `token/docs/METADATEN-SPEICHERUNG.md`)
- **Rechtslage für den konkreten Startmarkt prüfen** (kein Rechtsstand gegeben, keine Freigabe)
- Externes **Audit** der Emissions- und Distributions-Logik (bisher nicht durchgeführt)
- Impressum/Datenschutz finalisieren

### Phase 2 — Technische Umsetzung

- Vierstufiges Emissions-Skript (ein Konto pro Verteilungsanteil) — heute emittiert `mint-initial.ts` bewusst die Gesamtmenge an eine einweg-Admin-Konten
- Neue, getrennte **Hardware-Wallets** für Emission und (falls behalten) Freeze — keine einweg-Test-Wallet für den Mainnet
- Metadaten auf dem permanenten Speicher hochladen, `verify.ts` gegen die neue URI laufen lassen
- Domain `superintelnex.com` aus der GitHub-Verification-Phase bringen

### Phase 3 — Transparenz nach Launch

- Mint-Adresse, Emissions- und Entzugs-Signaturen öffentlich protokollieren (explizit `MAINNET`-gelabelt)
- Explorer-Links veröffentlichen
- Im Whitepaper die finalen Mainnet-Parameter nachtragen

> **Was nicht versprochen wird:** kein Kurs, keine Erträge, keine Rechtsfreigabe, keine automatische Börsenaufnahme. Listings erfordern separate Prozesse der jeweiligen Anbieter.

---

## 7. Risiken und rechtlicher Hinweis

- **Status:** Projekt im Aufbau. Es existiert **kein Mainnet-Token, kein Verkauf und kein Liquiditätspool**. Der Devnet-Token hat keinen wirtschaftlichen Wert.
- **Keine Anlageberatung.** Dieses Whitepaper ist ein technisches und planendes Dokument. Es enthält keine Empfehlung zum Erwerb oder Verkauf von Token, keine Kursprognose und keine Gewinnzusagen.
- **Kein Rechtsstand.** Ob und unter welchen Bedingungen ein Mainnet-Start rechtlich möglich ist, wurde noch nicht geprüft. Die Prüfung der Rechtslage für den Startmarkt steht in der Roadmap.
- **Keine zugesagten Features.** Handelbarkeit, Händlerakzeptanz und KI-Anwendungen sind geplante Langfristziele — nicht umgesetzte Funktionen.
- **Offene Punkte werden offengelegt** (z. B. Vesting, Verteilungsbestätigung, Audit), statt als erledigt dargestellt.

---

## Anhang: Quellen und Nachvollziehbarkeit

| Aussage in diesem Whitepaper | Beleg im Repository |
|---|---|
| Kernparameter (SIN, 10^14, 5 Dez., FIXED, 81/10/5/4, Vollmachten) | `token/config/token.json` (Bestätigung 09.11.2026 im `_status`-Feld) |
| u64-Begründung der 5 Dezimalstellen | `token/docs/FRAGENLISTE.md` (Q3) |
| Emissions-Skripte & Test-Suite | `token/README.md`, `token/scripts/`, `token/tests/` |
| Vollmachts-Doku (Mint/Freeze) | `token/docs/AUTHORITIES.md` |
| Devnet-Lauf: Mint, Signaturen, Endzustand | `token/docs/DEVNET-TESTTOKEN-BERICHT.md` |
| Test-Ergebnisse (6/6) & Sicherheitslage | `token/docs/STATUS-BERICHT.md` |
| Mainnet-Offene Punkte | `token/docs/MAINNET-CHECKLISTE.md` |
| URI-Speicher (Devnet provisorisch / Mainnet content-addressed) | `token/docs/METADATEN-SPEICHERUNG.md`, `token/config/token.json` (Feld `metadata._note`) |
| Vision & Risiken (geplante Ziele, keine Zusagen) | `index.html` (Sektionen „Vision" / „Projektstatus"), `token/metadata/superintelnex-token.json` (Description) |

**Kontakt / Kanäle:** X [@superintelnex](https://x.com/superintelnex) · Discord (Link im Footer der Website `superintelnex.com`) · GitHub `superintelnex/superintelnex`

---

*Dokumentversion 0.9 (Draft). Nächste Version nach Bestätigung der Mainnet-Parameter. Alle Parameter gelten für den Devnet-Testtoken; der Mainnet-Launch erfolgt erst nach erneuter Bestätigung und Absolvierung der Roadmap.*

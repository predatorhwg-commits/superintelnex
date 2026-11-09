# Status-Bericht: SuperIntelNex-Token (SPL, Solana)

Stand: 09.11.2026 · Branch `feature/solana-devnet-token` (PR #13) ·
Ort: `token/` im Repo (nicht `solana-token/` — das ist ein leerer
Übersichtsordner mit `node_modules`).

Der Bericht trennt strikt vier Kategorien:

1. **Vorbereiteter Code** — steht, ist nachvollziehbar, aber noch nicht
   auf Devnet ausgeführt.
2. **Tatsächlich ausgeführte Tests** — mit Zeitstempeln und Ergebnissen.
3. **Tatsächlich auf Devnet erstellter Token** — **Nein, noch nicht.**
   (Nur LOCALNET-TEST und ein früherer lokaler Emissionslauf existieren,
   siehe unten.)
4. **Noch offene Arbeiten** — Entscheidungen + ein manueller Schritt.

---

## 1) Vorbereiteter Code (lauffähig, Devnet noch nicht ausgeführt)

| Baustein | Pfad | Status |
|---|---|---|
| Zentrale Konfiguration | `token/config/token.json` | vorhanden, Parameter **BESTÄTIGT** (100 Billion @ 5 Dez., Commit `8c57777`) |
| Mint + Metadaten (1 Tx) | `token/scripts/create-mint.ts` | fertig, getestet auf LOCALNET |
| Emission Gesamtmenge | `token/scripts/mint-initial.ts` | fertig, getestet auf LOCALNET |
| Checked-Transfer 1.234 | `token/scripts/transfer-test.ts` | fertig, getestet auf LOCALNET |
| On-Chain-Abgleich | `token/scripts/verify.ts` | fertig, prüft Decimals/Supply/Vollmachten/Metadaten |
| Vollmachten entziehen | `token/scripts/revoke-authorities.ts` | fertig, **einweg** — nur nach Bestätigung |
| Devnet-Prüfung ohne Tx | `token/scripts/devnet-prefund.ts` | fertig (neu in diesem Lauf) |
| Off-Chain-Metadaten | `token/metadata/superintelnex-token.json` + `assets/` (Logo 512/800 px) | URI korrigiert auf `/token/...` |
| Doku | `token/docs/` (AUTHORITIES, DEVNET-RUNBOOK, METADATEN-SPEICHERUNG, MAINNET-CHECKLISTE, FRAGENLISTE) | vollständig |

Technik: **Standard-SPL-Token** (Token-Programm `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`)
+ **Metaplex Token-Metadata v2** (`metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s`).
Kein eigenes Programm, keine Token-2022-Extensionen, keine Fees/Hooks/
Blacklist-Logik. Laufzeit: Deno (npm-Pakete `@solana/web3.js@1.98.4`,
`@solana/spl-token@0.4.15`, `@metaplex-foundation/mpl-token-metadata@2.5.2`).

**Keine Simulations-Oberfläche:** Die Skripte bauen echte
`Transaction`-Objekte, signieren mit Test-KeyPairs und senden per
`sendRawTransaction` an einen echten RPC-Endpunkt. Lokal wurde das gegen
einen echten `solana-test-validator` (Agave 4.4.1, mit Devnet-Clone des
Metaplex-Programms) verifiziert.

## 2) Tatsächlich ausgeführte Tests (Dieser Lauf, 09.11.2026)

Umgebung: `solana-test-validator` (solana-core 4.4.1) auf `127.0.0.1:8011`,
Metaplex-TM-Program-Clone vorhanden (geprüft via `getAccountInfo`),
Deno 2.9.8.

| Test | Ergebnis | Beleg |
|---|---|---|
| `token/tests/config.test.ts` (offline) | **4/4 ok** | Pflichtfelder, Verteilung=100 %, authorities-Boolean, sellerFeeBasisPoints=0 + **u64-Supply-Guard** (neu: fängt totalSupply × 10^decimals > u64max ab — bei 100 Billion @ 9 Dez. würde genau hier der Fehler liegen) |
| `token/tests/integration.test.ts` (LOCALNET-TEST) | **ok** | Test-Mint (2 Dez.) `4eW2U83N...`, Emission 1234.57, Checked-Transfer 0.50, Decimals-/Supply-/Saldo-Gegenprobe + On-Chain-Metadaten-Name — alles bestanden |
| `token/tests/authorities.test.ts` (LOCALNET-TEST, neu) | **ok** | Test-Mint `64w5Lmyc...`: Freeze-Vollmacht entzogen (sig `37fVxcvH...`) → Freeze-Instruktion On-Chain **abgelehnt**; Mint-Vollmacht entzogen (sig `2TLSdugC...`) → MintTo **abgelehnt**; Supply fix bei 1000.00, beide Vollmachten = `none` |
| `deno test --allow-all token/tests/` (Gesamt) | **6 passed / 0 failed** | Einzelaufruf, 09.11.2026 (inkl. u64-Guard und decimals-awareem Transfer-Test) |
| `token/scripts/devnet-prefund.ts` (devnet-Modus) | **funktioniert** | zeigt Test-Wallet `FoJ8tLty...`, Saldo 0.000000 SOL, die 3 Finanzierungswege; keine Transaktion gesendet |

**Früherer LOCALNET-Testlauf (06:21–06:28, `token/result/EXECUTED-TRANSACTIONS.jsonl`):**
Mint `4vzB8a7AonPzro9NNjbpMZDghh6ZSU8Cbe8GXUDPW6Te` (LOCALNET-TEST!),
Emission 1.000.000.000, Transfer 1.234, beide Vollmachten entzogen,
Admin-Wallet archiviert. Das ist ein **lokaler Validierungslauf, kein
Devnet-Ergebnis** — er taucht in keinem öffentlichen Index auf.

## 3) Tatsächlich auf Devnet erstellter Token?

**JA — am 09.11.2026 wurde der SuperIntelNex-Testtoken (SIN) auf Solana
Devnet erstellt.** (Zuvor in dieser Sitzung: Nein; die Blockade wurde
überbrückt, nachdem der Betreiber per GitHub-Faucet ~0,5 Test-SOL an die
einweg-Admin-Test-Wallet überwiesen hatte.)

- Mint: `CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf`
- Supply: 10^19 smallest units = 100.000.000.000.000 SIN (10^14 @ 5 Dez.)
- 1.000.000 SIN an die einweg-Empfänger-Test-Wallet
  (`2hsXa6fvkns9869eyvorvieEQ2i41M2WwJrp1y2GMpxe`, ATA
  `BPen7C9U3wwkJjsQHURvC6qWDjzTNJSg7YM55pxG5bMJ`) übertragen.
- Mint- und Freeze-Vollmacht **unwiderruflich entzogen** — im Explorer:
  `mintAuthority = (none)`, `freezeAuthority = (none)`.
- Vollständiges Signatur-Protokoll + `?cluster=devnet`-Links:
  `token/docs/DEVNET-TESTTOKEN-BERICHT.md` (Kopie; lokale Quelle in
  `token/result/`, gitignoriert). Alle Einträge als **DEVNET-TESTTOKEN**
  gekennzeichnet — kein Mainnet-Ergebnis.

**Wichtige Korrektur aus diesem Lauf:** Die Metadaten-URI zeigte auf
`superintelnex.com/...`, aber die Custom-Domain lag in der
GitHub-„Verification of Contact Information"-Phase (nicht aktiv) und
`token/` existierte erst auf der Feature-Branche (nicht `main`) → die URI
war tot. Vor dem (unwiderruflichen) Devnet-Mint umgestellt auf die
stabile Raw-URL der Feature-Branche (HTTP 200 geprüft, Commit `22bddbd`)
— diese URI ist jetzt On-Chain fixiert (`isMutable: false`).

**Blockade-Protokoll (überwunden, 09.11.2026):** Zuvor waren alle
offentlichen Wege tot (RPC-Faucet HTTP 410, Ankr/publicnode 404/403,
QuickNode-Faucet verlangt Mainnet-Saldo, Solana-Faucet: frischer
GitHub-Account abgewiesen). Gelöst über `faucet.solana.com` mit einem
älteren GitHub-Konto des Betreibers: 0,5 Test-SOL per Airdrop an die
einweg-Admin-Test-Wallet (Signatur im Bericht oben). Die drei Wege
A/B/C aus `DEVNET-RUNBOOK.md` gelten weiterhin für künftige
Finanzierungen — für diesen Lauf war nur Weg A nötig.

**Sicherheitslage des Laufs:** Signiert wurde ausschließlich mit den
einweg-Test-Wallets; jede Transaktion ist im Explorer nachvollziehbar
(`?cluster=devnet`). Die Seed Phrase / der private Schlüssel des
Betreibers wurden **nie** abgefragt. Nach dem Lauf ist die
Admin-Test-Wallet lokal gesperrt (`main.json` archiviert) —
Minten/Freezen ist On-Chain unmöglich (Vollmachten entzogen).

**Wichtig (Pubkey-Kopplung):** Die Test-Wallet-Dateien liegen lokal
(gitignoriert) und sind je Projektordner eigenständig. `devnet-prefund.ts`
immer in dem Ordner ausführen, in dem der Lauf stattfinden soll, und
**den dort angezeigten Pubkey** finanzieren. Der genannte
`FoJ8tLty...` galt für diesen Worktree.

## 4) Noch offene Arbeiten

### A) Ihre Entscheidungen (kurz) — Details: `token/docs/FRAGENLISTE.md`

| # | Frage | Bestätigter Wert (09.11.2026) |
|---|---|---|
| Q1 | Kürzel | `SIN` |
| Q2 | Gesamtmenge | **100.000.000.000.000** (100 Billion = 10^14, deutsche Zählung) — vorgegeben |
| Q3 | Dezimalstellen | **5** (technisch gebunden an Q2: u64-Supply-Obergrenze erlaubt 10^14 maximal mit 5 Dez.) |
| Q4 | Ausgabe-Policy | **feste Menge, keine weiteren Emissionen** (FIXED-NO-FURTHER-ISSUANCE) |
| Q5 | Verteilung | 55 % Community / 20 % Gründer / 15 % Entwicklung / 10 % Liquidität (Planwert; Multi-Adress-Emission erst für den Mainnet-Launch, Devnet-Lauf mintet die Gesamtmenge an die einweg-Admin-ATA) |
| Q6 | Vollmachten | **beide nach Emission unwiderruflich entziehen** (Mint: sonst unbegrenzte Ausweitung der Supply; Freeze: einzige Sperrmöglichkeit im SPL — Beibehaltung = dauerhafte Macht über fremde Konten; Entzug = kein Rekorrigieren, kein Thawen mehr). On-Chain sichtbar: `mintAuthority = (none)` |
| Q7 | URI-Speicher | Devnet: GitHub Pages (provisorisch); für Mainnet: IPFS (Pinata/Web3Storage) oder Arweave (content-addressed, manipulationsresistent) |
| Q8 | Devnet-Lauf | **abgeschlossen am 09.11.2026** — Devnet-Mint, Emission, Transfer-Test, 1 Mio. SIN an die Empfänger-Test-Wallet, Vollmachten entzogen (Bericht: `DEVNET-TESTTOKEN-BERICHT.md`) |

### B) Technische Restarbeiten

Erledigt (Devnet, 09.11.2026):

- Devnet-Erstellung der 5 Schritte (Mint → Emission → Transfer → Verify →
  Vollmachten entziehen) — abgeschlossen, ~0,5 Test-SOL, keine echten Kosten.
- Ergebnis-Protokoll mit Mint, Signaturen und `?cluster=devnet`-Links als
  **DEVNET-TESTTOKEN** — `token/docs/DEVNET-TESTTOKEN-BERICHT.md`
  (Kopie; lokale Quelle `token/result/`).

Für Mainnet (offen, erst nach erneuter Bestätigung):

1. Falls die Q5-Verteilung final wird: Emissions-Skript für 4
   Verteilungsadressen (Community/Gründer/Dev/Liquidität) — aktuell ist
   das bewusst nicht implementiert (`mint-initial.ts` mintet die
   Gesamtmenge an die einweg-Admin-ATA).
2. Metadaten-URI aktuell On-Chain fixiert auf die Raw-URL der
   Feature-Branche (`isMutable: false` → für diesen Mint dauerhaft). Für
   Mainnet: IPFS/Arweave (content-addressed) + Config-Update +
   `verify.ts` vor dem Mint.
3. Custom-Domain `superintelnex.com` aus der GitHub-Verification-Phase
   bringen (Repository-Settings → Pages), falls die Website-URI künftig
   genutzt werden soll.
4. Neue Devnet-Läufe (Tests, Distributionssimulation) brauchen eine
   **frische** einweg-Admin-Wallet (`main.json` ist lokal gesperrt;
   Weg A/B/C aus `DEVNET-RUNBOOK.md` erneut finanzieren).

### C) Späterer öffentlicher Launch (Mainnet) — kurz

- Entscheidungen: alle Q1–Q7 final; Admin-Wallet(en) getrennt vom
  Mainnet-Tresor; Hardware-Wallet für Emission + (falls behalten) Freeze.
- Prüfung: externe Audits (Emissions-/Distributions-Logik), Rechtslage
  für Startmarkt, Impressum/Datenschutz final.
- Finanzierung: Rent + Fees pro Mainnet-Transaktion (~0,001–0,005 SOL
  pro Tx), Emission/ATA-Setup ~0,1 SOL, Distributionskonten ~0,02 SOL
  pro Account; Liquiditätspool + Market-Maker-Fees danach (außerhalb
  dieses Auftrags).
- Metadaten: IPFS/Arweave-Upload + `config`-Aktualisierung + `verify.ts`
  vor dem Mainnet-Mint.
- Keine Zusagen: kein Kurs, kein Gewinn, keine Rechtsfreigabe, keine
  automatische Börsenaufnahme; Listings erfordern separate Anbieter-
  Prozesse.

---

## Sicherheitslage (Status)

- Nur einweg-Test-Wallets (`token/wallets/*.json`, gitignoriert):
  `main` (Devnet-Admin, in diesem Lauf `FoJ8tLty...`), `mint`,
  `recipient`, `test-admin`. `main.json.archiviert` ist der
  lokal entzogene Admin.
- Keine Schlüssel in Repo, Logs oder Frontend; `result/` und `wallets/`
  sind gitignoriert.
- Keine Seed-Phrase-/Key-Anfrage; Finanzierungswege A/B/C oben sind
  optional und nur für wertloses Test-SOL.

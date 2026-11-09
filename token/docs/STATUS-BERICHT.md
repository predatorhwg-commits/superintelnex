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
| Zentrale Konfiguration | `token/config/token.json` | vorhanden, alle Parameter mit `NOT-FINAL` markiert |
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
| `token/tests/config.test.ts` (offline) | **3/3 ok** | Pflichtfelder, Verteilung=100 %, authorities-Boolean, sellerFeeBasisPoints=0 |
| `token/tests/integration.test.ts` (LOCALNET-TEST) | **ok** | Test-Mint (2 Dez.) `4eW2U83N...`, Emission 1234.57, Checked-Transfer 0.50, Decimals-/Supply-/Saldo-Gegenprobe + On-Chain-Metadaten-Name — alles bestanden |
| `token/tests/authorities.test.ts` (LOCALNET-TEST, neu) | **ok** | Test-Mint `64w5Lmyc...`: Freeze-Vollmacht entzogen (sig `37fVxcvH...`) → Freeze-Instruktion On-Chain **abgelehnt**; Mint-Vollmacht entzogen (sig `2TLSdugC...`) → MintTo **abgelehnt**; Supply fix bei 1000.00, beide Vollmachten = `none` |
| `deno test --allow-all token/tests/` (Gesamt) | **5 passed / 0 failed** | Einzelaufruf, 09.11.2026 |
| `token/scripts/devnet-prefund.ts` (devnet-Modus) | **funktioniert** | zeigt Test-Wallet `FoJ8tLty...`, Saldo 0.000000 SOL, die 3 Finanzierungswege; keine Transaktion gesendet |

**Früherer LOCALNET-Testlauf (06:21–06:28, `token/result/EXECUTED-TRANSACTIONS.jsonl`):**
Mint `4vzB8a7AonPzro9NNjbpMZDghh6ZSU8Cbe8GXUDPW6Te` (LOCALNET-TEST!),
Emission 1.000.000.000, Transfer 1.234, beide Vollmachten entzogen,
Admin-Wallet archiviert. Das ist ein **lokaler Validierungslauf, kein
Devnet-Ergebnis** — er taucht in keinem öffentlichen Index auf.

## 3) Tatsächlich auf Devnet erstellter Token?

**Nein.** Es existiert **kein** Devnet-Mint von SuperIntelNex.

Blockade (geprüft in diesem Lauf):

- Öffentlicher Devnet-Airdrop: `https://api.devnet.solana.com` →
  HTTP 410 „The RPC faucet is closed on this cluster".
- Testnet-Endpunkt: ebenfalls HTTP 410.
- Public-RPCs mit Airdrop (Ankr, publicnode): 404 / 403.
- Web-Faucets (`faucet.solana.com` etc.): CAPTCHA (Cloudflare Turnstile) —
  wird aus Sicherheitsgründen in diesem Projekt **nicht** umgangen
  (regel in `DEVNET-RUNBOOK.md`).

**Damit Devnet wirklich läuft, braucht es einen einzigen manuellen
Schritt von Ihnen** (Test-SOL ist wertlos, es geht nichts Reales):

- **Wege A (empfohlen):** `https://faucet.solana.com/` im eigenen Browser,
  Pubkey der einweg-Test-Wallet eintragen: **`FoJ8tLtyPfPMR3ni1wESJVWTCdE8RBeSaazYMPUSy6F4`**
  (~0,5 Test-SOL). Den Inhalt der Wallet-Datei selbst niemals in fremde
  Felder kopieren — nur den Pubkey.
- **Wege B:** einen RPC mit aktivem Airdrop (QuickNode/Alchemy-Devnet-URL,
  eigener Account) als `SIN_RPC` bereitstellen.
- **Wege C:** ~0,05–0,1 Test-SOL von einer Ihrer Devnet-Tester-Wallets
  per `solana transfer FoJ8tLtyPfPMR3ni1wESJVWTCdE8RBeSaazYMPUSy6F4 0.1`
  senden.

Sobald die Wallet finanziert ist (und die Parameter in `FRAGENLISTE.md`
bestätigt sind), laufen die 5 Befehle aus `DEVNET-RUNBOOK.md` §3 —
jede Signatur wird im Ergebnis-Protokoll als **DEVNET-TESTTOKEN**
dokumentiert mit Mint-Adresse, Signaturen und
`?cluster=devnet`-Explorer-Links. Sie können jede Transaktion vor dem
Abschluss in Ihrer Wallet prüfen; signiert wird ausschließlich mit den
einweg-Test-Wallets. **Ihre Seed Phrase / Ihr privater Schlüssel werden
niemals abgefragt.**

**Wichtig (Pubkey-Kopplung):** Die Test-Wallet-Dateien liegen lokal
(gitignoriert) und sind je Projektordner eigenständig. Da im
Hauptprojekt-Ordner `main.json` aus dem Localnet-Lauf archiviert ist,
erzeugt das Skript dort bei Bedarf eine **frische** einweg-Admin-Wallet.
Deshalb: `devnet-prefund.ts` in dem Ordner ausführen, in dem der
Devnet-Lauf stattfinden soll, und **den dort angezeigten Pubkey**
finanzieren (nicht zwingend die oben historischen Adressen). Der
genannte `FoJ8tLty...` gilt nur für den aktuellen Arbeits-Worktree.

**Wichtige Korrektur aus diesem Lauf:** Die Metadaten-URI zeigte auf
`superintelnex.com/solana-token/...`, aber der Repo-Ordner heißt `token/`
→ die URI war tot. Korrigiert auf `/token/metadata/...` (Commit
`66b02ee`). **Deshalb muss der Devnet-Lauf erst nach diesem Fix erfolgen
** — die On-Chain-Metadaten sind mit `isMutable: false` unwandelbar.

## 4) Noch offene Arbeiten

### A) Ihre Entscheidungen (kurz) — Details: `token/docs/FRAGENLISTE.md`

| # | Frage | Vorschlag (begründet) |
|---|---|---|
| Q1 | Kürzel | `SIN` (3 Zeichen, aus dem Namen abgeleitet; Alternativen: SNX, SI) |
| Q2 | Gesamtmenge | 1.000.000.000 (runde, leicht kommunizierbare Größenordnung) |
| Q3 | Dezimalstellen | 9 (SPL-Standard, wie SOL) |
| Q4 | Ausgabe-Policy | **feste Menge, keine weiteren Emissionen** (höchste Integrität; nach Entzug der Mint-Vollmacht ohnehin unmöglich) |
| Q5 | Verteilung | 55 % Community / 20 % Gründer / 15 % Entwicklung / 10 % Liquidität (+ optional Vesting für Gründer/Dev) — Multi-Adress-Emission ist GEPLANT, erscheint erst nach Bestätigung |
| Q6 | Vollmachten | **beide nach Emission unwiderruflich entziehen** (Mint: sonst unbegrenzte Ausweitung der Supply; Freeze: einzige Sperrmöglichkeit im SPL — Beibehaltung = dauerhafte Macht über fremde Konten; Entzug = kein Rekorrigieren, kein Thawen mehr). On-Chain sichtbar: `mintAuthority = (none)` |
| Q7 | URI-Speicher | Devnet: GitHub Pages reicht; für Mainnet: IPFS (Pinata/Web3Storage) oder Arweave (content-addressed, manipulationsresistent) |
| Q8 | Devnet-Lauf | nach Q1–Q7 + nach Test-SOL-Finanzierung (Wege A/B/C) |

### B) Technische Restarbeiten (nach Ihren Entscheidungen)

1. Devnet-Erstellung der 5 Schritte (Mint → Emission → Transfer →
   Verify → [Vollmachten entziehen]) — ~0,5 Test-SOL, keine echten Kosten.
2. Falls Q5 bestätigt wird: Emissions-Skript für 4 Verteilungsadressen
   (Community/Gründer/Dev/Liquidität) — aktuell ist das bewusst nicht
   implementiert (`mint-initial.ts` mintet die Gesamtmenge an die
   einweg-Admin-ATA).
3. Metadaten-URI live erreichbar machen: `token/` muss via Merge nach
   `main` deployed (GitHub Pages). Vor dem Devnet-Lauf prüfen:
   `curl -I https://superintelnex.com/token/metadata/superintelnex-token.json`.
4. Ergebnis-Protokoll: Mint, Signaturen, `?cluster=devnet`-Explorer-Links,
   als **DEVNET-TESTTOKEN** markiert (`token/result/`).

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

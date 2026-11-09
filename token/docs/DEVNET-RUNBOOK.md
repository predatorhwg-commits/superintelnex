# Devnet-Runbook (token/)

Ziel: Das Testtoken einmalig auf **Devnet** erstellen und den ganzen
Lebenszyklus dort verifizieren. Devnet = Pruefnetz mit wertlosem
Test-SOL. Das Ergebnis ist immer als `DEVNET-TESTTOKEN` zu labeln —
nicht „auf Devnet veroffentlicht".

## 1) Vorbereitung (maschinenbedingt)

- Deno steht unter `~/.deno/bin/deno`, die Agave-CLI unter
  `~/.local/share/solana/install/active_release/bin`.
- Kein Node, kein npm, kein cargo: alle Laeufe gehen ueber
  `deno run --allow-all` bzw. `deno test`.

## 2) Devnet-SOL beschaffen

Der oeffentliche Devnet-Airdrop (`faucet.solana.com` / RPC-`requestAirdrop`
gegen `api.devnet.solana.com`) war zum Arbeitszeitpunkt **abgeschaltet**
(HTTP 410) und alle Web-Faucets (QuickNode, Solana-Faucet-UI) erfordern
CAPTCHA (Cloudflare Turnstile). CAPTCHA wird in diesem Projekt nicht
umgangen.

Empfohlener Weg fuer den Betreiber:
1. **Manuell:** `https://faucet.solana.com/` im eigenen Browser, Wallet
   `token/wallets/main.json` (Pubkey anzeigen; den Inhalt selbst niemals
   in fremden Felder kopieren).
2. **Alternativ:** Ein RPC-Endpunkt, der `requestAirdrop` aktiviert
   (z. B. ein QuickNode/Alchemy-Projekt), durch `SIN_RPC` uebergeben:
   ```bash
   SIN_NETWORK=devnet SIN_RPC=https://<ihr-rpc> deno run --allow-all token/scripts/create-mint.ts
   ```
3. Notfalls: 0.05–0.1 Test-SOL von einer bekannten Wallet per Transfer
   an `token/wallets/main.json` ueber die Agave-CLI (`solana transfer`).

SOL-Bedarf pro Lauf (Devnet): ~0.05 SOL (Mint-Rent, ATA, Gebuehren).
~0.2 SOL Puffer reicht mit Ausrede.

## 3) Laufreihenfolge auf Devnet

```bash
export PATH="$HOME/.deno/bin:$PATH"   # falls noch nicht gesetzt
cd SuperIntelNex

# 0) Offline-Konfigcheck (kein Netzwerk)
deno test --allow-read token/tests/config.test.ts

# 1) Mint + Metadaten + Admin-ATA (ein Transaktion)
SIN_NETWORK=devnet deno run --allow-all token/scripts/create-mint.ts

# 2) Emission der Gesamtmenge an die Admin-ATA
SIN_NETWORK=devnet deno run --allow-all token/scripts/mint-initial.ts

# 3) Test-Transfer 1.234 SIN an frische Test-Wallet
SIN_NETWORK=devnet deno run --allow-all token/scripts/transfer-test.ts

# 4) Abgleich der On-Chain-Parameter gegen die Konfiguration
SIN_NETWORK=devnet deno run --allow-all token/scripts/verify.ts

# 5) NUR nach bewusster Entscheidung des Betreibers:
SIN_NETWORK=devnet deno run --allow-all token/scripts/revoke-authorities.ts
```

Jeder Schritt haengt, bevor die Waehler in `config/token.json`
bestaetigt sind (SIN / 9 Dezimalstellen / 1.000.000.000 / fest /
55-20-15-10 / beides entziehen). Die Konfiguration ist mit
`"_status": "NOT-FINAL"` gekennzeichnet und darf erst nach Bestaetigung
umgebaut werden.

## 4) Protokoll / Nachweis

- `token/result/MINT-ADDRESS.txt` — Mint, ATA, Metadaten-PDA, Signatur
  der Erzeugungs-Transaktion, laeuft mit dem Label `DEVNET-TESTTOKEN`.
- `token/result/EXECUTED-TRANSACTIONS.jsonl` — jede Signatur mit
  Zeitstempel, Netzlabel und Schrittname.
- Explorer-Links (im Pruefbericht immer „DEVNET/TESTTOKEN" labeln):
  - Mint: `https://explorer.solana.com/address/<MINT>?cluster=devnet`
  - Tx: `https://explorer.solana.com/tx/<SIGNATUR>?cluster=devnet`

## 5) Wiederholung auf localnet (ohne Devnet-SOL)

```bash
# Validator mit Devnet-Programmen (SPL-Token + Metaplex-TM) starten
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana-test-validator --reset --quiet --bind-address 127.0.0.1 \
  --rpc-port 8011 --faucet-port 8012 --ledger ~/.sln-local/ledger \
  --url devnet \
  --clone-upgradeable-program metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s
```

Danach `SIN_NETWORK=localnet` (Standard) verwenden. Alles laeuft auf
`127.0.0.1:8011`, Airdrops koennen per Skript `requestAirdrop`
ausgelöst werden.

## 6) Was NICHT passiert

- Kein Mainnet-Start, kein Verkauf, keine Liquidaet, kein Realgeld.
- Keine Seed-Phrase oder Private-Key-Anfragen; die einweg-Test-Wallets
  liegen als base58-JSON unter `token/wallets/` (gitignoriert).
- Die Distribution (55/20/15/10) ist ein Vorschlag; der Emissions-Code
  (`mint-initial.ts`) mintet momentan die Gesamtmenge an die Admin-ATA,
  nicht an die vier Anteile. Die Mehrfach-Emission ist GEPLANT und
  erscheint erst, wenn der Betreiber die Aufteilung bestaetigt hat.

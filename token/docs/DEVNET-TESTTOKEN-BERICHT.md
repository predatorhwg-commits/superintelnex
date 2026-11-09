# DEVNET-TESTTOKEN — Ergebnis-Protokoll SuperIntelNex (SIN)

Stand: 09.11.2026 · Netz: **SOLANA DEVNET** · Kennzeichnung: **DEVNET-TESTTOKEN**
(reines Testnetz, kein echtes Geld; kein Mainnet-Ergebnis, keine Kurs-/Gewinn-Aussage)

## Mint (Token + On-Chain-Metadaten)

| Feld | Wert |
|---|---|
| Mint-Adresse | `CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf` |
| Name / Symbol | SuperIntelNex / SIN |
| Decimals | 5 |
| Total Supply | 100.000.000.000.000 (10^14) = 10^19 smallest units |
| Metadaten-URI | https://raw.githubusercontent.com/predatorhwg-commits/superintelnex/feature/solana-devnet-token/token/metadata/superintelnex-token.json |
| isMutable | false (On-Chain fixiert) |
| Metadaten-PDA | `DFBZb3SuyvstKn4GvjCdgvAgbP6QCHp3UQi2nyt1d4WR` |

**Explorer (DEVNET):**
- Mint: https://explorer.solana.com/address/CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf?cluster=devnet
- ATA Admin: https://explorer.solana.com/address/Ha8pCNYRT9CQ1iYZD9Xgaw2VBKKK78CjuL5VLhzwEhZ5?cluster=devnet
- ATA Empfänger: https://explorer.solana.com/address/BPen7C9U3wwkJjsQHURvC6qWDjzTNJSg7YM55pxG5bMJ?cluster=devnet

## Signierte Transaktionen (alle DEVNET)

| Schritt | Signatur | Explorer |
|---|---|---|
| Airdrop 0,5 Test-SOL (Faucet) | 4rnmBpepdUCdmU4D5XyS794DbQms7xB13Rv24mJ8wAxT4Wghqr88khzzRnacPi94Yn46gUeJt3oUVm9k9Bqa4ntY | https://explorer.solana.com/tx/4rnmBpepdUCdmU4D5XyS794DbQms7xB13Rv24mJ8wAxT4Wghqr88khzzRnacPi94Yn46gUeJt3oUVm9k9Bqa4ntY?cluster=devnet |
| 1. create-mint (Mint+ATA+Metadaten) | 3xTz68ijmkYEB9iZo3AdG8kDRX2xqfftubaHAPNN6jTEXPmzDmTTHYehrw5YznymVueCTKf1SLfLfpg67vmsRExX | https://explorer.solana.com/tx/3xTz68ijmkYEB9iZo3AdG8kDRX2xqfftubaHAPNN6jTEXPmzDmTTHYehrw5YznymVueCTKf1SLfLfpg67vmsRExX?cluster=devnet |
| 2. mint-initial (100 Billion SIN) | 4bemaL978Uupk6PJ4wv3Q7VjzUgtNj7xYVy8NmrW8uuouSM7x2bJwAMAEoz7r4sAoofAbDuUQ4KmcnzdgnLW7mLp | https://explorer.solana.com/tx/4bemaL978Uupk6PJ4wv3Q7VjzUgtNj7xYVy8NmrW8uuouSM7x2bJwAMAEoz7r4sAoofAbDuUQ4KmcnzdgnLW7mLp?cluster=devnet |
| 3a. ATA-Recipient anlegen | 2XqsCnzDeDrE4cpMDcxqLANsuDsWBvhYxgbQ4tYBEcrsbXadB3mVZGMKxdSiDzJY3QM1nTJjXLB8wrWNnD1eoAyQ | https://explorer.solana.com/tx/2XqsCnzDeDrE4cpMDcxqLANsuDsWBvhYxgbQ4tYBEcrsbXadB3mVZGMKxdSiDzJY3QM1nTJjXLB8wrWNnD1eoAyQ?cluster=devnet |
| 3b. Checked-Transfer-Test 1.234 SIN | 3aNM3HavfKXGdBfVBvF2YAzfo35JRUQatE59c2S6MTrCUPkoCk9Lt7iVnicDeE9Yn6RVYYZjv1yeV2UkkwjeXrbh | https://explorer.solana.com/tx/3aNM3HavfKXGdBfVBvF2YAzfo35JRUQatE59c2S6MTrCUPkoCk9Lt7iVnicDeE9Yn6RVYYZjv1yeV2UkkwjeXrbh?cluster=devnet |
| 4. Transfer 1.000.000 SIN an Empfänger | 5ssTrnJQNRM8ivmxyfansm68se8q28UEUFPvLWY19KB4JNj5atrFSN2us9JR2mzTmKaZJmYaMhACZNQCsfyauQKC | https://explorer.solana.com/tx/5ssTrnJQNRM8ivmxyfansm68se8q28UEUFPvLWY19KB4JNj5atrFSN2us9JR2mzTmKaZJmYaMhACZNQCsfyauQKC?cluster=devnet |
| 5a. Mint-Vollmacht entzogen | 4kGskHXLRV48b5AGfFJL4bZzV5JUzvGLUpfK96CyYE3N2n2sCMVFdJJB9myNCMstEquPbDnn31sPPCBqT53xjzpb | https://explorer.solana.com/tx/4kGskHXLRV48b5AGfFJL4bZzV5JUzvGLUpfK96CyYE3N2n2sCMVFdJJB9myNCMstEquPbDnn31sPPCBqT53xjzpb?cluster=devnet |
| 5b. Freeze-Vollmacht entzogen | 4rUFwheZM9g8xgyCBqwP2SYWdE1B361fkCPqydTrGECPpkSU7qse2baFtVGc5d9MEnrHs2N1wXxPHXUozz1ik2XQ | https://explorer.solana.com/tx/4rUFwheZM9g8xgyCBqwP2SYWdE1B361fkCPqydTrGECPpkSU7qse2baFtVGc5d9MEnrHs2N1wXxPHXUozz1ik2XQ?cluster=devnet |

## Endzustand (On-Chain, geprüft per verify.ts)

- decimals = 5 ✅ · supply = 10^19 smallest units = 100 Billion SIN ✅
- mintAuthority = **(keine)** · freezeAuthority = **(keine)** — unwiderruflich entzogen ✅
- Metadaten On-Chain: Name/Symbol/URI exakt wie konfiguriert, isMutable=false ✅

## Einweg-Test-Wallets (gitignoriert, NIE das Haupt-/Tresor-Wallet)

| Rolle | Adresse (Pubkey) |
|---|---|
| Admin (erzeugt, signierte alle Txs) | `FoJ8tLtyPfPMR3ni1wESJVWTCdE8RBeSaazYMPUSy6F4` (lokal archiviert/sperrbar) |
| Empfänger (hält 1.000.001,234 SIN) | `2hsXa6fvkns9869eyvorvieEQ2i41M2WwJrp1y2GMpxe` |
| Mint-Keypair | `CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf` |

**Sicherheitslage:** Alle Signaturen erfolgten ausschließlich mit lokalen
einweg-Test-Schlüsseln. Keine Seed-Phrase, kein privater Schlüssel des
Betreibers wurde abgefragt oder verwendet. Für Mainnet gilt dieser Stand
erst nach erneuter Bestätigung — hier: DEVNET-TESTTOKEN, kein echtes Geld.

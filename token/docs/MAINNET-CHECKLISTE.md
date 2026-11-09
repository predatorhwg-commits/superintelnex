# Mainnet-Checkliste (token/)

Stand: Testtoken lokal/Devnet erstellt, **kein Mainnet-Start
erfolgt**. Diese Liste ist die Vorlage für die Phase „öffentlicher
Launch". Keine Einzelpost ist vorab erledigt; alles hier ist
**offene Arbeit**.

## 1. Entscheidungen (Betreiber)

Die Parameter wurden am 09.11.2026 für den DEVNET-Testtoken bestätigt
(Details: `FRAGENLISTE.md`); sie gelten für Mainnet erst nach
erneuter Bestätigung:

- [x] **Ticker/Kürzel** — `SIN` (bestätigt 09.11.2026)
- [x] **Gesamtmenge** — 100.000.000.000.000 (100 Billion = 10^14, bestätigt)
- [x] **Dezimalstellen** — 5 (technisch gebunden an 10^14: u64-Supply-
      Obergrenze, max. 5 Dez.; bestätigt)
- [x] **Verteilung** — 55/20/15/10 (Planwert, bestätigt;
      Sperrfristen/Vesting für Gründer/Dev: noch offen)
- [x] **Admin-Vollmachten** — beide nach Emission entziehen
      (bestätigt; `AUTHORITIES.md`)
- [ ] **Metadaten-URI** — Devnet: Raw-URL der Feature-Branche (fixiert im
      Devnet-Mint). Für Mainnet: IPFS/Arweave (content-addressed)
      entscheiden (`METADATEN-SPEICHERUNG.md`).

## 2. Technische Vorbereitungen

- [ ] Distributions-Skript: `mint-initial.ts` emittiert aktuell die
      Gesamtmenge an eine Admin-ATA; ein vierstufiges Emissions-
      Skript (pro Anteil ein Emissionskonto) ist **GEPLANT** und
      erst nach Verteilungsbestätigung zu implementieren.
- [ ] Off-Chain-Metadaten auf dem gewählten permanenten Speicher
      (IPFS/Arweave) hochladen, `uri` in `config/token.json`
      aktualisieren und vor dem Mainnet-Mint testen
      (`verify.ts` lokal gegen die neue URI).
- [ ] Explorer-Verlinkung im Ergebnis-Protokoll auf
      `?cluster=mainnet-beta` umstellen (aktuell: Devnet/Localnet).
- [ ] Keine Test-Adressen, keine `DEVNET-TESTTOKEN`-Labels in
      öffentlichen Dokumenten — `result/` ist ohnehin gitignoriert.

## 3. Sicherheit / Schlüsselschutz

- [ ] **Keine einweg-Test-Wallet für Mainnet** — neue,
      getrennte Haupt-Tresor-Wallets (z. B. Hardware-Wallet) für
      Emission und (falls behalten) Freeze-Vollmacht.
- [ ] Keys niemals in Repo, Logs, Screenshots oder Frontend.
- [ ] Emissions-Skript gegen Mainnet: `config/token.json`
      `networks.default` auf `mainnet` setzen (aktuell:
      `localnet`) und per `SIN_NETWORK=mainnet` ausführen.
- [ ] Vor dem Entzug: Bestätigung, dass alle Emissionen
      abgeschlossen sind — danach ist die Supply endgültig fix.

## 4. Rechtliches / Transparenz (nicht erledigt)

- [ ] **Audit** der Emissions- und Distributions-Logik (externer
      Auditor; kein Audit durchgeführt).
- [ ] **Rechtslage** für den konkreten Startmarkt prüfen (kein
      Rechtsstand gegeben, keine Freigabe).
- [ ] **Risikohinweis** auf der Website bleibt sichtbar
      (Abschnitt `#risiko` auf der Landingpage).
- [ ] **Impressum/Datenschutz** vor öffentlichem Launch
      finalisieren (siehe Website-Dokumentation).

## 5. Kein Kurs-, Profit- oder Garantieberichten

- [ ] Keine Kursprognose, keine „geprüft von"-Angaben, keine
      erfundenen Zahlen (Inhaltsregeln AGENTS.md gelten auch hier).
- [ ] Alle Zahlen im Launch-Skript stammen aus `config/token.json`
      und sind dort mit Quellen belegt (in `docs/QUELLEN.md`
      ergänzen, falls neue Fakten hinzukommen).

## 6. Betrieb (nach Mainnet-Erstellung)

- [ ] Mint-Adresse + Emissions-Signaturen im öffentlichen
      Ergebnis-Protokoll dokumentieren (explizit
      `MAINNET` gelabelt, nicht „DEVNET/TESTTOKEN").
- [ ] Explorer-Links zum Mint + zur Erzeugungs-Transaktion
      veröffentlichen.
- [ ] Falls Vollmachten entzogen: Signaturen beider
      `SetAuthority`-Transaktionen protokollieren (beweisbarer
      Zustand `mintAuthority = (none)`).

## Was in diesem Prototyp NICHT enthalten ist

- Kein Mainnet-Start, kein Sale, keine Liquidität, kein Realgeld.
- Keine Token-2022-Extensionen (Fee, Hook, Freeze-Beschränkung
  jenseits der Standard-SPL).
- Keine versprochenen Listings, keine Partnerschaften, keine
  „geprüft von"-Angaben.

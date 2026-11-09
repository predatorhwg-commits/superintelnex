# Vollmachten (Authorities) am Mint (token/)

Dieses Dokument erklärt die beiden Vollmachten, die beim Anlegen des
Mints gesetzt werden, was jede Einzelne kann, und welche Optionen beim
**irreversiblen Entzug** bestehen. Das ist eine offengelegte
Sicherheitsentscheidung — keine versteckte Gewalt im Programm.

Es gibt beim klassischen SPL Token (Token Program
`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`) exakt zwei am Mint
hängende Vollmachten:

## MintAuthority (Mint-Vollmacht)

- Wer das ist: die Wallet, die `mintAuthority` am Mint-Account
  besitzt (im Projekt: die einweg-Admin-Test-Wallet).
- Was sie kann: **neue Token erzeugen** (`MintTo`) und damit die
  Gesamtmenge erhöhen. Ohne diese Vollmacht ist die Supply fixiert.
- Wer die hat, bestimmt: ob später noch Token „aus dem Nichts"
  erscheinen. Das ist das eigentliche Risiko einer aufrechten
  Mint-Vollmacht.

## FreezeAuthority (Freeze-Vollmacht)

- Wer das ist: die Wallet, die `freezeAuthority` am Mint-Account
  besitzt.
- Was sie kann: Token-Accounts von beliebigen Haltern **einfrieren**
  (`Freeze`) bzw. **auftauen** (`Thaw`).
- Wer die hat, kann theoretisch das Konto eines Halters blockieren.
  Im SPL-Standard gibt es keine Blacklist-Logik im Programm selbst —
  einfrieren ist die einzige „Sperr"-Möglichkeit und ist eine
  explizite, protokollierte Transaktion.

## Konfiguration (aktuell in `config/token.json`)

```json
"authorities": {
  "revokeMintAuthority": true,
  "revokeFreezeAuthority": true
}
```

Beide `true` = Vorschlag „nach Emission beides entziehen". Der
Betreiber hat diese Werte **noch nicht bestätigt**
(`"_status": "NOT-FINAL"`).

## Optionen (Vorteile / Nachteile)

### 1. Beide Vollmachten entziehen (Vorschlag: beides auf `null`)

- Nach dem Entzug kann **niemand** mehr minten und niemand mehr
  einfrieren. Das ist ein irreversibler, einseitiger, öffentlich
  nachprüfbarer Zustand (im Explorer sichtbar: `mintAuthority =
  (none)`).
- Vorteil: höchste Integrität für die Community; der Token ist nach
  Emission vollständig von niemandem mehr kontrollierbar.
- Nachteil: keine spätere Korrektur mehr möglich (z. B. kein
  nachträgliches Minten eines Fehlers, kein Thaw eines versehentlich
  eingefrorenen Kontos mehr möglich).
- Geeignet: wenn die Gesamtmenge und Verteilung **vor** dem Entzug
  final und korrekt sind.

### 2. Mint-Vollmacht entziehen, Freeze-Vollmacht behalten

- Die Supply ist fix, aber das Team kann eingefrorene Konten
  auftauen (oder Konten einfrieren, z. B. bei Missbrauch).
- Vorteil: operativer Puffer, kein sturer Lockdown.
- Nachteil: solange die Freeze-Vollmacht existiert, besteht die
  Option, Konten zu blockieren. Das ist ein Vertrauensrisiko, das
  offen kommuniziert werden muss.
- Geeignet: wenn die Verteilung bereits erfolgt ist, aber ein
  Sicherheitspuffer gewünscht wird (z. B. bei einem nachträglichen
  Bug im Emissions-Code).

### 3. Beide Vollmachten behalten

- Maximale Flexibilität, aber maximale Vertrauenslast auf eine
  einzige Wallet.
- Vorteil: spätere Änderungen (minten, freeze/thaw) möglich.
- Nachteil: wer die Wallet-Keys hat, kontrolliert den Token
  vollständig; ein Verlust der Keys würde beide Funktionen für immer
  entfernen, aber keinen Missbrauch verhindern.
- Geeignet: nur als **vorübergehender Zustand** während der
  Erprobungsphase — nicht als Endzustand.

## Was das Entzug-Skript konkret macht

`token/scripts/revoke-authorities.ts`:

1. Liest `config/token.json` → beide Booleans.
2. Pro `true`-Wert: eine `SetAuthority`-Transaktion am Mint
   (Reihenfolge: `MintTokens` → `FreezeAccount`, `newAuthority =
   null`).
3. Protokolliert beide Signaturen in `result/EXECUTED-TRANSACTIONS.jsonl`.
4. Prüft nach: `getMint()` muss `mintAuthority = null` und /
   `freezeAuthority = null` ergeben, je nach Konfiguration.
5. Wenn **beide** entzogen wurden: `token/wallets/main.json` wird
   nach `token/wallets/main.json.archiviert` **umbenannt** (nicht
   gelöscht, damit der Betreiber bei einem Irrtum die Datei
   zurückstellen kann — die On-Chain-Vollmachten sind aber
   dauerhaft weg).

**Wichtig:** Der Entzug ist auf-chain irreversibel. Vor der
Ausführung müssen die Gesamtmenge, die Verteilung und alle
Korrekturen abgeschlossen sein.

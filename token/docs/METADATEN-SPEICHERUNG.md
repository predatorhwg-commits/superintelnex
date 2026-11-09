# Metadaten-Speicherung (token/)

Wie die Token-Metadaten (Name, Kürzel, Bild, URI) auf Solana
gelagert sind und wer sie ändern kann.

## Aufteilung: On-Chain vs. Off-Chain

### On-Chain (im Metaplex Token-Metadaten-Programm)

Programm: `metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s`
(Metaplex Token Metadata v2, fungibele SPL-Token).

Beim `create-mint.ts`-Aufruf wird ein Metadaten-Account als PDA
angelegt (Seeds `["metadata", program_id, mint]`). Darin liegen:

| Feld | Wert (aktuell) |
|---|---|
| `name` | `SuperIntelNex` |
| `symbol` | `SIN` (Vorschlag, nicht bestätigt) |
| `uri` | `https://superintelnex.com/token/metadata/superintelnex-token.json` |
| `sellerFeeBasisPoints` | `0` (keine Verkaufsprovision) |
| `creators` | Admin-Test-Wallet, 100 % |
| `isMutable` | `false` |

### Off-Chain (die `uri` zeigt darauf)

- `token/metadata/superintelnex-token.json` im Repo (Commit):
  Beschreibung, Bild-URL, Kategorie, `seller_fee_basis_points: 0`.
- `token/assets/superintelnex-logo-512.png` (und 800-px-Variante):
  wird von GitHub Pages ausgeliefert unter
  `superintelnex.com/token/assets/...`.
- Die `uri` ist ein gewöhnlicher HTTPS-Link. Wer ihn hostet, kann
  den Inhalt ändern — solange das Metadaten-Account änderbar ist.

## Wer darf die Metadaten ändern?

Beim Anlegen ist `updateAuthority = Admin-Test-Wallet` (die in
`wallets/main.json` liegt). Das heißt:

- `isMutable: false` macht die On-Chain-Metadaten nach dem
  Anlegen **dauerhaft unveränderbar**. Das Programm lehnt jede
  `Update`-Instruktion ab, unabhängig davon, ob die
  `updateAuthority` noch existiert.
- Das ist eine bewusste Entscheidung: Name, Symbol, URI und
  Creators sind zum Anlegezeitpunkt fixiert. Korrekturen sind
  danach **nicht** möglich (bewusst keine Token-2022
  `mutable: true`-Variante, die hier nicht verwendet wird).
- Die `updateAuthority` selbst kann per `SetAuthority` entzogen
  oder übertragen werden; das ändert nichts an `isMutable`.
- **Folge:** Vor dem `create-mint.ts`-Aufruf muss die
  `uri`-Ziel-Datei (off-Chain-JSON) final sein. Die On-Chain-
  Metadaten sind danach einseitig gesetzt.

## Entscheidung: permanenter Off-Chain-Speicher

Derzeit: GitHub Pages (Repo + GitHub-Pages-Domain). Das ist für den
Testtoken ausreichend, aber:

- GitHub Pages kann vom Repo-Besitzer jederzeit deaktiviert werden.
- Für einen dauerhaften Launch ist ein **content-addressed**
  Speicher (IPFS oder Arweave) der übliche Standard, da die URI
  dann auf einen Hash zeigt und nicht auf eine manipulierbare
  Datei-URL.

**Geplant, noch nicht entschieden:** IPFS-Upload (z. B. über
`Pinata` oder `Web3Storage`) oder `Arweave` (AO-Format). Bis dahin
gilt die GitHub-URI als Provisorium. Das ist im
`config/token.json` als `metadata._note` dokumentiert.

## Keine versteckten Rechte

- Keine `collection`, keine `uses`-Beschränkung, keine
  Royalties (`sellerFeeBasisPoints: 0`).
- Das Token ist ein Standard-SPL-Asset: jeder Wallet-Besitzer kann
  es zu jeder Wallet transferieren. Es gibt keine Sperr-,
  Blacklist- oder Gebührenlogik im Programmcodes (SPL Token
  Program ist quelloffen und auditgetestet; Token-2022
  Extensionen sind NICHT aktiviert).

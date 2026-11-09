# SuperIntelNex

Repository für den Community-Token **SuperIntelNex** (`superintelnex.com`).

## Struktur

| Ordner | Zweck |
|---|---|
| `site/` | Landingpage (statistisch: `index.html` mit Inline-CSS/JS). Netlify-Publish-Verzeichnis. |
| `token/` | Coin-Arbeit: Skripte, Konfiguration, Metadaten, Tests und Doku (Solana/SPL). |

### Sensible Inhalte (gitignored, niemals committen)

- `token/wallets/` — EINWEG-Test-Wallets (base58-Keys)
- `token/result/` — lokale Ergebnis-Protokolle

Die Website wird über Netlify deployet (Publish-Verzeichnis `site/`).
Der `token/`-Ordner wird dadurch nie veröffentlicht.

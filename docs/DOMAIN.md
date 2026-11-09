# Domain: superintelnex.com — GitHub Pages + Checkdomain

Stand: 08.11.2026 · Repository: `predatorhwg-commits/superintelnex` (öffentlich, Branch `main`)
Hosting: GitHub Pages (Legacy-Build), Quelle: `main` · CNAME: `superintelnex.com`

## Warum GitHub Pages, öffentlich

GitHub Pages ist im Free-Plan nur für **öffentliche** Repositories verfügbar.
Das Repository enthält nur statische Website-Inhalte (HTML/CSS/JS, keine
Secrets). Deshalb wurde es öffentlich geschaltet. Kein kostenpflichtiger
Dienst wird benötigt.

## Ist-Zustand DNS (dokumentiert vor den Änderungen)

| Zone | NS | Einträge |
|---|---|---|
| Registry (wirksam) | `ns1.registrant-verification.com`, `ns2.registrant-verification.com` | A `superintelnex.com` = 212.123.41.108 (Parking); Wildcard: alle Subdomains (u. a. `www`, `mail`, `smtp`, `imap`, `pop`, `mx`) auf 212.123.41.108; kein MX, kein TXT |
| Checkdomain-Zone (bereit, delegiert noch nicht) | `ns.checkdomain.de`, `ns2.checkdomain.de` | A `superintelnex.com` = 130.185.109.77, A `www.superintelnex.com` = 130.185.109.77, MX `superintelnex.com` → `superintelnex.com` (Priority 10), AAAA `2a01:4a0:2002:4:1da9:a99f:5423:3cf1` |

Wichtig: E-Mail-Einträge gibt es in der Zone heute **keine** (kein MX/TXT wirksam).
Die MX-Eintrag in der Checkdomain-Zone und die bestehenden A-Record (130.185.109.77)
bleiben in der Checkdomain-Zone erhalten — nur die unten genannten Felder ändern wir.

## Ziel-Zustand (Checkdomain)

### 1. Nameserver auf Checkdomain umstellen (einmalig)

Die Registry-Zone (`registrant-verification.com`) überschreibt jede Subdomain
per Wildcard mit einer Parking-IP — einzelne DNS-Einträge sind dort nicht
verwaltbar. Notwendig ist daher der Wechsel auf die Checkdomain-Nameserver
(sie kennen die Domain bereits, keine Datenverluste):

- Domain-Eintrag bei Checkdomain: **Superintelnex.com**
- Nameserver 1: `ns.checkdomain.de`
- Nameserver 2: `ns2.checkdomain.de`

Pfad: checkdomain.net → Login → **Domains** → neben `superintelnex.com`
**Configuration** → **checkdomain nameserver** → beide Nameserver eintragen →
**Save**. Wirkung: ca. 2–6 Stunden, registrierungsseitig bis zu 24–48 Stunden.

### 2. DNS-Einträge (Sektion „DNS records" auf derselben Seite)

| Name | Type | Value |
|---|---|---|
| `superintelnex.com` (bzw. `@`/leer) | A | `185.199.108.153` |
| `superintelnex.com` (bzw. `@`/leer) | A | `185.199.109.153` |
| `superintelnex.com` (bzw. `@`/leer) | A | `185.199.110.153` |
| `superintelnex.com` (bzw. `@`/leer) | A | `185.199.111.153` |
| `www` | CNAME | `predatorhwg-commits.github.io` |

Vorher löschen (sonst bleibt 130.185.109.77 neben den neuen A-Records):
den vorhandenen A-Record `superintelnex.com` → `130.185.109.77` und, falls
als eigener Eintrag gepflegt, den A-Record `www` → `130.185.109.77`
(durch den CNAME ersetzen). `www` darf kein A-Record mehr haben.
Der MX-Eintrag bleibt unverändert.

Offizielle GitHub-Pages-Werte (A-Records) — Quelle:
docs.github.com „Managing a custom domain for your GitHub Pages site"
(Stand 08.11.2026).

### 3. Optional: Domain-Verifizierung bei GitHub (Empfehlung)

Profil → Einstellungen → **Pages** → **Add a domain** → `superintelnex.com`
→ TXT-Record anlegen (Wert zeigt GitHub im UI an, Format:
`_github-pages-challenge-predatorhwg-commits.superintelnex.com`):
| Name | Type | Value |
|---|---|---|
| `_github-pages-challenge-predatorhwg-commits` | TXT | (Wert aus dem GitHub-UI kopieren) |
Danach im UI „Continue verifying" / „Verify". Diese TXT bleibt dauerhaft stehen.

### 4. HTTPS (automatisch)

GitHub issued ein Let's-Encrypt-Zertifikat für `superintelnex.com` automatisch.
Sobald der DNS-Punkt zeigt: **Settings → Pages → Enforce HTTPS** aktivieren.

## Geleistete Schritte (08.11.2026)

- [x] Repository öffentlich geschaltet
- [x] `CNAME` (`superintelnex.com`) und `.nojekyll` per PR #1
- [x] Pages-Quelle: Branch `domain/github-pages` (Legacy-Build), Status: built
- [x] Edge testet die Domain bereits (Host: superintelnex.com liefert 200)
- [ ] DNS bei Checkdomain wie oben (Nameserver + 4×A + CNAME)
- [ ] HTTPS erzwingen, sobald DNS live ist

## Prüfung nach DNS-Änderung

```bash
dig +short A superintelnex.com            # 185.199.108/109/110/111.153
dig +short CNAME www.superintelnex.com    # predatorhwg-commits.github.io.
curl -sI https://superintelnex.com/       # 200, Zertifikat superintelnex.com
curl -sI https://www.superintelnex.com/   # 301 -> https://superintelnex.com/
```

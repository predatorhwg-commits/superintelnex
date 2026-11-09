# DEPLOY-ABNAHME — superintelnex.com auf den aktuellen `main` stellen

**Stand 09.11.2026 12:15 · Status: BLOKIERT durch externe Schritte (Netlify/DNS — kein Agent-Job)**

## Befund (geprüft via curl/dig, reprozierbar)

| Probe | Ergebnis | Bedeutung |
|---|---|---|
| `https://superintelnex.com` | **HTTP 200 — aber ALTER englischer Stand** (3 Szenen, EN-OG-Text „Community token project in development", SVG-Icon `superintelnex-sn-anthrazit.svg`, der nicht im Repo existiert) | Domain zeigt einen **alten Netlify-Deploy**, nicht den aktuellen `site/` |
| `https://gleaming-meerkat-935538.netlify.app/` | **HTTP 404** (Netlify-Default „Site not found"-Seite) | Die gemeldete Netlify-Subdomain hat **keinen gültigen Deploy** — Subdomain umbenennen/gelöscht oder nie aktiv |
| `superintelnex.com` DNS | A: `75.2.60.5`, NS: `registrant-verification.com` (Register-Spark/NS, nicht Checkdomain-ALIAS) | Domain-NS liegen beim Registrar; ein **ALIAS/CNAME** (oder A) zeigt auf den alten Netlify-Deploy |
| `main` @ GitHub | `1795c7c` (gepusht, lokal == origin) | Repo-Seite ist fertig, alles QA-grün |

**Kurzfassung:** Das Release ist im Repo fertig und grün — aber die Live-Domain
zeigt noch einen voralten Stand, weil (a) die Netlify-Subdomain `gleaming-meerkat-935538`
offensichtlich nicht (mehr) existiert und (b) die Domain-Namensauflösung noch auf den
alten Deploy zeigt.

## ZIP-Abnahme (Kurzweg, geprüft 12:25)

`sni-deploy.zip` (Repo-Root, untracked, erzeugt 12:16) ist **byte-identisch mit
`site/` @ `75d71e5`** verifiziert (diff aller 5 Dateien: index.html inkl.
Test-Hebel `__sinxPointer`, impressum.html, datenschutz.html, 404.html,
og-image.png). Damit gilt: Unabhängig von den Netlify-Reconnect-Schritten
(unten) kann das ZIP sofort per **Netlify-Dashboard → „Drag & Drop" (manueller
Deploy)** hochgeladen werden — der Abnahme-Check (Schritt 3) lässt sich danach
schon auf der Subdomain testen. Das ZIP ist **deploy-fertig**, kein Rebuild,
kein erneutes Packen nötig. (Empfohlen bleibt: Schritt 1–2 (Repo-Connect +
DNS), damit zukünftige Pushes automatisch deployen.)

## Was zu tun ist (User/CEO, <5 min pro Schritt)

### Schritt 1 — Netlify klären (Dashboard, Login)
1. Netlify → Sites: welche Site heißt `gleaming-meerkat-935538`? Ist sie existierend
   (dann: welcher Stand ist deployed?) oder weg (umbenannt/gelöscht)?
2. Falls weg: **Neue Site anlegen (oder umbenannte finden)**, Repository
   `predatorhwg-commits/superintelnex` verbinden, Publish-Verzeichnis `site/`,
   **kein Build-Schritt** (statik). Deploy aus `main` → neuer Deploy-Link.
3. Falls vorhanden: Deploy neu auslösen (Button „Deploy" bzw. Auto-Deploy auf Push).

### Schritt 2 — DNS/Checkdomain
1. In der Netlify-Site: Custom Domain → `superintelnex.com` anlegen (Netlify gibt
   ALIAS/DNS-Werte vor: `https://<site>.netlify.app`).
2. Checkdomain-Panel: bei `superintelnex.com` ALIAS (bzw. A) auf den Netlify-Wert
   setzen — den alten Registrar/`registrant-verification.com`-Eintrag ersetzen.
   (DNS-Konfiguration darf nur dort erfolgen, wo die Zone verwaltet wird — bei
   Registrant-verification-NS das Checkdomain-Panel.)
3. Wartezeit: A-Record-TTL (typisch 5–30 min) bzw. CNAME-Propagation.

### Schritt 3 — Abnahme (copy-paste-fertig)
```bash
# 1) Live-Domain zeigt den NEUEN Stand (Deutsch, 4 Szenen, TITLES-Map):
curl -s https://superintelnex.com/ | grep -c 'class="scene"'      # Erwartet: 4
curl -s https://superintelnex.com/ | grep -o "SuperIntelNex | Community-Token-Projekt im Aufbau" | head -1
curl -s https://superintelnex.com/ | grep -c "superintelnex-sn-anthrazit" # Erwartet: 0 (altes SVG weg)

# 2) OG-Image erreichbar:
curl -s -o /dev/null -w "%{http_code}\n" https://superintelnex.com/og-image.png  # 200

# 3) Rechtstexten + Footer-Hinweis:
curl -s https://superintelnex.com/impressum.html | grep -c "PLATZHALTER — wird ergänzt"  # ≥1 (Betreiberdaten offen)
curl -s https://superintelnex.com/ | grep -c "keine Anlageberatung"  # ≥1

# 4) Finale Gate-Abnahme (lokal, identisch mit Release-Gate):
cd /Users/haqmal/Desktop/Projekte/SuperIntelNex
bash agenten/checks/run-gate.sh .   # exit 0 erwartet
```

### Schritt 4 — danach (einmalig)
- Platzhalter-Austausch, sobald Betreiberdaten vorliegen (`agenten/BETREIBERDATEN-ABLAGE.md`),
  danach ein Push + Abnahme-Check wiederholen (Step 3).

## Warum nicht ein Agent
Netlify-Login/DNS-Panels sind **externe Konten** (User-Gebiet) — kein
Agent hat dafür Zugriff. Dieses Dokument macht die Schritte für den User
kopierlauffähig; das Team wartet auf „Abnahme-Kennzeichen" (Step 3 grün).

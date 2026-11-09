# SuperIntelNex — Agenten-Team (5 Agenten + CEO)

5 parallele Agenten arbeiten an der Website `superintelnex.com`.
Dieser Ordner enthält für jeden Agenten **seinen vollständigen Prompt**
(fertig zum Einfügen, z. B. in ChatGPT/Codex, Cursor, OpenCode …).

## Das System (kurz)

```
agent-design.md        1. Design & Grafik      → site/index.html (optik), site/og-image (neu)
agent-engineering.md   2. Engineering & JS     → site/index.html (script), neue site/*.html (js/seo)
agent-content.md       3. Content & Redaktion  → site/*.html (nur Texte/Labels)
agent-recht.md         4. Recht & Compliance   → site/impressum.html, site/datenschutz.html, site/risikohinweis-Texte
agent-qa.md            5. QA & Release-Gate    → agenten/checks/ (test-Skripte), keine Site-Änderungen
ceo-coordinator.md     6. CEO                  → koordiniert, meldet Konflikt, macht Pushes
```

## Golden Rules (gilt für ALLE Agenten — steht in jedem Prompt)

1. **Eine Datei = ein Owner.** Kein Agent rührt eine Datei an, die einem anderen Agenten gehört (Tabelle oben). CEO meldet jedes Überschneidungsproblem.
2. **Keine erfundenen Fakten.** Finanzprojekt: nichts Erfinden (keine Partner, keine Kurses, keine Team, keine Registry, keine Adresse). Fehlende Angaben = `PLATZHALTER`-Block (gestrichelte Box, Design-Vokabular).
3. **Keine Secrets.** `token/wallets/`, `token/result/` NIE anfassen, NIE committen. Keine API-Keys/Keys in Datein.
4. **Single-File-Disziplin.** Die Site bleibt statisches HTML mit Inline-CSS/JS (kein Build, kein npm). Neue Seiten: gleiche Design-Sprache (schwarz, Mono-Eyebrow `letter-spacing:.21em`, `.details`-Grid, `#edge:clamp(20px,5vw,84px)`).
5. **Netlify-Publish = `site/`.** `token/` wird niemals publiziert (`netlify.toml`).
6. **Rechtstext-Regeln** (aus altem Issue): Impressums-Betreiberangaben NUR als sichtbar markierte Platzhalter; Datenschutz NUR für tatsächlich eingesetzte Dienste (aktuell: keine Cookies, kein Tracking, keine Fonts, kein Formular; Hosting = Netlify/USA; 1 ausgehender Link = Solana-Devnet-Explorer).
7. **Risikohinweis immer sichtbar:** „Projekt im Aufbau, keine Anlageberatung" bleibt im Footer; Risikohinweis-Block in der Status-Szene; Devnet-Testtoken = „kein echtes Geld".
8. **Vor jedem Push: QA-Gate grün** (siehe `agent-qa.md` — Headless: 0 JS-Fehler, 0 tote Links, 0 Overflow @390px, Secret-Scan).
9. **Berge & Merges macht nur der CEO** (pro Agent einen Git-Worktree). Agenten arbeiten in ihrem Worktree, committen sauber, berichten fertig → CEO meldet Konflikt.
10. **Bericht:** Jeder Agent schreibt nach jeder Arbeitsrunde nach `agenten/berichte/<agenten-name>-YYYY-MM-DD-HHMM.md` (kurz: Was fertig, was offen, welche Entscheidungen, welche Dateien).

## Arbeitsablauf (5 Std.)

```
0:00  CEO teilt Worktrees aus, gibt jedem Agenten seinen Prompt (siehe Datei)
0:15  Alle 5 Agenten starten parallel in ihren Worktrees
1:30  Erste Berichte fällig → CEO Check: Konflikt? → klären oder Reihenfolge ändern
3:00  CEO Merge-Phase 1: Design + Engineering + Content (Kerne-Änderungen)
3:30  CEO Merge-Phase 2: Recht + QA-Skripte
4:30  QA-Gate auf dem finalen Merge (CEO startet Headless-Tests)
5:00  Push nach QA-green, Netlify auto-deploys, CEO schreibt Final-Bericht
```

## Start-Befehl (CEO, einmalig)

```bash
cd /Users/haqmal/Desktop/Projekte/SuperIntelNex
for a in design engineering content recht qa; do
  git worktree add -b agenten/$a "agenten/worktree-$a" main
done
# Jeder Agent arbeitet in agenten/worktree-<name>
# CEO meldet:  git merge agenten/<name>  (pro Phase, Konflikt = CEO)
# Cleanup:      git worktree remove agenten/worktree-<name>
```

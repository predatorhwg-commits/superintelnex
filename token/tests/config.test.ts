// Offline-Test: Konfigurationsdatei ist gultig und intern konsistent.
// Aufruf (npm-Import laedt web3.js, dessen ws-Abhaengigkeit den
// Umgebungsvariablen-Zugriff fuer WS_NO_BUFFER_UTIL prueft -> --allow-env):
//   cd SuperIntelNex && deno test --allow-read --allow-env token/tests/config.test.ts
import { loadConfig } from "../scripts/lib/common.ts";

Deno.test("config/token.json laesst sich laden und hat Pflichtfelder", () => {
  const cfg = loadConfig();
  const t = cfg.token;
  if (typeof t.name !== "string" || t.name.length === 0) throw new Error("name fehlt");
  if (!/^[A-Z0-9]{2,10}$/.test(t.symbol)) throw new Error("symbol ungueltig: " + t.symbol);
  if (!Number.isInteger(t.decimals) || t.decimals < 0 || t.decimals > 9) {
    throw new Error("decimals ungueltig: " + t.decimals);
  }
  if (typeof t.totalSupply !== "number" || t.totalSupply <= 0) throw new Error("totalSupply fehlt");
  // Netzwerke vorhanden
  const nets = cfg.networks;
  if (!nets[nets.default]) throw new Error("default-Netz nicht definiert");
  // Metadata-URI muss https sein (keine lokalen Pfade)
  const md = cfg.metadata as { uri: string; image: string; sellerFeeBasisPoints: number; isMutable: boolean };
  if (!/^https:\/\//.test(md.uri)) throw new Error("metadata.uri muss https sein: " + md.uri);
  if (!/^https:\/\//.test(md.image)) throw new Error("metadata.image muss https sein: " + md.image);
  if (typeof md.isMutable !== "boolean") throw new Error("metadata.isMutable muss boolean sein");
  if (md.sellerFeeBasisPoints !== 0) throw new Error("Keine verborgenen Gebuehren: sellerFeeBasisPoints muss 0 sein");
});

Deno.test("Verteilung (Vorschlag) addiert sich zu 100 %", () => {
  const cfg = loadConfig();
  const sum = Object.values(cfg.token.distribution).reduce((a, b) => a + b, 0);
  if (Math.abs(sum - 1) > 1e-9) throw new Error("Verteilung addiert sich nicht zu 1: " + sum);
});

Deno.test("authorities-Block ist eindeutig (beide boolean)", () => {
  const cfg = loadConfig();
  const a = cfg.authorities as { revokeMintAuthority?: unknown; revokeFreezeAuthority?: unknown };
  if (typeof a.revokeMintAuthority !== "boolean") throw new Error("revokeMintAuthority muss boolean sein");
  if (typeof a.revokeFreezeAuthority !== "boolean") throw new Error("revokeFreezeAuthority muss boolean sein");
});

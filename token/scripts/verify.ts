// Verifikation: Mint-Parameter, Supply, Decimals, Vollmachten, Metadaten.
// Aufruf: deno run --allow-all token/scripts/verify.ts
// Netz: SIN_NETWORK (Standard: localnet) / SIN_RPC optional.
// Erwartet token/result/MINT-ADDRESS.txt (erzeugt von create-mint.ts).
// Beendet sich mit Code 0 (alles OK) oder 1 (Abweichung).
import { PublicKey } from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { loadConfig, conn, networkLabel, metadataPda, parseMetadataAccount } from "./lib/common.ts";

const cfg = loadConfig();
const c = conn();
const label = networkLabel();
const out = JSON.parse(Deno.readTextFileSync(new URL("../result/MINT-ADDRESS.txt", import.meta.url)));
const mint = new PublicKey(out.mint);

let ok = true;
function check(name: string, expect: string, actual: string) {
  const pass = expect === actual;
  ok = ok && pass;
  console.log((pass ? "  OK   " : "  FAIL ") + name + " = " + actual + (pass ? "" : "  (erwartet: " + expect + ")"));
}
function info(name: string, actual: string) {
  console.log("  info  " + name + " = " + actual);
}

console.log("=== Verifikation [" + label + "]  Mint " + mint.toBase58() + " ===");
const m = await token.getMint(c, mint);
check("decimals", String(cfg.token.decimals), String(m.decimals));
check("totalSupply (smallest units)",
  (BigInt(cfg.token.totalSupply) * 10n ** BigInt(cfg.token.decimals)).toString(),
  m.supply.toString());
info("mintAuthority", m.mintAuthority?.toBase58() ?? "(keine — entzogen)");
info("freezeAuthority", m.freezeAuthority?.toBase58() ?? "(keine — entzogen)");

// On-Chain-Metadaten aus dem Metaplex-Metadaten-PDA lesen.
// Layout: key(1) updateAuthority(32) mint(32), danach drei laenge-
// praefixierte Slots (name/symbol/uri) — siehe parseMetadataAccount
// in lib/common.ts (empirisch gegen den lokalen Devnet-Clone geprueft).
const meta = metadataPda(mint);
const [metaAcct] = await c.getMultipleAccountsInfo([meta]);
if (!metaAcct || metaAcct.data.length === 0) {
  console.log("  WARN  kein Metaplex-Metadaten-Account fuer diesen Mint gefunden");
  ok = false;
} else {
  const parsed = parseMetadataAccount(metaAcct.data);
  check("on-chain metadata name", cfg.token.name, parsed.name);
  check("on-chain metadata symbol", cfg.token.symbol, parsed.symbol);
  check("on-chain metadata uri", (cfg.metadata as { uri?: string }).uri ?? "", parsed.uri);
}

console.log(ok ? "=== ALLE PRUEFUNGEN OK ===" : "=== ABWEICHUNGEN GEFUNDEN ===");
Deno.exit(ok ? 0 : 1);

// Initial-Emission: mintet die Gesamtmenge an die ATA der Admin-Test-Wallet.
// Aufruf: deno run --allow-all token/scripts/mint-initial.ts
// Netz: SIN_NETWORK (Standard: localnet) / SIN_RPC optional.
// Erwartet token/result/MINT-ADDRESS.txt (erzeugt von create-mint.ts).
//
// ACHTUNG: Die Verteilung (community/founder/dev/liquidity) ist NOCH nicht
// implementiert und darf erst nach Bestaetigung der Aufteilung erfolgen.
// Dieses Skript mintet aktuell die GESAMTMENGE an eine EINWEG-Test-Wallet.
// Es ist kein Distributions- oder Verkaufs-Skript.
import { PublicKey, Transaction } from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { loadConfig, conn, getWallet, sendTx, journal, networkLabel } from "./lib/common.ts";

const cfg = loadConfig();
const c = conn();
const label = networkLabel();

const resDir = new URL("../result/", import.meta.url);
const out = JSON.parse(Deno.readTextFileSync(new URL("MINT-ADDRESS.txt", resDir)));
if ((out.netz ?? "") !== label) {
  console.log("WARNUNG: MINT-ADDRESS.txt gehoert zu Netz '" + (out.netz ?? "?") + "', Lauf erfolgt auf " + label + ".");
}
const mintPub = new PublicKey(out.mint);
const admin = await getWallet("main");
const ata = await token.getAssociatedTokenAddress(mintPub, admin.publicKey);

// Gesamtmenge in smallest units: totalSupply * 10^decimals
const raw = (BigInt(cfg.token.totalSupply) * 10n ** BigInt(cfg.token.decimals)).toString();
console.log("Minten von", cfg.token.totalSupply, cfg.token.symbol,
  "(= " + raw + " smallest units) an ATA " + ata.toBase58());

const t = new Transaction().add(
  token.createMintToInstruction(mintPub, ata, admin.publicKey, BigInt(raw), []),
);
const sig = await sendTx(c, t, [admin]);
console.log("Emissions-Signatur:", sig);
journal("mint-initial", { signature: sig, details: { mint: out.mint, amount: raw } });

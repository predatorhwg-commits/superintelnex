// Uebertragt eine SIN-Menge von der Admin-ATA an die Empfaenger-Test-Wallet
// (token/wallets/recipient.json, einweg). Menge per Umgebungsvariable
// SIN_TRANSFER_SIN (Standard: 1000000). Aufruf:
//   SIN_NETWORK=devnet deno run --allow-all token/scripts/transfer-to-holder.ts
// MUESSBEFORE revoke-authorities laufen: danach ist main.json gesperrt
// (archiviert) und koennen keine Transaktionen mehr signiert werden.
import { PublicKey, Transaction } from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { loadConfig, conn, getWallet, sendTx, journal, networkLabel } from "./lib/common.ts";

const cfg = loadConfig();
const c = conn();
const label = networkLabel();

const out = JSON.parse(Deno.readTextFileSync(new URL("../result/MINT-ADDRESS.txt", import.meta.url)));
if ((out.netz ?? "") !== label) {
  console.log("WARNUNG: MINT-ADDRESS.txt gehoert zu Netz '" + (out.netz ?? "?") + "', Lauf erfolgt auf " + label + ".");
}
const mint = new PublicKey(out.mint);
const admin = await getWallet("main");
const holder = await getWallet("recipient");

const srcAta = await token.getAssociatedTokenAddress(mint, admin.publicKey);
const dstAta = await token.getAssociatedTokenAddress(mint, holder.publicKey);

const sin = Deno.env.get("SIN_TRANSFER_SIN") ?? "1000000";
const amt = BigInt(sin) * 10n ** BigInt(cfg.token.decimals);

console.log("Ueberweise " + sin + " " + cfg.token.symbol + " (=" + amt + " smallest units)");
console.log("von Admin-ATA " + srcAta.toBase58());
console.log("nach Holder-ATA " + dstAta.toBase58());

const t = new Transaction().add(
  token.createTransferCheckedInstruction(srcAta, mint, dstAta, admin.publicKey, amt, cfg.token.decimals, []),
);
const sig = await sendTx(c, t, [admin]);
console.log("Transfer-Signatur:", sig);
journal("transfer-to-holder", { signature: sig, details: { mint: out.mint, amount: amt.toString(), holder: holder.publicKey.toBase58() } });

const acc = await token.getAccount(c, dstAta);
console.log("Holder-Saldo: " + (Number(acc.amount) / 10 ** cfg.token.decimals).toString() + " " + cfg.token.symbol);
console.log("OK — Transfer laeuft On-Chain durch. [" + label + "]");

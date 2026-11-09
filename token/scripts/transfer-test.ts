// Transfer-Test: legt die ATA des Empfangers an und ueberweist per
// Checked-Transfer (Decimals-geprueft) 1.234 SIN an eine frische Test-Wallet.
// Aufruf: deno run --allow-all token/scripts/transfer-test.ts
// Netz: SIN_NETWORK (Standard: localnet) / SIN_RPC optional.
// Erwartet token/result/MINT-ADDRESS.txt.
import { PublicKey, Transaction, LAMPORTS_PER_SOL } from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { loadConfig, conn, getWallet, sendTx, journal, networkLabel, confirmSignature } from "./lib/common.ts";

const cfg = loadConfig();
const c = conn();
const label = networkLabel();

const out = JSON.parse(Deno.readTextFileSync(new URL("../result/MINT-ADDRESS.txt", import.meta.url)));
if ((out.netz ?? "") !== label) {
  console.log("WARNUNG: MINT-ADDRESS.txt gehoert zu Netz '" + (out.netz ?? "?") + "', Lauf erfolgt auf " + label + ".");
}
const mint = new PublicKey(out.mint);
const admin = await getWallet("main");
const recipient = await getWallet("recipient");

// Auf dem lokalen Netz muessen beide Wallets SOL haben (ATA-Setup zahlt Admin)
if (label === "LOCALNET-TEST") {
  const bal = await c.getBalance(recipient.publicKey);
  if (bal < 0.05 * LAMPORTS_PER_SOL) {
    const sig = await c.requestAirdrop(recipient.publicKey, 0.5 * LAMPORTS_PER_SOL);
    await confirmSignature(c, sig);
    console.log("Airdrop fuer recipient:", sig);
  }
}

const srcAta = await token.getAssociatedTokenAddress(mint, admin.publicKey);
const dstAta = await token.getAssociatedTokenAddress(mint, recipient.publicKey);

// 1) ATA des Empfangers idempotent anlegen (Admin zahlt die Transaktion)
const t1 = new Transaction().add(
  token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, dstAta, recipient.publicKey, mint),
);
const sig1 = await sendTx(c, t1, [admin]);
console.log("ATA-Recipient:", dstAta.toBase58(), "sig:", sig1);

// 2) Checked-Transfer von 1.234 SIN — prueft im Programm die Decimals.
//    1.234 = 1234/1000; in smallest units: 1234 * 10^decimals / 1000
//    (100 Billion Gesamtmenge bei 5 Dezimalstellen => 123400, nicht 1234000000)
const amt = 1234n * 10n ** BigInt(cfg.token.decimals) / 1000n;
const t2 = new Transaction().add(
  token.createTransferCheckedInstruction(srcAta, mint, dstAta, admin.publicKey, amt, cfg.token.decimals, []),
);
const sig2 = await sendTx(c, t2, [admin]);
console.log("Transfer 1.234 " + cfg.token.symbol + " sig:", sig2);

// 3) Saldo-Gegenprobe
const a = await token.getAccount(c, srcAta);
const b = await token.getAccount(c, dstAta);
console.log("Saldo Admin:    " + (Number(a.amount) / 10 ** cfg.token.decimals).toString() + " " + cfg.token.symbol);
console.log("Saldo Recipient " + (Number(b.amount) / 10 ** cfg.token.decimals).toString() + " " + cfg.token.symbol);
if (b.amount !== amt) throw new Error("Unerwarteter Recipient-Saldo: " + b.amount + " (erwartet " + amt + ")");

journal("transfer-test", { signature: sig2, details: { mint: out.mint, amount: amt.toString() } });
console.log("OK — Checked-Transfer laeuft ohne Decimals-Fehler.");

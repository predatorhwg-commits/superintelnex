// Devnet-Vorbereitung OHNE Transaktion: zeigt die einweg-Admin-Test-Wallet
// (Pubkey + Test-SOL-Saldo) und die exakte Befehlsfolge zum Devnet-Lauf.
//
// Aufruf:  deno run --allow-read --allow-write --allow-net token/scripts/devnet-prefund.ts
//          (netz: SIN_NETWORK, Standard localnet; fuer die Devnet-Finanzierung: SIN_NETWORK=devnet)
//
// Es wird NICHTS signiert und NICHTS an eine Chain gesendet — nur eine
// Leseabfrage (getBalance). Die Wallet ist eine EINWEG-Test-Wallet
// (token/wallets/main.json, gitignoriert), niemals das Tresor-Wallet.
import { LAMPORTS_PER_SOL } from "npm:@solana/web3.js@1.98.4";
import { loadConfig, conn, getWallet, networkLabel } from "./lib/common.ts";

const cfg = loadConfig();
const label = networkLabel();
console.log("=== Devnet-Prefund [" + label + "] — keine Transaktion, nur Leseabfrage ===");

// 1) Admin-Test-Wallet wiederverwenden bzw. erzeugen (gitignoriert).
const admin = await getWallet("main");
const pubkey = admin.publicKey.toBase58();
console.log("Admin-Test-Wallet (einweg, gitignoriert):", pubkey);

// 2) Saldo lesen (read-only RPC).
let lamports = 0;
try {
  lamports = await conn().getBalance(admin.publicKey);
} catch (e) {
  console.log("(Saldo-Abfrage fehlgeschlagen: " + String(e) + ")");
}
const haveSOL = lamports / LAMPORTS_PER_SOL;
const needed = 0.5;
console.log("Test-SOL-Saldo: " + haveSOL.toFixed(6) + " SOL" + (haveSOL >= needed ? " (reicht)" : " (erforderlich: " + needed + " SOL)"));

// 3) Finanzierung — nur wenn der Saldo nicht reicht.
if (haveSOL < needed) {
  const net = (Deno.env.get("SIN_NETWORK") ?? cfg.networks.default);
  if (net === "devnet") {
    console.log("");
    console.log("Finanzierung der Devnet-Wallet (drei Wege, einer reicht):");
    console.log("  A) Manuell im Browser: https://faucet.solana.com/ — Pubkey hierher kopieren:");
    console.log("       " + pubkey);
    console.log("     (CAPTCHA wird in diesem Projekt nicht umgangen; ~0.5 Test-SOL anfordern.)");
    console.log("  B) Agave-CLI mit einem RPC, das Airdrops aktiviert (z. B. QuickNode-Devnet-URL):");
    console.log("       SIN_RPC=https://<ihr-rpc> solana airdrop " + needed + " " + pubkey);
    console.log("  C) Test-SOL von einer eigenen Devnet-Wallet per Transfer senden:");
    console.log("       solana transfer " + pubkey + " " + needed);
  } else {
    console.log("(Localnet: kein Finanzierungsbedarf — das Erzeugungs-Skript loest den Airdrop automatisch aus.)");
  }
}

// 4) Die Befehlsfolge, die danach laeuft (siehe DEVNET-RUNBOOK.md, Abschnitt 3).
console.log("");
console.log("Danach, jede Zeile einzeln, im Projektordner:");
const net = (Deno.env.get("SIN_NETWORK") ?? cfg.networks.default);
const env = "SIN_NETWORK=" + net + " ";
console.log("  " + env + "deno test  --allow-read --allow-env token/tests/config.test.ts   # offline-Check");
console.log("  " + env + "deno run --allow-all token/scripts/create-mint.ts        # Mint + Metadaten (1 Tx)");
console.log("  " + env + "deno run --allow-all token/scripts/mint-initial.ts       # Emission der Gesamtmenge");
console.log("  " + env + "deno run --allow-all token/scripts/transfer-test.ts      # Checked-Transfer 1.234");
console.log("  " + env + "deno run --allow-all token/scripts/verify.ts             # On-Chain-Abgleich");
console.log("  " + env + "deno run --allow-all token/scripts/revoke-authorities.ts # NUR nach Bestaetigung (einweg!)");
console.log("");
console.log("Ergebnis-Protokoll: token/result/MINT-ADDRESS.txt + EXECUTED-TRANSACTIONS.jsonl");
console.log("Label: DEVNET-TESTTOKEN — kein Mainnet, kein Realgeld.");

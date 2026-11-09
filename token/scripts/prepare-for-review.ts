// Prueft lokal die Vollmaechtigkeit des Pruefwegs: erstellt auf localnet
// ein Test-Mint (Decimals=2), mintet 1000, brennt 1, friert/thaut den ATA
// und transferiert 0.01 an eine frische Wallet. Die Signaturen werden fuer
// die Wallet-Inspektion ueber die Agave-CLI vorbereitet. NUR lokal.
// Aufruf: deno run --allow-all token/scripts/prepare-for-review.ts
// Netz: SIN_NETWORK=localnet (Standard) — jeder andere Netzabschluss wird
// abgelehnt, damit versehentlich kein Devnet-Mint erzeugt wird.
import {
  Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL,
} from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { conn, getWallet, sendTx, journal, networkLabel, confirmSignature } from "./lib/common.ts";

const label = networkLabel();
if (label !== "LOCALNET-TEST") {
  console.log("ABGELEHNT: prepare-for-review.ts darf nur auf localnet laufen (SIN_NETWORK=localnet).");
  Deno.exit(1);
}
const c = conn();

// 1) Frische Admin-Test-Wallet + Airdrop
const admin = await getWallet("main", { regenerate: true });
const a1 = await c.requestAirdrop(admin.publicKey, 2 * LAMPORTS_PER_SOL);
await confirmSignature(c, a1);
console.log("1) localnet-Airdrop an Admin-Test-Wallet " + admin.publicKey.toBase58() + " sig:", a1);

// 2) Lokales Test-Mint (Decimals=2, kleine Zahlen)
const testMint = Keypair.generate();
const t1 = new Transaction().add(
  SystemProgram.createAccount({
    fromPubkey: admin.publicKey,
    newAccountPubkey: testMint.publicKey,
    lamports: await c.getMinimumBalanceForRentExemption(token.MINT_SIZE),
    space: token.MINT_SIZE,
    programId: token.TOKEN_PROGRAM_ID,
  }),
  token.createInitializeMintInstruction(testMint.publicKey, 2, admin.publicKey, admin.publicKey),
);
const s1 = await sendTx(c, t1, [admin, testMint]);
console.log("2) lokales Test-Mint:", testMint.publicKey.toBase58(), "sig:", s1);

// 3) ATA + 1000.00 minten
const ata = await token.getAssociatedTokenAddress(testMint.publicKey, admin.publicKey);
const t2 = new Transaction().add(
  token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, ata, admin.publicKey, testMint.publicKey),
  token.createMintToInstruction(testMint.publicKey, ata, admin.publicKey, 100000n, []),
);
const s2 = await sendTx(c, t2, [admin]);
console.log("3) ATA + 1000.00 minten sig:", s2);

// 4) Burn 1.00 (Supply sinkt; Mint-Verhindern ist via Vollmacht, nicht via Programm)
const t3 = new Transaction().add(
  token.createBurnInstruction(ata, testMint.publicKey, admin.publicKey, 100n, []),
);
const s3 = await sendTx(c, t3, [admin]);
console.log("4) Burn 1.00 sig:", s3);

// 5) Freeze/Thaw — belegt, dass Konten gesperrt/entsperrt werden koennen
const t4 = new Transaction().add(
  token.createFreezeAccountInstruction(ata, testMint.publicKey, admin.publicKey, []),
);
const s4 = await sendTx(c, t4, [admin]);
console.log("5) Freeze-Test sig:", s4);
const t4b = new Transaction().add(
  token.createThawAccountInstruction(ata, testMint.publicKey, admin.publicKey, []),
);
const s4b = await sendTx(c, t4b, [admin]);
console.log("   Thaw-Test sig:", s4b);

// 6) Checked-Transfer 0.01 an frische Wallet (Decimals-Pruefung)
const dst = await getWallet("review-dst");
const bal = await c.getBalance(dst.publicKey);
if (bal < 0.05 * LAMPORTS_PER_SOL) {
  const a = await c.requestAirdrop(dst.publicKey, 0.5 * LAMPORTS_PER_SOL);
  await confirmSignature(c, a);
}
const dstAta = await token.getAssociatedTokenAddress(testMint.publicKey, dst.publicKey);
const t5 = new Transaction().add(
  token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, dstAta, dst.publicKey, testMint.publicKey),
  token.createTransferCheckedInstruction(ata, testMint.publicKey, dstAta, admin.publicKey, 1n, 2, []),
);
const s5 = await sendTx(c, t5, [admin]);
console.log("6) Transfer-Test 0.01 sig:", s5);

// 7) Abschluss-Zustand
const m = await token.getMint(c, testMint.publicKey);
console.log("7) Mint-Zustand: supply=" + m.supply.toString() +
  " mintAuthority=" + m.mintAuthority?.toBase58() +
  " freezeAuthority=" + m.freezeAuthority?.toBase58());
journal("prepare-for-review", { signature: s3, details: {
  testMint: testMint.publicKey.toBase58(),
  sigs: [s1, s2, s3, s4, s4b, s5],
} });
console.log("OK — alle Pruef-Transaktionen lokal durchlaufen.");

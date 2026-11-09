// Erzeugt den Mint + Metaplex-Metadaten auf dem gewaehlten Netzwerk.
// Aufruf: deno run --allow-all token/scripts/create-mint.ts
// Netz: Umgebungsvariable SIN_NETWORK (localnet=Standard | devnet),
//       optional SIN_RPC fuer einen eigenen RPC-Endpunkt.
//
// Das Skript erzeugt EINWEG-Test-Wallets (token/wallets/main.json,
// token/wallets/mint.json, gitignoriert) und uebernimmt Mint- und
// Freeze-Vollmacht. Das sind NIE die Haupt-/Tresor-Wallets des Betreibers.
// Fuer Devnet muss die Admin-Wallet vorab ueber einen Faucet mit
// Test-SOL finanziert werden (siehe token/docs/DEVNET-RUNBOOK.md).
import {
  SystemProgram, Transaction, LAMPORTS_PER_SOL,
} from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { createCreateMetadataAccountV3Instruction } from "npm:@metaplex-foundation/mpl-token-metadata@2.5.2";
import { loadConfig, conn, getWallet, sendTx, journal, metadataPda, networkLabel, confirmSignature } from "./lib/common.ts";

const cfg = loadConfig();
const c = conn();
const label = networkLabel();

// 1) Waehlen oder wiederverwenden der einweg Test-Wallet
const admin = await getWallet("main");

// 2) SOL vorhanden?
const bal = await c.getBalance(admin.publicKey);
console.log("[" + label + "] Admin-Test-Wallet:", admin.publicKey.toBase58(), "SOL:", bal / LAMPORTS_PER_SOL);
if (label !== "LOCALNET-TEST") {
  if (bal < 0.5 * LAMPORTS_PER_SOL) {
    console.log("Zu wenig Test-SOL. Bitte Wallet ueber einen Faucet finanzieren (DEVNET-RUNBOOK.md).");
    Deno.exit(1);
  }
} else {
  const sig = await c.requestAirdrop(admin.publicKey, 2 * LAMPORTS_PER_SOL);
  console.log("Localnet-Airdrop gesendet:", sig);
  await confirmSignature(c, sig);
}

// Schutz: Bei vorhandenem Ergebnis-Protokoll nicht blind neu erzeugen
const resDir = new URL("../result/", import.meta.url);
try {
  if (Deno.statSync(new URL("MINT-ADDRESS.txt", resDir)).isFile) {
    console.log("result/MINT-ADDRESS.txt existiert bereits:");
    console.log(Deno.readTextFileSync(new URL("MINT-ADDRESS.txt", resDir)));
    if (Deno.env.get("SIN_FORCE") !== "1") {
      console.log("ABBRUCH: Fuer Neu-Anlage SIN_FORCE=1 setzen und das alte Protokoll verschieben.");
      Deno.exit(1);
    }
  }
} catch {
  // kein Ergebnis-Protokoll, weiter
}

// 3) Mint-Key-Paar erzeugen (wird in token/wallets/mint.json abgelegt,
//    gitignoriert — EINWEG-Test-Artifact, nicht das Tresor-Wallet)
const mint = await getWallet("mint", { regenerate: true });
const ata = await token.getAssociatedTokenAddress(mint.publicKey, admin.publicKey);

// 4) Mietpreis des Mint-Accounts ermitteln (ATA wird in derselben Transaktion
//    idempotent angelegt, ihr Rent-Preis laedt das Programm zur Laeuftzeit)
const mintRent = await c.getMinimumBalanceForRentExemption(token.MINT_SIZE);
console.log("Mint-Rent:", mintRent);

// 5) Mint-Account anlegen + initialisieren + ATA + Metaplex-Metadaten
const meta = metadataPda(mint.publicKey);
const md = cfg.metadata as { uri: string; image: string; sellerFeeBasisPoints: number; isMutable: boolean };

const t = new Transaction();
t.add(
  SystemProgram.createAccount({
    fromPubkey: admin.publicKey,
    newAccountPubkey: mint.publicKey,
    lamports: mintRent,
    space: token.MINT_SIZE,
    programId: token.TOKEN_PROGRAM_ID,
  }),
  token.createInitializeMintInstruction(mint.publicKey, cfg.token.decimals, admin.publicKey, admin.publicKey),
  token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, ata, admin.publicKey, mint.publicKey),
  createCreateMetadataAccountV3Instruction(
    {
      metadata: meta,
      mint: mint.publicKey,
      mintAuthority: admin.publicKey,
      payer: admin.publicKey,
      updateAuthority: admin.publicKey,
    },
    {
      createMetadataAccountArgsV3: {
        data: {
          name: cfg.token.name,
          symbol: cfg.token.symbol,
          uri: md.uri,
          sellerFeeBasisPoints: md.sellerFeeBasisPoints,
          creators: [{ address: admin.publicKey, verified: true, share: 100 }],
          collection: null,
          uses: null,
        },
        isMutable: md.isMutable,
        collectionDetails: null,
      },
    },
  ),
);

const sig = await sendTx(c, t, [admin, mint]);
console.log("Erstellt:", sig);

// 6) Ergebnis protokollieren (result/ ist gitignoriert, kein Geheimnis,
//    aber kein Website-Inhalt)
const out = {
  netz: label,
  mint: mint.publicKey.toBase58(),
  ataAdmin: ata.toBase58(),
  metadataPda: meta.toBase58(),
  mintAuthority: admin.publicKey.toBase58(),
  freezeAuthority: admin.publicKey.toBase58(),
  signature: sig,
  // Korrektes Explorer-Format: mainnet-Pfad + Cluster-Query-Parameter
  explorerMint: "https://explorer.solana.com/address/" + mint.publicKey.toBase58()
    + (label === "DEVNET-TESTTOKEN" ? "?cluster=devnet" : ""),
};
try { Deno.mkdirSync(resDir, { recursive: true }); } catch { /* existiert */ }
Deno.writeTextFileSync(new URL("MINT-ADDRESS.txt", resDir), JSON.stringify(out, null, 2) + "\n");
journal("create-mint", { signature: sig, details: out });
console.log("Protokoll geschrieben: token/result/MINT-ADDRESS.txt");

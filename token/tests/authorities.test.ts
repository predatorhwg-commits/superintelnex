// Vollmachts-Test (optin, nur wenn ein Test-Validator erreichbar ist):
// Belegt auf localnet die EINWEG-Entscheidung aus config/token.json
// (authorities.revokeMintAuthority / revokeFreezeAuthority = true):
//   1) Mint mit beidenden Vollmachten anlegen
//   2) Mint-Vollmacht entziehen (SetAuthority MintTokens -> null)
//      -> afterwards: getMint.mintAuthority === null UND ein Mint-Versuch fehlschlaegt
//   3) Freeze-Vollmacht entziehen (SetAuthority FreezeAccount -> null)
//      -> afterwards: getMint.freezeAuthority === null UND ein Freeze-Versuch fehlschlaegt
//
// Aufruf:  deno test --allow-all token/tests/authorities.test.ts
// Validator: siehe token/docs/DEVNET-RUNBOOK.md (solana-test-validator,
// mit --clone-upgradeable-program fuer Metaplex TM; hier wird nur das
// SPL-Token-Programm gebraucht, der Clone kostet nichts).
import {
  Keypair, SystemProgram, Transaction, LAMPORTS_PER_SOL,
} from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { conn, loadConfig, getWallet, sendTx, confirmSignature, rpcUrl } from "../scripts/lib/common.ts";

async function reachable(): Promise<boolean> {
  const c = conn();
  try { const bh = await c.getLatestBlockhash(); return !!bh.blockhash; } catch { return false; }
}
const isReachable = await reachable();

Deno.test({
  name: "authorities: Mint-/Freeze-Vollmacht entziehen (irreversibel) auf LOCALNET",
  ignore: !isReachable
    ? "Kein erreichbarer Test-Validator auf " + rpcUrl() +
      " — Vollmachts-Test uebersprungen (Validator laut DEVNET-RUNBOOK.md starten)."
    : undefined,
  fn: async () => {
    const c = conn();
    const cfg = loadConfig();
    const auths = cfg.authorities as { revokeMintAuthority?: boolean; revokeFreezeAuthority?: boolean };

    // Testvoraussetzung: der Konfig-Wert muss true sein (sonst ist der
    // Test obsolet, weil die Konfiguration die Entzuellung nicht vorsieht).
    if (auths.revokeMintAuthority !== true || auths.revokeFreezeAuthority !== true) {
      throw new Error("Konfig authorities revidieren? Test erwartet beides = true (aktuell: " +
        JSON.stringify(auths) + ")");
    }

    // Frische einweg Test-Wallet + Airdrop
    const admin = await getWallet("test-admin", { regenerate: true });
    const s0 = await c.requestAirdrop(admin.publicKey, 2 * LAMPORTS_PER_SOL);
    await confirmSignature(c, s0);

    // Mint mit 2 Dezimalstellen + ATA + 1000.00 emittieren
    const mint = Keypair.generate();
    const ata = await token.getAssociatedTokenAddress(mint.publicKey, admin.publicKey);
    const t1 = new Transaction().add(
      SystemProgram.createAccount({
        fromPubkey: admin.publicKey,
        newAccountPubkey: mint.publicKey,
        lamports: await c.getMinimumBalanceForRentExemption(token.MINT_SIZE),
        space: token.MINT_SIZE,
        programId: token.TOKEN_PROGRAM_ID,
      }),
      token.createInitializeMintInstruction(mint.publicKey, 2, admin.publicKey, admin.publicKey),
      token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, ata, admin.publicKey, mint.publicKey),
      token.createMintToInstruction(mint.publicKey, ata, admin.publicKey, 100000n, []),
    );
    const s1 = await sendTx(c, t1, [admin, mint]);
    console.log("  Test-Mint:", mint.publicKey.toBase58(), "sig:", s1);

    // Ausgangszustand: beide Vollmachten aktiv
    let m = await token.getMint(c, mint.publicKey);
    if (m.mintAuthority?.toBase58() !== admin.publicKey.toBase58()) throw new Error("Mint-Vollmacht vor Entzug erwartet: " + String(m.mintAuthority));
    if (m.freezeAuthority?.toBase58() !== admin.publicKey.toBase58()) throw new Error("Freeze-Vollmacht vor Entzug erwartet: " + String(m.freezeAuthority));

    // 1) Freeze-Vollmacht entziehen -> Freeze muss danach fehlschlagen
    const s2 = await sendTx(c, new Transaction().add(
      token.createSetAuthorityInstruction(mint.publicKey, admin.publicKey, token.AuthorityType.FreezeAccount, null, []),
    ), [admin]);
    m = await token.getMint(c, mint.publicKey);
    if (m.freezeAuthority !== null) throw new Error("Freeze-Vollmacht nach SetAuthority nicht null");
    console.log("  Freeze-Vollmacht entzogen, sig:", s2);
    let freezeFailed = false;
    try {
      await sendTx(c, new Transaction().add(
        token.createFreezeAccountInstruction(ata, mint.publicKey, admin.publicKey, []),
      ), [admin]);
    } catch { freezeFailed = true; }
    if (!freezeFailed) throw new Error("Freeze nach Entzug der Vollmacht sollte ABGEHNOERT werden");
    console.log("  OK: Freeze-Transaktion nach Entzug wird abgelehnt");

    // 2) Mint-Vollmacht entziehen -> MintTo muss danach fehlschlagen
    const s3 = await sendTx(c, new Transaction().add(
      token.createSetAuthorityInstruction(mint.publicKey, admin.publicKey, token.AuthorityType.MintTokens, null, []),
    ), [admin]);
    m = await token.getMint(c, mint.publicKey);
    if (m.mintAuthority !== null) throw new Error("Mint-Vollmacht nach SetAuthority nicht null");
    console.log("  Mint-Vollmacht entzogen, sig:", s3);
    let mintFailed = false;
    try {
      await sendTx(c, new Transaction().add(
        token.createMintToInstruction(mint.publicKey, ata, admin.publicKey, 1n, []),
      ), [admin]);
    } catch { mintFailed = true; }
    if (!mintFailed) throw new Error("MintTo nach Entzug der Vollmacht sollte ABGELEHNT werden");
    console.log("  OK: Emissions-Transaktion nach Entzug wird abgelehnt");

    // 3) Supply bleibt exakt auf 1000.00 (keine unentdeckte Erhohung)
    m = await token.getMint(c, mint.publicKey);
    if (m.supply !== 100000n) throw new Error("Supply-Fehlwert nach Vollmachts-Test: " + m.supply.toString());
    console.log("  OK: supply fixiert bei 1000.00, beide Vollmachten = (none)");
  },
  sanitizeOps: true,
  sanitizeResources: false,
} as Deno.TestDefinition);

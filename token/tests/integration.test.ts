// Integrationstest (optin, nur wenn ein Test-Validator erreichbar ist):
// Erzeugt ein Test-Mint mit 2 Dezimalstellen, mintet 1234.57, transferiert
// 0.5 und prueft Decimals/Supply/Saldos/On-Chain-Metadaten. Laeuft gegen
// den in config/token.json definierten Default (localnet 127.0.0.1:8011).
// Ohne erreichbare Localnet wird der Test sauber uebersprungen (skip).
//
// Aufruf: cd SuperIntelNex && deno test --allow-all token/tests
// Validator starten (siehe token/docs/DEVNET-RUNBOOK.md):
//   solana-test-validator --reset --quiet --bind-address 127.0.0.1 \
//     --rpc-port 8011 --faucet-port 8012 --ledger ~/.sln-local/ledger \
//     --url devnet \
//     --clone-upgradeable-program metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s
import {
  Keypair, SystemProgram, Transaction, LAMPORTS_PER_SOL,
} from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { createCreateMetadataAccountV3Instruction } from "npm:@metaplex-foundation/mpl-token-metadata@2.5.2";
import { conn, loadConfig, getWallet, sendTx, metadataPda, confirmSignature, rpcUrl, parseMetadataAccount } from "../scripts/lib/common.ts";

// Erreichbarkeit ohne die (in dieser Version untypisierte) getHealth-Methode:
// getLatestBlockhash ist ein minimaler, stabiler Health-Check.
async function reachable(): Promise<boolean> {
  const c = conn();
  try {
    const bh = await c.getLatestBlockhash();
    return !!bh.blockhash;
  } catch {
    return false;
  }
}

// Erreichbarkeit wird einmalig beim Modul-Import geprueft (Top-Level-Await),
// damit der Test bei fehlender Localnet sauber ignoriert wird, nicht fehlschlaegt.
const isReachable = await reachable();

Deno.test({
  name: "integration: Token-Lebenszyklus lokal (LOCALNET-TEST)",
  ignore: !isReachable
    ? "Kein erreichbarer Test-Validator auf " + rpcUrl() +
      " — Integrationstest uebersprungen (Validator laut DEVNET-RUNBOOK.md starten)."
    : undefined,
  fn: async () => {
    const c = conn();
    const admin = await getWallet("test-admin", { regenerate: true });
    const recipient = Keypair.generate();
    const s1 = await c.requestAirdrop(admin.publicKey, 2 * LAMPORTS_PER_SOL);
    await confirmSignature(c, s1);
    const s2 = await c.requestAirdrop(recipient.publicKey, 0.5 * LAMPORTS_PER_SOL);
    await confirmSignature(c, s2);

    // Test-Mint mit 2 Dezimalstellen (kleine Zahlen, lokaler Lauf)
    const cfg = loadConfig();
    const mint = Keypair.generate();
    const decimals = 2;
    const ataA = await token.getAssociatedTokenAddress(mint.publicKey, admin.publicKey);
    const ataR = await token.getAssociatedTokenAddress(mint.publicKey, recipient.publicKey);
    const meta = metadataPda(mint.publicKey);
    const md = cfg.metadata as { uri: string; sellerFeeBasisPoints: number; isMutable: boolean };

    // Zwei getrennte Transaktionen (entsprechend dem bewaehrten Smoke-Verfahren):
    // 1) Mint-Konto + Initialisierung, 2) ATAs + Metadaten. So vermeidet
    // der Lauf die "Missing signature"-Kollision ueber die Metadaten-Instruktion.
    const t1a = new Transaction().add(
      SystemProgram.createAccount({
        fromPubkey: admin.publicKey,
        newAccountPubkey: mint.publicKey,
        lamports: await c.getMinimumBalanceForRentExemption(token.MINT_SIZE),
        space: token.MINT_SIZE,
        programId: token.TOKEN_PROGRAM_ID,
      }),
      token.createInitializeMintInstruction(mint.publicKey, decimals, admin.publicKey, admin.publicKey),
    );
    const sigMint = await sendTx(c, t1a, [admin, mint]);
    console.log("  Test-Mint:", mint.publicKey.toBase58(), "sig:", sigMint);

    // Der in-memory-Recipient signiert die Transaktion nicht; er kann also
    // kein Payer sein. Der Admin zahlt den ATA-Rent-Preis fuer beide Konten
    // (Payer und Owner koennen getrennt sein).
    const t1b = new Transaction().add(
      token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, ataA, admin.publicKey, mint.publicKey),
      token.createAssociatedTokenAccountIdempotentInstruction(admin.publicKey, ataR, recipient.publicKey, mint.publicKey),
      createCreateMetadataAccountV3Instruction(
        { metadata: meta, mint: mint.publicKey, mintAuthority: admin.publicKey,
          payer: admin.publicKey, updateAuthority: admin.publicKey },
        {
          createMetadataAccountArgsV3: {
            data: {
              name: cfg.token.name + " (Integrationstest)",
              symbol: "TST",
              uri: md.uri,
              sellerFeeBasisPoints: 0,
              creators: [{ address: admin.publicKey, verified: true, share: 100 }],
              collection: null,
              uses: null,
            },
            isMutable: false,
            collectionDetails: null,
          },
        },
      ),
    );
    const sigMeta = await sendTx(c, t1b, [admin]);
    void sigMeta;

    // Emission: 1234.57 (dezimalgeprueft via Checked-Transfer)
    const t2 = new Transaction().add(
      token.createMintToInstruction(mint.publicKey, ataA, admin.publicKey, 123457n, []),
    );
    const sigEmission = await sendTx(c, t2, [admin]);

    // Transfer: 0.50
    const t3 = new Transaction().add(
      token.createTransferCheckedInstruction(ataA, mint.publicKey, ataR, admin.publicKey, 50n, decimals, []),
    );
    const sigTransfer = await sendTx(c, t3, [admin]);

    // Gegenpruefung
    const m = await token.getMint(c, mint.publicKey);
    if (m.decimals !== decimals) throw new Error("decimals-Fehlwert: " + m.decimals);
    if (m.supply !== 123457n) throw new Error("Supply-Fehlwert: " + m.supply);
    const accA = await token.getAccount(c, ataA);
    const accR = await token.getAccount(c, ataR);
    if (accA.amount !== 123407n) throw new Error("Admin-Saldo falsch: " + accA.amount);
    if (accR.amount !== 50n) throw new Error("Recipient-Saldo falsch: " + accR.amount);

    // On-Chain-Metadaten: Name lesbar (Layout-Parser in lib/common.ts)
    const [metaAcct] = await c.getMultipleAccountsInfo([meta]);
    if (!metaAcct) throw new Error("Kein Metadaten-Account fuer Test-Mint");
    const onchainName = parseMetadataAccount(metaAcct.data).name;
    if (!onchainName.includes("Integrationstest")) {
      throw new Error("On-Chain-Metadaten-Name unerwartet: " + JSON.stringify(onchainName));
    }
    console.log("  OK: Emission/Transfer/Decimals/Metadaten");
  },
  sanitizeOps: true,
  sanitizeResources: false,
} as Deno.TestDefinition);

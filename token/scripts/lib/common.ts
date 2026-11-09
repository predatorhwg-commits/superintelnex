// Gemeinsame Hilfsfunktionen fuer alle Erzeugungs-Skripte.
// Lauefbar mit: deno run --allow-all
import {
  Connection, Keypair, PublicKey, Transaction,
} from "npm:@solana/web3.js@1.98.4";
import * as token from "npm:@solana/spl-token@0.4.15";
import { PROGRAM_ID as TM_PROGRAM_ID } from "npm:@metaplex-foundation/mpl-token-metadata@2.5.2";

// ---------- Konfiguration ----------

export interface TokenConfig {
  networks: Record<string, string> & { default: string };
  token: {
    name: string;
    symbol: string;
    decimals: number;
    totalSupply: number;
    supplyPolicy: string;
    distribution: Record<string, number>;
  };
  authorities: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export function loadConfig(): TokenConfig {
  // common.ts liegt unter token/scripts/lib/ -> zwei Stufen bis token/
  const p = new URL("../../config/token.json", import.meta.url);
  const raw = JSON.parse(Deno.readTextFileSync(p));
  return raw as TokenConfig;
}

// ---------- Netzwerk / RPC ----------

// Netzwerk waehlbar per Umgebungsvariable SIN_NETWORK (localnet | devnet).
// RPC explizit ueberreitsehen per SIN_RPC.
export function rpcUrl(): string {
  const explicit = Deno.env.get("SIN_RPC");
  if (explicit) return explicit;
  const cfg = loadConfig();
  const net = Deno.env.get("SIN_NETWORK") ?? cfg.networks.default;
  const url = cfg.networks[net];
  if (!url) throw new Error("Unbekanntes Netz '" + net + "' (verfuegbar: " + Object.keys(cfg.networks).join(", ") + ")");
  return url;
}

export function networkLabel(): string {
  const explicit = Deno.env.get("SIN_RPC");
  if (explicit) return "CUSTOM-RPC: " + explicit;
  const cfg = loadConfig();
  const net = Deno.env.get("SIN_NETWORK") ?? cfg.networks.default;
  if (net === "localnet") return "LOCALNET-TEST";
  if (net === "devnet") return "DEVNET-TESTTOKEN";
  return net.toUpperCase();
}

export function conn(): Connection {
  // commitment=confirmed; Bestaetigung laeuft per RPC-Polling (keine
  // WebSocket-Abhaengigkeit, weil der lokale Validator nur HTTP+TCP-Ports oeffnet).
  return new Connection(rpcUrl(), "confirmed");
}

// ---------- Zufaellige Test-Wallets (nur fuer localnet/devnet-Tests) ----------

// Wallets liegen als JSON (base58-Seed-Array) unter token/wallets/
// und sind per .gitignore ausgeschlossen. Es handelt sich NIE um das
// Haupt- oder Tresor-Wallet des Betreibers.
export async function getWallet(name: string, opts: { regenerate?: boolean } = {}): Promise<Keypair> {
  const dir = new URL("../../wallets/", import.meta.url);
  try { await Deno.stat(dir); } catch { await Deno.mkdir(dir, { recursive: true }); }
  const f = new URL(name + ".json", dir);
  const keypath = f.pathname;
  if (opts.regenerate) {
    const kp = Keypair.generate();
    // 64-Byte-Array als JSON-Liste serialisieren (Uint8Array waere sonst
    // als Objekt mit Numerix-Indexen serialisiert)
    Deno.writeTextFileSync(keypath, JSON.stringify(Array.from(kp.secretKey)));
    console.log("  (Wallet '" + name + "' neu erzeugt: " + kp.publicKey.toBase58() + ")");
    return kp;
  }
  let existing = false;
  try {
    const st = Deno.statSync(keypath);
    existing = st.isFile;
  } catch {
    existing = false;
  }
  if (existing) {
    return Keypair.fromSecretKey(new Uint8Array(JSON.parse(Deno.readTextFileSync(keypath))));
  }
  const kp = Keypair.generate();
  Deno.writeTextFileSync(keypath, JSON.stringify(Array.from(kp.secretKey)));
  console.log("  (Wallet '" + name + "' erzeugt: " + kp.publicKey.toBase58() + ")");
  return kp;
}

// ---------- Transaktionsversand + Bestaetigung per RPC ----------

function sleep(ms: number) { return new Promise((r) => setTimeout(r, ms)); }

export async function confirmSignature(c: Connection, sig: string, timeoutMs = 60000): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const st = await c.getSignatureStatuses([sig]);
    const v = st.value[0];
    if (v) {
      if (v.err) throw new Error("On-Chain-Fehler in Transaktion " + sig + ": " + JSON.stringify(v.err));
      if (v.confirmationStatus === "confirmed" || v.confirmationStatus === "finalized") return;
    }
    await sleep(500);
  }
  throw new Error("Bestaetigung fuer " + sig + " nach " + timeoutMs + " ms nicht erreicht");
}

export async function sendTx(c: Connection, tx: Transaction, signers: Keypair[]): Promise<string> {
  if (!tx.recentBlockhash) {
    tx.recentBlockhash = (await c.getLatestBlockhash()).blockhash;
  }
  tx.sign(...signers);
  const sig = await c.sendRawTransaction(tx.serialize(), { skipPreflight: true });
  await confirmSignature(c, sig);
  return sig;
}

// ---------- Protokoll (fuer Nachweis: Mint, Signaturen, Labels) ----------

export interface ExecEntry {
  time: string;
  network: string;
  step: string;
  signature?: string;
  details?: Record<string, unknown>;
}

export function journal(step: string, entry: Partial<ExecEntry>) {
  const dir = new URL("../../result/", import.meta.url);
  const f = new URL("EXECUTED-TRANSACTIONS.jsonl", dir);
  try { Deno.statSync(dir); } catch { Deno.mkdirSync(dir, { recursive: true }); }
  const line = JSON.stringify({
    time: new Date().toISOString(),
    network: entry.network ?? networkLabel(),
    step,
    ...entry,
  }) + "\n";
  Deno.writeTextFileSync(f, line, { append: true });
}

// ---------- Metaplex-Token-Metadaten (PDA + Account-Parsing) ----------

// Metaplex TM v2 fuer SPL-Token (Program "metaqbxx..."):
// PDA-Seeds = ["metadata", program_id, mint]
export function metadataPda(mint: PublicKey): PublicKey {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("metadata"), TM_PROGRAM_ID.toBytes(), mint.toBytes()],
    TM_PROGRAM_ID,
  )[0];
}

// Sequenzieller Reader fuer den Metadaten-Account (empirisch in dieser
// Programmversion verifiziert): key(1) updateAuthority(32) mint(32),
// danach drei laenge-praefixierte Slots (u32 Kapazitaet + Fix-Byte):
//   name (Kapazitaet 32), symbol (Kapazitaet 10), uri (Kapazitaet 200)
// => erstes laenge-u32 bei Offset 65.
export function parseMetadataAccount(
  data: Uint8Array | Buffer,
): { name: string; symbol: string; uri: string } {
  const dec = new TextDecoder();
  const buf = new DataView(data.buffer, data.byteOffset, data.byteLength);
  let p = 1 + 32 + 32; // 65
  function readSlot(): string {
    const cap = buf.getUint32(p, true); // little-endian
    p += 4;
    const s = dec.decode(data.subarray(p, p + cap)).replace(/\u0000+$/, "");
    p += cap;
    return s;
  }
  return { name: readSlot(), symbol: readSlot(), uri: readSlot() };
}

// ---------- Basis-Konstanten ----------

export { token, TM_PROGRAM_ID };

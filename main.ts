// Writes the passport spread to /output/entry.png.
// The image is built by build-image.py and lives beside this file as
// entry.png; this program only copies it to the output directory.
// Copies the pre-built Meridia passport spread to /output/entry.png.
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
const src = join(here, "entry.png");
let size: number;
try {
  size = statSync(src).size;
} catch {
  throw new Error(`entry.png missing: ${src}`);
}
if (size > 1048576) {
  throw new Error(`entry.png too large: ${size} bytes (max 1048576)`);
}
const bytes = readFileSync(src);
if (bytes.length !== size) {
  throw new Error(`entry.png changed while reading: ${src}`);
}
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));

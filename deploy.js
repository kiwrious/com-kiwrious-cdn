// deploy.js
import { execSync } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const repoUrl = "https://github.com/stakco/stakco.github.io.git"; // GitHub Pages repo
const branch = "gh-pages";
const subDir = "kiwrious/cdn"; // where to copy inside gh-pages
const sourceDir = path.join(__dirname, "lib"); // your static folder
const tempDir = path.join(__dirname, "gh-pages");

try {
  console.log("🚀 Starting deployment...");

  // Clean up old clone if exists
  if (fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }

  // Shallow + sparse clone only the gh-pages branch
  execSync(
    `git clone --depth 1 --filter=blob:none --sparse --branch ${branch} ${repoUrl} ${tempDir}`,
    { stdio: "inherit" }
  );

  // Move into repo
  process.chdir(tempDir);

  // Checkout only the target subDir
  execSync(`git sparse-checkout set ${subDir}`, { stdio: "inherit" });

  // Ensure target subdir exists (if first deploy)
  const targetPath = path.join(tempDir, subDir);
  fs.mkdirSync(targetPath, { recursive: true });

  // Copy files from dist -> gh-pages/itiles-web-bluetooth
  fs.cpSync(sourceDir, targetPath, { recursive: true });

  // Commit + push
  execSync("git add .", { stdio: "inherit" });

  try {
    execSync(`git commit -m "Deploy lib to ${subDir}"`, { stdio: "inherit" });
  } catch (e) {
    console.log("No changes to commit");
  }

  execSync(`git push origin ${branch}`, { stdio: "inherit" });

  // Clean up temp clone
  process.chdir(__dirname);
  fs.rmSync(tempDir, { recursive: true, force: true });

  console.log("✅ Deployment completed successfully!");
  console.log(`📦 Files available at: https://stakco.github.io/${subDir}/`);
} catch (err) {
  console.error("❌ Deployment failed:", err);
  process.exit(1);
}
#!/usr/bin/env node
/**
 * Upload the working tree to a GitHub repo via the Contents API, one commit
 * per file. This is the fallback transport when git push cannot reach
 * github.com (network layer resets the smart-HTTP route) but api.github.com
 * stays reachable through Node's TLS stack.
 *
 * Usage:
 *   node tools/upload_via_api.mjs <repo-dir> <owner> <repo> <token> [branch]
 *   node tools/upload_via_api.mjs <repo-dir> <owner> <repo> <token> [branch] --dry-run
 *
 * Walk is pinned to `git ls-files` so only committed, non-ignored files
 * (the exact repository content) are uploaded.
 */
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

const [, , repoDir, owner, repo, token, branchArg, dryRunArg] = process.argv;
const branch = branchArg && !branchArg.startsWith('--') ? branchArg : 'main';
const dryRun = dryRunArg === '--dry-run';

if (!repoDir || !owner || !repo || !token) {
  console.error('usage: node tools/upload_via_api.mjs <repo-dir> <owner> <repo> <token> [branch] [--dry-run]');
  process.exit(2);
}

// 1. exact committed file list
// git already emits forward slashes; Node reads them fine on Windows too
const files = execFileSync('git', ['ls-files'], { cwd: repoDir, encoding: 'utf8' })
  .split('\n')
  .filter(Boolean);

const api = 'https://api.github.com';
const headers = {
  Authorization: `Bearer ${token}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'luxun-skill-upload',
  'Content-Type': 'application/json',
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function gh(method, route, body) {
  const res = await fetch(`${api}${route}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = {}; }
  return { status: res.status, data, text };
}

(async () => {
  // confirm repo + default branch
  const info = await gh('GET', `/repos/${owner}/${repo}`);
  if (info.status !== 200) {
    console.error(`repo check failed ${info.status}: ${info.data.message || info.text}`);
    process.exit(1);
  }
  const defaultBranch = info.data.default_branch || branch;
  console.log(`repo ${owner}/${repo} ok (default_branch=${defaultBranch})`);

  const enc = (rel) => rel.split('/').map(encodeURIComponent).join('/');

  let uploaded = 0;
  let skipped = 0;
  let failed = 0;

  for (const file of files) {
    const rel = file;
    const content = readFileSync(path.join(repoDir, file));
    const base64 = content.toString('base64');
    const sha = createHash('sha1').update(`blob ${content.length}\u0000`).update(content).digest('hex');

    // 2. does the file already exist with same content?
    const existing = await gh('GET', `/repos/${owner}/${repo}/contents/${enc(rel)}?ref=${defaultBranch}`);
    if (existing.status === 200 && existing.data && existing.data.sha === sha) {
      skipped += 1;
      continue;
    }

    if (dryRun) {
      console.log(`DRY  would write ${rel} (${content.length} bytes)`);
      uploaded += 1;
      continue;
    }

    const commitMsg = `distill: ${rel} — luxun-skill（鲁迅表达风格 Skill，dot-skill 引擎六维蒸馏）`;
    const body = {
      message: commitMsg,
      content: base64,
      branch: defaultBranch,
    };
    if (existing.status === 200) {
      body.sha = existing.data.sha; // update path
    }

    let ok = false;
    for (let attempt = 1; attempt <= 4; attempt += 1) {
      const result = await gh('PUT', `/repos/${owner}/${repo}/contents/${enc(rel)}`, body);
      if (result.status === 200 || result.status === 201) {
        ok = true;
        break;
      }
      if (result.status === 409 || result.status === 422) {
        // stale sha or conflict -> re-read and retry once
        const again = await gh('GET', `/repos/${owner}/${repo}/contents/${enc(rel)}?ref=${defaultBranch}`);
        if (again.status === 200 && again.data?.sha) body.sha = again.data.sha;
        await sleep(600 * attempt);
        continue;
      }
      console.error(`FAIL ${rel}: ${result.status} ${result.data.message || result.text}`);
      failed += 1;
      ok = true; // stop retrying this file
      break;
    }
    if (!ok) {
      console.error(`FAIL ${rel}: retries exhausted`);
      failed += 1;
      continue;
    }
    uploaded += 1;
    if (uploaded % 10 === 0) console.log(`... ${uploaded} files`);
    await sleep(120);
  }

  console.log(`DONE uploaded=${uploaded} skipped=${skipped} failed=${failed}`);
  process.exit(failed > 0 && !dryRun ? 1 : 0);
})();
#!/usr/bin/env node
/**
 * Minimal GitHub REST helper used by tools/publish.py.
 *
 * Node's OpenSSL TLS stack reaches api.github.com reliably, whereas Python's
 * TLS 1.2-only handshake is frequently reset by the network layer on this
 * machine. publish.py delegates every REST call to this script.
 *
 * Usage:
 *   node tools/gh_api.mjs METHOD PATH TOKEN [BODY_JSON]
 * Output: one JSON line: {"status": <http-status>, "payload": <object>}
 */
const [method, path, token, bodyJson] = process.argv.slice(2);

if (!method || !path || !token) {
  console.error('usage: node tools/gh_api.mjs METHOD PATH TOKEN [BODY_JSON]');
  process.exit(2);
}

const res = await fetch('https://api.github.com' + path, {
  method,
  headers: {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github+json',
    'User-Agent': 'luxun-skill-publish',
    'Content-Type': bodyJson ? 'application/json' : 'text/plain',
  },
  body: bodyJson || undefined,
});

const text = await res.text();
let payload = {};
try {
  payload = text ? JSON.parse(text) : {};
} catch {
  payload = {};
}
console.log(JSON.stringify({ status: res.status, payload }));
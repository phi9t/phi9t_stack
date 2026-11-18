# Provenance

The core packages were rewritten for this repository. Their methods draw on
prior engineering practice, Lauren Tan's public engineering essays and the
pstack source. They are not an installation of Cursor's plugin. The separately vendored `phi9t-pstack` package below is
the exception: it ships upstream pstack skill files as released.

- Vendored upstream pstack: `93b916d4a1e806507e22f4716b352fa91f2b227e`, version
  0.15.43, https://github.com/cursor/plugins/tree/93b916d4a1e806507e22f4716b352fa91f2b227e/pstack

Upstream pstack is MIT licensed. The relevant notice is retained below. 

## Vendored skill trees

`phi9t-pstack` (poteto-mode, its sibling skills and principles, and the
poteto-agent definition) and `phi9t-pocock` (Matt Pocock's `engineering` and
`productivity` skills) carry unmodified upstream bytes at the commits pinned in
`vendor.json`, apart from the listed patches. `scripts/vendor.py sync` imports a
checkout and records file hashes; `scripts/vendor.py check` runs in
`./scripts/verify.sh` and refuses edited vendored files. To update, sync from a
newer upstream checkout, review the diff, bump the pin and release.
Each package keeps its upstream MIT notice in `LICENSE`. The frozen `misc`,
`deprecated` and `in-progress` Pocock buckets are not vendored, and Pocock's `tdd`
is dropped in favor of pstack's so each skill name appears once. The router
`SKILL.md` in each package is this repository's own and maps Cursor-specific
runtime terms to Codex and TRAE CLI.

## Upstream pstack notice

MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# GE × unchanged board-world108: offline passive-channel policy proposal

This experiment produces inspectable provenance and narrow channel metadata;
it does not admit RF, publish a native candidate, change regulatory country/board
settings, scan, read a device, load credentials or modify frozen sources.

## Provenance checked

* Location is the owner's explicit statement that the physical Dell and monitor
  are in Georgia, preserved in `location.json`. Country `GE` is not inferred
  from the SSID, Mac or Yukabox location. No independent geolocation was done;
  moving Dell invalidates this location-specific proposal.
* Physical native52 evidence reports SERVICE_READY valid, board regdomain108
  (`0x6c`) and capability interval2312..2732 MHz. The exact decoded evidence
  hash is pinned and used only to narrow metadata, not to invent permission.
  Target/PCI identity in the artifact identifies the existing reviewed Dell
  target; the baseline evidence is not remote device attestation. A future
  physical integration must rebind the artifact to its actual current target,
  epoch/native/candidate and owner state before any RF publication.
* Pinned Linux commit `6b5a2b7d9bc156e505f09e698d85d6a1547c1206` identifies108 as
  `WORC_WORLD`, `NO_CTL/NO_CTL`, selecting `ath_world_regdom_67_68_6A_6C`.
  It is not Georgia. The GE country-table mapping is not substituted for108.
* Official wireless-regdb release **2026.09.03** was downloaded from kernel.org
  and pinned by archive hash. The release's detached `regulatory.db.p7s`
  cryptographically verifies against **only** Chen-Yu Tsai's `wens` certificate
  extracted from the pinned Linux source `net/wireless/certs/wens.hex`.
  The verifier uses OpenSSL CMS `-binary -nointern -certfile <pinned-cert>
  -noverify`: `-nointern` prevents adoption of an embedded arbitrary signer;
  the explicitly pinned certificate supplies signer identity. `-noverify`
  bypasses PKIX chain/time validation, **not** signature/content verification.
  This is the Linux-pinned-key trust model, not a general Web-PKI certificate
  validation claim. Trust in that Linux source rests on the reviewed pinned
  repository/HTTPS provenance; an independent Linux/tag/OpenPGP trust chain and
  archive `.tar.sign` validation were not established in this experiment.
* Every extracted release byte is compared with the pinned archive. Official
  `db2fw.py` rebuilds `db.txt` into a binary byte-identical to the verified signed
  `regulatory.db`. Thus the inspected text rules are bound to the actual signed
  binary, rather than merely downloaded alongside a signature. Altered database
  and altered detached signature are rejected in negative tests.

Signed binary SHA256:
`7e236caecd939c8ec98be4870bf30422f28ffef2565a38aaaa2d9ddabd0c2641`.
Linux signer DER SHA256/fingerprint:
`eeb049594eb3a83e50bfb6782e7fdf9e96fbd5c2954a0bbb0931cd55321d0bcf`.
Archive SHA256:
`b22e0901227b820cd1c280abe681a15b773a5103a5e10dc442e94ebb34cbf58d`.
Full source/reference hashes and trust-model limitations are in the generated
`policy-proposal.json` and secret-free verification log.

## Narrow intersection

Official parser of the authenticated/rebuilt database gives GE's 2.4GHz rule:
2402..2482 MHz, maximum bandwidth40 MHz, maximum EIRP20 dBm, no extra rule flags.
The board's unchanged Linux world profile has these 2.4GHz rules:

| Occupied interval | Max bandwidth | Max EIRP | Board restriction |
|---|---:|---:|---|
| 2402..2472 MHz | 40 MHz | 20 dBm | none |
| 2457..2482 MHz | 40 MHz | 20 dBm | NO_IR |

This first metadata profile permits only **20MHz passive legacy11G** candidate
rows centered2412..2472 MHz in5MHz steps (channels1..13), intersecting the full
occupied20MHz span with both reviewed rules and supplied hardware limits.
Channels12/13 retain board NO_IR even though GE's rule does not impose it.
All thirteen candidate rows request passive operation and forbid active probes;
absence of NO_IR on channels1..11 does not expand this profile into active scan.
No channel14, nonstandard frequency, 5/6/60GHz, DFS, HT40/80 or probe permission
is inferred. If the router is outside these candidate channels this first
profile will not find it; unsupported metadata must not be widened to compensate.

Channel metadata for the independent channel-wire serializer:

* frequency/centre1 in MHz; centre2=0; width20; legacy11G mode1; passive1.
* flags0 for channels1..11; flags2(NO_IR) for12/13; DISABLED/RADAR remain absent
  for these narrowly derived rows. Excluded channels produce no row, not an
  enabled default. Active probes remain forbidden for **all** rows.
* maximum power/regulatory power20 dBm (2000mBm); serializer's half-dBm wire
  fields become40 by exact multiplication, never an invented20mBm/40dBm limit.
* antenna-gain parameter0 reflects the source rule metadata/default, not a
  measured zero-gain antenna or proof of actual EIRP. Before any later transmit
  profile, antenna/conducted-power/firmware constraints must actually be handled.
  These numbers are ceilings in an offline passive metadata proposal, not a
  measured RF output or permission to transmit.

The actual ath10k firmware caveat about DFS active probing remains material to
future integration; this profile excludes DFS. Passive command flags alone
still do not independently prove an absence of emitted frames on the air.
No PDEV_SET_REGDOMAIN country/CTL field is fabricated here; retain existing
board-world108 and derive actual command fields separately from pinned firmware
and the reviewed native integration.

## Tests and artifact boundary

199278 pure-filter checks pass under ASAN/UBSAN on Yukabox: every16-bit frequency,
board-domain and country pair, width0..200 for each candidate, occupied-band
edge inclusions/exclusions, reversed/overflow bounds, null inputs and unchanged
output on failure. An independent official-db-parser/source oracle confirms the
GE and board-world rules used by the filter. Freestanding x86-64 COFF compiles.
The public report binds every filter/test/verifier/location source and log hash.
The pure C function validates metadata only; it does not verify signatures,
location truth, target identity or source digests. A caller must perform those
checks against the full reviewed artifact and current native admission boundary.

`policy-proposal.json` contains all thirteen **candidate** rows and explicitly
sets `rf_admission_granted=false`, `country_or_board_override=false`. It is useful
input for the channel-wire serializer, but source digests are structural links,
not authority by themselves. A later verifier must check signature/rebuild/
location/board/context bindings and the actual single-owner persistent-radio
lifecycle before admitting one passive RF trial. It must not flip the boolean
or copy the candidate array into a signed native packet without those checks.

No primary Georgian2.4GHz legal instrument was independently verified here;
the mature signed Linux database is the engineering ruleset reference, not a
claim that this experiment independently determined Georgian law. No user
approval flow, RF admission or physical result is supplied by this artifact.

Reproduce on Yukabox using `verify_policy.py --reference <pinned-reference>
--physical52 <exact-evidence> --clang <reviewed-clang> --output <ignored-runs>`.
Reference retrieval and verification take place in
`/home/yuka/rabbit-world/parallel-regulatory-v1`, outside other agents' snapshots.
No native binaries or reference binary databases are committed.

## Primary sources

* [Official release index](https://www.kernel.org/pub/software/network/wireless-regdb/)
  and [2026.09.03 archive](https://www.kernel.org/pub/software/network/wireless-regdb/wireless-regdb-2026.09.03.tar.xz).
* [Linux regulatory database format documentation](https://wireless.docs.kernel.org/en/latest/en/developers/regulatory/wireless-regdb.html)
  explains full occupied bandwidth, not just center-frequency fit.
* [Pinned ath regd.c](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/regd.c)
  and [regd_common.h](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/regd_common.h)
  supply the unchanged board-world intersection.
* [Pinned Linux wens certificate](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/net/wireless/certs/wens.hex)
  supplies the explicit signer trust anchor.

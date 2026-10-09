# Public owner pairing request builder

Exact public200-byte parent template RABPAIR1 v1/flags0, target32,epoch64,
sealedcode-set32,DellfullSPKI32,clientSPKI32,nonce32,issued/expires64. Only
clientSPKI placeholder changes. Caller supplies actual parent context plus
physically confirmed full Dell hash. Exact canonical P256 public DER only.
External admitted local signer produces64-byte owner Ed25519 signature; this
code never reads keys, signs, requests passwords, transmits BLE or asserts human
approval. Dell must independently validate and consume its actual challenge
once before ACTIVATE. No plaintext credentials or host-time authority.

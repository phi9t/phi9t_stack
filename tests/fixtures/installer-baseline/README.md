# Installer persistence baseline

These records were emitted by the actual installer at `d11da00`, whose installer
bytes match the implementation baseline `5775759`. The source is the ordinary
`StackTests` package fixture. `manifest-v2.json` contains the exact installed
manifest bytes. `transaction-v1.json` contains the first-install backup with
only its machine-specific `target` replaced by `<TARGET>`.

The tests substitute their resolved scratch target, then pass these records to
the real CLI. Keep their saved formats fixed during the internal model refactor.

# Purchases, payments and referral gifts

The administrator ledger belongs to Keyholder. Marzban remains authoritative for
service status, expiry, quota and selected inbounds. Recording a purchase, confirmed
payment or delivered gift does not change the panel. Use explicit `user update`
operations separately after reviewing the agreed terms.

The command examples below use the separate public `keyholder-admin` client.
Install/configure that client and a compatible server dispatcher first; the backend
package does not provide these shell commands.

## Record a purchase and payment

Run `keyholder help RESOURCE ACTION` for complete flags. Existing customer selectors
work: UUID, username, exact display name, phone or Telegram. Financial history uses
the customer UUID and survives panel remapping, revocation and token rotation.

```sh
keyholder purchase create alice --description '30 days / 20 GB' --amount 100000 --unit toman --quota-bytes 20000000000 --duration-days 30
keyholder payment create alice --amount 1000000 --receiving-account personal --reference BANK_REFERENCE
keyholder payment show PAYMENT_UUID
keyholder payment confirm PAYMENT_UUID --reason 'Verified in bank transaction history' --confirm
keyholder payment allocate PAYMENT_UUID --purchase-id PURCHASE_UUID --amount 1000000 --confirm
keyholder billing balances alice
```

Amounts are exact decimal text. The default currency is IRR (whole rial); explicit
`toman` input multiplies by ten. Purchases can also be priced in USDT (six decimal
places) or LTC (eight), but crypto receipt workflows and exchange-rate conversion
are deferred. Balances never combine currencies. Quota/duration describe the agreed
purchase; they are not copied from the panel or automatically enforced there.

Payments start pending. Verify funds in the bank before confirming. A screenshot
alone is not confirmation. Receiving-account aliases must consistently identify the
same account: references are unique within that alias among non-voided entries. An explicit void
allows a corrected replacement while retaining the original entry and audit.
Equal customer/account/amount/timestamp entries are flagged as possible duplicates,
not automatically rejected. No banking credentials or full card numbers are needed.

Partial payments and one payment covering several purchases are supported for the
same customer and currency. Outstanding purchases and unallocated confirmed funds
are reported separately. Cancel a purchase only after reversing its allocations.
Refunds require released allocations when the remaining funds would otherwise be
insufficient. `payment unallocate ALLOCATION_UUID`, `payment refund`, `payment void`
and `purchase cancel` require a reason and `--confirm`. Void reverses allocations;
it is an erroneous-entry correction, while refund records returned money.

Every financial mutation uses a persisted retry key. The CLI prints its generated
key before sending; save it and repeat `--key SAME_KEY` after an uncertain response.
Use identical explicit timestamps/options on retries. Never invent a new key until
you have inspected state. `/admin/billing/actions` and `billing actions` preserve
requests, reasons and original results. Confirmed records have no destructive edit
or delete operation; correct mistakes through reversals and replacement entries.

## Referrals and delivered gifts

```sh
keyholder referral create friend --referrer alice
keyholder referral list --customer alice --state eligible
keyholder gift create --referrer alice --description 'Delivered 10 GB' --referral-ids REFERRAL_1 REFERRAL_2 REFERRAL_3 --confirm
keyholder gift list --customer alice
```

One existing customer can recommend another once; self-referrals and cycles are
rejected. Eligibility starts with the first positive confirmed payment, including
payments recorded before attribution. Renewals add no credit. `--since` (inclusive)
and `--until` (exclusive) filter introduction timestamps with explicit timezones.
Select exactly the referrals covered by a gift. If three are considered now and two
arrive later, only the two remain eligible. Calendar boundaries do not reset state.

A full refund removes an unconsidered referral's eligibility. Previously delivered
gifts remain recorded and show changed qualification. `gift reverse GIFT_UUID
--reason ... --confirm` corrects the gift entry and releases its referrals; it does
not revoke a real-world gift or undo a panel change. Reversed gift history remains.

## Receipt images

```sh
keyholder receipt upload PAYMENT_UUID ./receipt.png
keyholder receipt list PAYMENT_UUID
keyholder receipt download RECEIPT_UUID --output ./private-receipt.png
keyholder receipt keep RECEIPT_UUID --reason 'Open dispute' --confirm
keyholder receipt release RECEIPT_UUID --reason 'Resolved' --confirm
```

The private management bot has `/billinghelp`. Ledger commands use the same resource
and action names with `key=value` options; mutations are previewed before `/confirm
CODE`. `/receipt upload PAYMENT_UUID` starts a five-minute image session. Send a
JPEG/PNG photo or document up to 5 MiB; a document preserves the original bytes.
Retrieve original images through the SSH CLI. Telegram retains its own chat copies;
B2 expiration does not delete them. The bot is administrator-only, not customer intake.

Images are optional, private and content-validated. SQL stores metadata and a hash,
not image bytes. Failed uploads do not lose payment records. Retry uncertain uploads
with the same key to reconcile an already-stored version. Downloads verify content
against its recorded checksum. Missing images do not alter account/payment state.

## Storage budgets and retention

Keep SQLite for this feature: its existing WAL and foreign keys are retained, and
financial writes are short serialized transactions. Image/network I/O does not hold
a database write transaction. PostgreSQL would require separate support for indexes,
backup, recovery and deployment; consider it for measured contention or replicas.

Defaults use decimal GB: 2 GB receipt bucket, 6 GB recovery bucket and 2 GB temporary
headroom under a 10 GB total. Backed-up receipt images count again in recovery;
restic deduplication is not assumed when admitting uploads. Other B2 storage must
be counted in `STORAGE_OTHER_BYTES`; these limits coordinate managed writers, not
unrelated clients. A provider spending cap is a separate safeguard.

Set `KEYHOLDER_STORAGE_ENABLED=true` and configure a dedicated private receipt
bucket with its own restricted S3 read/write/list/delete key and HTTPS endpoint.
Enable bucket versioning where required by the S3 provider; Backblaze B2 stores
versions natively. Never share the restic key or use a public bucket. Uploads request
AES256 encryption at rest. Keep secrets only on the foreign host and in protected
recovery material; object names/metadata contain opaque identities, not customer data.

Usage counts all stored versions, delete markers and unfinished upload parts.
Measurements expire after 24 hours by default. Reservations remain after uncertain
writes until a measured retry or explicit reconciliation proves what was stored.
A crashed receipt operation leaves `receipt-io` visible in `storage reservations`;
verify no operation is running before releasing it with a reason. Do not clear
reservations simply because an upload timed out.

Unprotected images expire at 180 days. Capacity cleanup may remove the oldest sooner,
but protects images younger than 30 days and images marked `keep`. Abandoned failed
uploads are eligible after one day. Payment/referral records and image tombstones
remain. Old encrypted backup copies expire with restic snapshots, not live images.

```sh
keyholder storage status
keyholder storage reconcile
keyholder storage cleanup
keyholder storage cleanup --pressure
# Review both previews before enabling automatic deletion or executing cleanup:
keyholder storage cleanup --execute --confirm
```

Explicit cleanup executes only on the configured receipt bucket. Automatic cleanup
requires `KEYHOLDER_STORAGE_CLEANUP_ENABLED=true` after review. At capacity, it tries
to reach 80% usage before reserving a new image; if protections prevent room, the
image is refused while payment entry remains available. Data is not credited as
reclaimed until version deletion is verified. Cleanup never deletes financial rows.

## Recovery integration

Capture the database, token encryption key and available encrypted receipt objects
as one consistent recovery point. Use the storage API reservations to coordinate
receipt changes with external backup capture. Client packages and operational
recovery implementation have separate releases.

# Subscription forwarding integration

Run `node --test integrations/cloudflare-subscription/worker.test.mjs`.
The runtime test also requires `WORKERD_BIN` pointing to workerd.

The Worker forwards subscription requests to `UPSTREAM_ORIGIN`. Set
`UPSTREAM_TIMEOUT_MS` to a value from 100 to 60000 milliseconds. Keep Cloudflare
account configuration, hostname routes, bindings, origin selection and deployment
procedures outside application source releases. Disable request-path logging because
subscription paths contain bearer tokens.

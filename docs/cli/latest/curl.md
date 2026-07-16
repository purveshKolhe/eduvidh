# modal curl | Modal Docs

Source: https://modal.com/docs/cli/latest/curl

---

---

Copy page

# `modal curl`

Send an authenticated request to a Modal endpoint.

Experimental: This command may change or be removed in the future.

This command allows you to send authenticated requests without including proxy token
headers. Authentication is managed via your local Modal API credentials. API-based
authentication adds latency to requests, so this utility is recommended only for
experimentation and debugging purposes.

All arguments are passed directly to `curl`, which must be installed locally.

Examples:

```
modal curl https://user--my-app.us-west.modal.direct
modal curl -X GET https://user--my-app.us-west.modal.direct
```

**Usage**:

```
modal curl [OPTIONS] CURL_ARGS...
```

**Options**:

* `--help`: Show this message and exit.

[modal curl](#modal-curl)
# modal changelog | Modal Docs

Source: https://modal.com/docs/cli/latest/changelog

---

---

Copy page

# `modal changelog`

Fetch release notes from the Modal changelog.

This command prints changelog contents as markdown text and is useful for including
information about recent updates in the context for agent development sessions.

By default, the most recent updates in the current release series are shown. Other options
allow for showing changes since a previous version, changes in a specific version, or changes
that are newer than whatâs currently installed.

Examples:

```
modal changelog --since 1.2.0  # Show updates added after a specific version

modal changelog --since 2026-01-01  # Show updates added after a specific date

modal changelog --newer  # Show updates released after the currently installed version

modal changelog --last 3  # Show updates included in the 3 most recent releases

modal changelog --for 1.3.1  # Show the changelog for a specific release
```

Note: when using `--since` or `--last`, only changes up to the currently installed version are shown.

**Usage**:

```
modal changelog [OPTIONS]
```

**Options**:

* `--last INTEGER`: Show the N most recent entries before the installed version.
* `--since TEXT`: Show entries after a version (X.Y.Z) or date (YYYY-MM-DD), exclusive.
* `--for TEXT`: Show entries for a version (X.Y.Z) or series (X.Y).
* `--newer`: Show entries newer than the installed version.
* `--all`: Show all entries.
* `--json`: Output as JSON.
* `--help`: Show this message and exit.

[modal changelog](#modal-changelog)
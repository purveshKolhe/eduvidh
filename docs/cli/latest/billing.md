# modal billing | Modal Docs

Source: https://modal.com/docs/cli/latest/billing

---

---

Copy page

# `modal billing`

View workspace billing information.

**Usage**:

```
modal billing [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `report`: Generate a billing report for the workspace.

## `modal billing report`Â

Generate a billing report for the workspace.

The report range can be provided by setting `--start` / `--end` dates (`--end` defaults to ânowâ)
or by requesting a date range using `--for` (e.g., `--for today`, `--for 'last month'`).

This command provides a CLI frontend for the [`Workspace.billing.report`](https://modal.com/docs/sdk/py/latest/modal.Workspace#billingreport) API.

Note that, as with the API, the start date is inclusive and the end date is exclusive.
Data will be reported for full intervals only. Using `--for` is a convenient way to define a
complete interval.

In addition, the `--show-resources` option further breaks the cost in each bucket by the resource
that generated it (CPU, Memory, specific GPU types, etc.). Note that the specific resource types
included in the report are subject to change as Modalâs billing model evolves.

Examples:

```
modal billing report --start 2025-12-01 --end 2026-01-01

modal billing report --for "last month" --tag-names team,project

modal billing report --for today --resolution h

modal billing report --for "this month" --show-resources

modal billing report --for yesterday -r h --tz local

modal billing report --for "last month" --csv > report.csv

modal billing report --start 2025-12-01 --json > report.json
```

**Usage**:

```
modal billing report [OPTIONS]
```

**Options**:

* `--start TEXT`: Start date. Date (in UTC by default): ISO format (2025-01-01) or relative (yesterday, 3 days ago, etc.).
* `--end TEXT`: End date. Date (in UTC by default): ISO format (2025-01-01) or relative (yesterday, 3 days ago, etc.). Defaults to now.
* `--for TEXT`: Convenience range: today, yesterday, this week, last week, this month, last month.
* `-r, --resolution TEXT`: Time resolution: âdâ (daily) or âhâ (hourly).
* `--tz TEXT`: Timezone for date interpretation: âlocalâ, offset (5, -4, +05:30), or IANA name. Requires hourly resolution.
* `-t, --tag-names TEXT`: Comma-separated list of tag names to include.
* `--show-resources`: Further break down usage by resource type.
* `--json`: Output as JSON.
* `--csv`: Output as CSV.
* `--help`: Show this message and exit.

[modal billing](#modal-billing)[modal billing report](#modal-billing-report)
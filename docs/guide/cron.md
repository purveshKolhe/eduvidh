# Scheduling remote cron jobs | Modal Docs

Source: https://modal.com/docs/guide/cron

---

---

Copy page

# Scheduling remote cron jobs

A common requirement is to perform some task at a given time every day or week
automatically. Modal facilitates this through function schedules.

## Basic schedulingÂ

Letâs say we have a Python module `heavy.py` with a function, `perform_heavy_computation()`.

```
# heavy.py
def perform_heavy_computation():
    ...

if __name__ == "__main__":
    perform_heavy_computation()
```

To schedule this function to run once per day, we create a Modal App and attach
our function to it with the `@app.function` decorator and a schedule parameter:

```
# heavy.py
import modal

app = modal.App()

@app.function(schedule=modal.Period(days=1))
def perform_heavy_computation():
    ...
```

To activate the schedule, deploy your App, either through the CLI:

```
modal deploy --name daily_heavy heavy.py
```

Or programmatically:

```
if __name__ == "__main__":
   app.deploy()
```

Now the function will run every day, at the time of the initial deployment,
without any further interaction on your part.

When you make changes to your Function, just rerun the deploy command to
overwrite the old deployment.

Note that when you redeploy your Function, `modal.Period` resets, and the
schedule will run X hours after this most recent deployment.

If you want to run your Function at a regular schedule not disturbed by deploys, `modal.Cron` (see below) is a better option.

## Monitoring your scheduled runsÂ

To see past execution logs for the scheduled Function, go to the [Apps](https://modal.com/apps) section on the Modal web site.

Schedules currently cannot be paused. Instead the schedule should be removed and
the App redeployed. Schedules can be started manually on the Appâs dashboard
page, using the ârun nowâ button.

## Schedule typesÂ

There are two kinds of base schedule values - [`modal.Period`](/docs/sdk/py/latest/modal.Period) and [`modal.Cron`](/docs/sdk/py/latest/modal.Cron).

[`modal.Period`](/docs/sdk/py/latest/modal.Period) lets you specify an interval
between function calls, e.g. `Period(days=1)` or `Period(hours=5)`:

```
# runs once every 5 hours
@app.function(schedule=modal.Period(hours=5))
def perform_heavy_computation():
    ...
```

[`modal.Cron`](/docs/sdk/py/latest/modal.Cron) gives you finer control using [cron](https://en.wikipedia.org/wiki/Cron) syntax:

```
# runs at 8 am (UTC) every Monday
@app.function(schedule=modal.Cron("0 8 * * 1"))
def perform_heavy_computation():
    ...

# runs daily at 6 am (New York time)
@app.function(schedule=modal.Cron("0 6 * * *", timezone="America/New_York"))
def send_morning_report():
    ...
```

For more details, see the API reference for [Period](/docs/sdk/py/latest/modal.Period), [Cron](/docs/sdk/py/latest/modal.Cron) and [Function](/docs/sdk/py/latest/modal.Function)

[Scheduling remote cron jobs](#scheduling-remote-cron-jobs)[Basic scheduling](#basic-scheduling)[Monitoring your scheduled runs](#monitoring-your-scheduled-runs)[Schedule types](#schedule-types)

See it in action

[Hacker News Slackbot](/docs/examples/hackernews_alerts)
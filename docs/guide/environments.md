# Environments | Modal Docs

Source: https://modal.com/docs/guide/environments

---

---

Copy page

# Environments

Modal Environments isolate Modal applications and resources from one another.

Environments are sub-divisions of [Workspaces](/docs/guide/workspaces),
allowing you to deploy the same App (or set of Apps)
in multiple instances for different purposes without changing code.

Typical use cases for Environments include having one `dev` Environment and one `prod` Environment. Production Apps are protected from overwriting
when developing new features, but you can still deploy and test changes with a
âliveâ and potentially complex structure of Apps.

Each Environment has its own set of [Secrets](/docs/guide/secrets) and any
object lookups, say for [Dicts](/docs/guide/dicts) or [Volumes](/docs/guide/volumes),
performed from an App in an Environment will by default look for objects in the same Environment.

By default, every Workspace has a single Environment called âmainâ. New
Environments can be created on the CLI:

```
modal environment create dev
```

Run `modal environment --help` for more info.

Workspaces can have up to 1500 Environments.

Once created, Environments show up as a dropdown menu in the navbar of the [Modal dashboard](/apps), letting you set browse all Modal Apps, Secrets, and Storage
filtered by which Environment they were deployed to.

Most CLI commands also support an `--env` flag letting you specify which
Environment you intend to interact with, e.g.:

```
modal run --env=dev app.py
modal volume create --env=dev storage
```

To set a default Environment for your current CLI profile you can use `modal config set-environment`, e.g.:

```
modal config set-environment dev
```

Alternatively, you can set the `MODAL_ENVIRONMENT` environment variable.

## Environment web suffixesÂ

Environments have a âweb suffixâ which is used to make [Web Function URLs](/docs/guide/webhook-urls) unique across your workspace. One
Environment is allowed to have no suffix (`""`).

## Cross environment lookupsÂ

Itâs possible to explicitly look up objects in Environments other than the Environment
your App runs within:

```
production_secret = modal.Secret.from_name(
    "my-secret",
    environment_name="main",
)
```

```
modal.Function.from_name(
    "my_app",
    "some_function",
    environment_name="dev"
)
```

However, the `environment_name` argument is optional and omitting it will use
the Environment from the objectâs associated App or calling context.

[Environments](#environments)[Environment web suffixes](#environment-web-suffixes)[Cross environment lookups](#cross-environment-lookups)
# modal.config | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.config

---

---

Copy page

# modal.config

Modal intentionally keeps configurability to a minimum.

The main configuration options are the API tokens: the token id and the token secret.
These can be configured in two ways:

1. By running the `modal token set` command.
   This writes the tokens to `.modal.toml` file in your home directory.
2. By setting the environment variables `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`.
   This takes precedence over the previous method.

## .modal.tomlÂ

The `.modal.toml` file is generally stored in your home directory.
It should look like this::

```
[default]
token_id = "ak-12345..."
token_secret = "as-12345..."
```

You can create this file manually, or you can run the `modal token set ...` command (see below).

## Setting tokens using the CLIÂ

You can set a token by running the command::

```
modal token set \
  --token-id <token id> \
  --token-secret <token secret>
```

This will write the token id and secret to `.modal.toml`.

If the token id or secret is provided as the string `-` (a single dash),
then it will be read in a secret way from stdin instead.

## Other configuration optionsÂ

Other possible configuration options are:

* `loglevel` (in the .toml file) / `MODAL_LOGLEVEL` (as an env var).
  Defaults to `WARNING`. Set this to `DEBUG` to see internal messages.
* `logs_timeout` (in the .toml file) / `MODAL_LOGS_TIMEOUT` (as an env var).
  Defaults to 10.
  Number of seconds to wait for logs to drain when closing the session,
  before giving up.
* `max_throttle_wait` (in the .toml file) / `MODAL_MAX_THROTTLE_WAIT` (as an env var).
  Defaults to None (no limit).
  Maximum number of seconds to wait when requests are being throttled (i.e., due
  to rate limiting or other cases that can normally be resolved through backoff).
* `force_build` (in the .toml file) / `MODAL_FORCE_BUILD` (as an env var).
  Defaults to False.
  When set, ignores the Image cache and builds all Image layers. Note that this
  will break the cache for all images based on the rebuilt layers, so other images
  may rebuild on subsequent runs / deploys even if the config is reverted.
* `ignore_cache` (in the .toml file) / `MODAL_IGNORE_CACHE` (as an env var).
  Defaults to False.
  When set, ignores the Image cache and builds all Image layers. Unlike `force_build`,
  this will not overwrite the cache for other images that have the same recipe.
  Subsequent runs that do not use this option will pull the *previous* Image from
  the cache, if one exists. It can be useful for testing an Appâs robustness to
  Image rebuilds without clobbering Images used by other Apps.
* `traceback` (in the .toml file) / `MODAL_TRACEBACK` (as an env var).
  Defaults to False. Enables printing full tracebacks on unexpected CLI
  errors, which can be useful for debugging client issues.
* `log_pattern` (in the .toml file) / `MODAL_LOG_PATTERN` (as an env var).
  Defaults to `"[modal-client] %(asctime)s %(message)s"` The log formatting pattern that will be used by the modal client itself.
  See <https://docs.python.org/3/library/logging.html#logrecord-attributes> for available
  log attributes.
* `dev_suffix` (in the .toml file) / `MODAL_DEV_SUFFIX` (as an env var).
  Overrides the default `-dev` suffix added to URLs generated for Web Functions
  when the App is ephemeral (i.e., created via `modal serve`). Must be a short
  alphanumeric string.

## Meta-configurationÂ

Some âmeta-optionsâ are set using environment variables only:

* `MODAL_CONFIG_PATH` lets you override the location of the .toml file,
  by default `~/.modal.toml`.
* `MODAL_PROFILE` lets you use multiple sections in the .toml file
  and switch between them. It defaults to âdefaultâ.

## modal.config.ConfigÂ

```
class Config(object)
```

Singleton that holds configuration used by Modal internally.

```
__init__(self)
```

 

### getÂ

```
get(self, key, *, profile=None, use_env=True)
```

Look up a configuration value.

Resolution order (highest priority first):

1. Environment variable `MODAL_<KEY>` (underscore-separated, uppercased), when `use_env` is True.
2. The named profile in `.modal.toml`.
3. The built-in default for that setting.

**Parameters**

key str

Setting name (for example `"loglevel"` or `"server_url"`); see the `modal.config` module docs.

profile str | None

Profile section to read from the TOML file; defaults to the active profile.

use\_env bool

When False, skip environment variables and read only from the file or defaults. (Default is True)

**Returns**

The transformed configuration value (type depends on the setting).

### override\_locallyÂ

```
override_locally(self, key, value)
```

 

### to\_dictÂ

```
to_dict(self)
```

 

## modal.config.config\_profilesÂ

```
config_profiles()
```

List the available Modal profiles in the `.modal.toml` file.

**Returns**

Profile section names present in the configuration file.

## modal.config.config\_set\_active\_profileÂ

```
config_set_active_profile(profile)
```

Set the userâs active Modal profile by writing it to the `.modal.toml` file.

**Parameters**

profile str

Name of an existing profile section to mark as active.

[modal.config](#modalconfig)[.modal.toml](#modaltoml)[Setting tokens using the CLI](#setting-tokens-using-the-cli)[Other configuration options](#other-configuration-options)[Meta-configuration](#meta-configuration)[Config](#modalconfigconfig)[get](#get)[override\_locally](#override_locally)[to\_dict](#to_dict)[config\_profiles](#modalconfigconfig_profiles)[config\_set\_active\_profile](#modalconfigconfig_set_active_profile)
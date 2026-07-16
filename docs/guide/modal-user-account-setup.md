# Modal user account setup | Modal Docs

Source: https://modal.com/docs/guide/modal-user-account-setup

---

---

Copy page

# Modal user account setup

To run and deploy applications on Modal youâll need to sign up and create a user
account.

You can visit the [signup](/signup) page to begin the process or execute [`modal setup`](/docs/cli/latest/setup#modal-setup) on the command line.

Users can also be provisioned through [Okta SSO](/docs/guide/okta-sso), which is
an enterprise feature that you can request. For the typical user youâll sign-up
using an existing GitHub account. If youâre interested in authenticating with
other identity providers let us know at [support@modal.com](mailto:support@modal.com).

## What GitHub permissions does signing up require?Â

* `user:email` â gives us the emails associated with the GitHub account.
* `read:org` (invites only) â needed for Modal Workspace invites. Note: this
  only allows us to see what organization memberships you have
  ([GitHub docs](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)).
  We wonât be able to access any code repositories or other details.

## How can I change my email?Â

You can change your email on the [settings](/settings) page.

[Modal user account setup](#modal-user-account-setup)[What GitHub permissions does signing up require?](#what-github-permissions-does-signing-up-require)[How can I change my email?](#how-can-i-change-my-email)
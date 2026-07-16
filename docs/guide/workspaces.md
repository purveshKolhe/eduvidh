# Workspaces | Modal Docs

Source: https://modal.com/docs/guide/workspaces

---

---

Copy page

# Workspaces

This page is a high-level guide to Modal Workspaces,
the primary unit of organization for Modal resources
and authentication.

A **Workspace** is an area where a user can deploy Modal Apps and other
resources. When you sign up to Modal, a Workspace is automatically created for
you. Its name is based on your GitHub username, but may be randomly generated
if that name is taken or invalid.

Every Workspace is shared, meaning you can invite others by email to
collaborate with you.

 

## Create a WorkspaceÂ

There are two ways to create an additional Modal Workspace on the [settings](/settings/workspaces) page.

![view of workspaces creation interface](https://modal-cdn.com/cdnbot/create-new-workspace-viewk0ka46_7_800f2053.webp)

1. Create from [GitHub organization](https://docs.github.com/en/organizations). Allows members of the GitHub organization to auto-join the Workspace.
2. Create from scratch. You can invite anyone to your Workspace.

If youâre interested in having a Workspace associated with your Okta
organization, then check out our [Okta SSO docs](/docs/guide/okta-sso).

To use SSO through Google or other providers, reach out to us at [support@modal.com](mailto:support@modal.com).

## Auto-joining a Workspace associated with a GitHub organizationÂ

Note: This is only relevant for Workspaces created from a GitHub organization.

Users can automatically join a Workspace on their [Workspace settings page](/settings/workspaces) if they are a member of the GitHub organization associated with the Workspace.

To turn off this functionality a Workspace Manager can disable it on the **Workspace Management** tab of their Workspaceâs settings page.

## Inviting new Workspace membersÂ

To invite a new Workspace member, you can visit the [settings](/settings) page
and navigate to the Members tab for the appropriate Workspace.

You can either send an email invite or share an invite link. Both existing Modal
users and people who donât yet have a Modal account can use the link to join
your Workspace; if they donât have an account, one is created for them.

Inviting members requires a verified account. If you havenât already, add a
payment method to verify your account.

![invite member section](/_app/immutable/assets/invite-member.CHnml0eT.png)

## Create a token for a WorkspaceÂ

To interact with a Workspaceâs resources programmatically, you need to add an
API token for that Workspace. Your existing API tokens are displayed on [the settings page](/settings/tokens) and new API tokens can be added for a
particular Workspace.

After adding a token for a Workspace to your Modal config file you can activate
that Workspaceâs profile using the CLI (see below).

As a Manager or Workspace Owner you can manage active tokens for a Workspace on [the member tokens page](/settings/tokens/member-tokens). For more information on API
token management see the [documentation about configuration](/docs/sdk/py/latest/modal.config).

## Switching active WorkspaceÂ

When on the dashboard or using the CLI, the active profile determines which
Workspace is associated with your actions.

### DashboardÂ

You can switch between your Workspaces by using the workspace selector at the
top of [the dashboard](/home).

### CLIÂ

To switch the Workspace associated with CLI commands, use `modal profile activate`.

## Administering Workspace membershipÂ

Workspaces have three different levels of access privileges:

* Owner
* Manager
* Member

A user that creates a Workspace is automatically set as the **Owner** for that
Workspace. The owner can assign any other roles within the Workspace, as well as
remove other members of the Workspace.

A **Manager** within a Workspace can assign all roles except **Owner** and can
also remove other members of the Workspace.

A **Member** of a Workspace cannot assign any access privileges within the
Workspace but can otherwise perform any action like running and deploying Apps
and modifying Secrets.

As an Owner or Manager you can administer the access privileges of other
members on the `Workspace Management` tab in [settings](/settings/workspace-management).

 

## Leaving a WorkspaceÂ

To leave a Workspace, navigate to [the settings page](/settings/workspaces) and
click âLeaveâ on a listed Workspace. You canât leave a Workspace if youâre its
only remaining member. If youâre the last Owner of a Workspace that still has
other members, assign a new Owner before leaving. Personal Workspaces are
single-member, so they canât be left.

[Workspaces](#workspaces)[Create a Workspace](#create-a-workspace)[Auto-joining a Workspace associated with a GitHub organization](#auto-joining-a-workspace-associated-with-a-github-organization)[Inviting new Workspace members](#inviting-new-workspace-members)[Create a token for a Workspace](#create-a-token-for-a-workspace)[Switching active Workspace](#switching-active-workspace)[Dashboard](#dashboard)[CLI](#cli)[Administering Workspace membership](#administering-workspace-membership)[Leaving a Workspace](#leaving-a-workspace)
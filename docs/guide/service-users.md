# Service Users | Modal Docs

Source: https://modal.com/docs/guide/service-users

---

---

Copy page

# Service Users

 

Service users are programmatic accounts that allow automated systems to interact with Modal. Theyâre ideal for CI/CD pipelines, automated deployments, and other workflows that need to authenticate.

## Create a Service UserÂ

Service users are only available for shared workspaces. You will need workspace owner or manager privileges to create service users.

To create a service user:

1. Go to your workspace [tokens settings page](/settings/tokens/service-users)
2. Click **New Service User**
3. Enter a name for your service user (must be lowercase alphanumeric, can contain hyphens or underscores)
4. Click **Create**

After creation, youâll see the `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`. **This is the only time you can view the token secret** for security reasons.

## Use Service User TokensÂ

Set the service user credentials as environment variables in your automated environment:

```
export MODAL_TOKEN_ID=your-token-id
export MODAL_TOKEN_SECRET=your-token-secret
```

Once configured, you can use Modalâs CLI and Python SDK as usual:

```
modal deploy your_app.py
```

 

## Delete a Service UserÂ

To remove a service user:

1. Go to the [tokens settings page](/settings/tokens/service-users)
2. Find the service user in the table
3. Click **Delete** when you hover over the row

## PermissionsÂ

Service users have the same permissions as workspace members. They cannot do actions that are only permitted for a workspace owner or manager. To learn more about members, managers, and owners, see this [workspace](/docs/guide/workspaces#administrating-workspace-members) section.

## Securing Service UsersÂ

Because service user tokens are long-lived and used in automated environments, itâs important to limit their access to only whatâs necessary:

* **Store tokens securely.** Use a secrets manager or your CI/CD platformâs built-in secrets storage rather than hardcoding tokens in source code or configuration files.
* **Use restricted Environments.** Assign service users the **Contributor** role only on the specific Environments they need access to, keeping production isolated from development and staging.

[Service Users](#service-users)[Create a Service User](#create-a-service-user)[Use Service User Tokens](#use-service-user-tokens)[Delete a Service User](#delete-a-service-user)[Permissions](#permissions)[Securing Service Users](#securing-service-users)
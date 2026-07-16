# Custom SAML SSO | Modal Docs

Source: https://modal.com/docs/guide/saml-sso

---

---

Copy page

# Custom SAML SSO

 

If you use an identity provider (IdP) other than Okta, you can configure custom SAML SSO for your Modal Workspace.

For Okta-specific setup, see our [Okta SSO documentation](/docs/guide/okta-sso).

## PrerequisitesÂ

* A Workspace thatâs on an [Enterprise](/pricing) plan
* Admin access to the Workspace you want to configure with SSO
* Admin privileges for your identity provider

## Supported featuresÂ

* Identity Provider (IdP) initiated SSO
* Service Provider (SP) initiated SSO
* Just-In-Time account provisioning

## ConfigurationÂ

 

### Modal SAML settingsÂ

Configure your IdP with the following settings:

| Setting | Value |
| --- | --- |
| Entity ID | `https://www.modal.com` |
| ACS URL | `https://modal.com/api/okta/saml/sso/<workspace>` |

Replace `<workspace>` with your Modal Workspace name.

### Required SAML attributesÂ

Your IdP must send the following SAML attributes:

| Attribute | Description |
| --- | --- |
| email | Userâs email address |
| firstName | Userâs first name |
| lastName | Userâs last name |

 

### Configuration stepsÂ

 

#### Step 1: Configure your IdPÂ

1. Create a new SAML application in your identity provider
2. Set the Entity ID to `https://www.modal.com`
3. Set the ACS URL to `https://modal.com/api/okta/saml/sso/<workspace>` (replace `<workspace>` with your Workspace name)
4. Configure the required SAML attributes (email, firstName, lastName)
5. Ensure your IdP signs SAML assertions

#### Step 2: Link your Workspace to your IdPÂ

1. Obtain the SAML Metadata URL from your IdP
2. Sign in to <https://modal.com> and visit your [Workspace Management](/settings/workspace-management/identity-and-provisioning) pageâs `Identity and Provisioning` tab
3. Paste the Metadata URL in the input and click âSave Changesâ

#### Step 3: Test the integrationÂ

1. Assign users in your IdP
2. Test IdP-initiated SSO by clicking the Modal application in your IdP dashboard
3. Test SP-initiated SSO by visiting the login URL below

#### Step 4: Read this before you enable âRequire SSOâÂ

Enabling âRequire SSOâ will force all users to sign in via SSO. Ensure that you
have admin access to your Modal Workspace through your identity provider before
enabling.

## Login URLÂ

This URL can be used so that users can sign-in to the correct workspace from your IdP.

`https://modal.com/login/sso?workspace=<workspace>` (replace `<workspace>` with your workspace name)

## TroubleshootingÂ

 

### Microsoft Entra SAMLÂ

Make sure the SAML attributes are mapped correctly. For example, `email` should be lowercase and the SAML attribute should not have a namespace. Read more about Microsoft Entra SAML attributes [here](https://learn.microsoft.com/en-us/entra/identity-platform/saml-claims-customization).

[Custom SAML SSO](#custom-saml-sso)[Prerequisites](#prerequisites)[Supported features](#supported-features)[Configuration](#configuration)[Modal SAML settings](#modal-saml-settings)[Required SAML attributes](#required-saml-attributes)[Configuration steps](#configuration-steps)[Step 1: Configure your IdP](#step-1-configure-your-idp)[Step 2: Link your Workspace to your IdP](#step-2-link-your-workspace-to-your-idp)[Step 3: Test the integration](#step-3-test-the-integration)[Step 4: Read this before you enable âRequire SSOâ](#step-4-read-this-before-you-enable-require-sso)[Login URL](#login-url)[Troubleshooting](#troubleshooting)[Microsoft Entra SAML](#microsoft-entra-saml)
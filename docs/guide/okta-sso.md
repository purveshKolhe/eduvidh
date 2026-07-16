# Okta SSO | Modal Docs

Source: https://modal.com/docs/guide/okta-sso

---

---

Copy page

# Okta SSO

  

## PrerequisitesÂ

* A Workspace thatâs on an [Enterprise](/pricing) plan
* Admin access to the Workspace you want to configure with Okta Single-Sign-On (SSO)
* Admin privileges for your Okta Organization

## Supported featuresÂ

* Identity Provider (IdP) initiated SSO
* Service Provider (SP) initiated SSO
* Just-In-Time account provisioning

For more information on the listed features, visit the [Okta Glossary](https://help.okta.com/okta_help.htm?type=oie&id=ext_glossary).

## ConfigurationÂ

 

### Read this before you enable âRequire SSOâÂ

Enabling âRequire SSOâ will force all users to sign in via Okta. Ensure that you
have admin access to your Modal Workspace through an Okta account before
enabling.

### Configuration stepsÂ

 

#### Step 1: Add Modal app to Okta ApplicationsÂ

1. Sign in to your Okta admin dashboard
2. Navigate to the Applications tab and click âBrowse App Catalogâ. ![Okta browse application](/_app/immutable/assets/okta-browse-applications.BiqGsdcd.png)
3. Select âModalâ and click âDoneâ.
4. Select the âSign Onâ tab and click âEditâ. ![Okta sign on edit](/_app/immutable/assets/okta-sign-on-edit.DHny2cIB.png)
5. Fill out Workspace field to configure for your specific Modal Workspace. See [Step 2](/docs/guide/okta-sso#step-2-link-your-workspace-to-okta-modal-application) if youâre unsure what this is. ![Okta add workspace](/_app/immutable/assets/okta-add-workspace-username.DoM8qewy.png)

#### Step 2: Link your Workspace to Okta Modal applicationÂ

1. Navigate to your application on the Okta Admin page.
2. Copy the Metadata URL from the Okta Admin Console (Itâs under the âSign Onâ
   tab). ![Okta metadata url](/_app/immutable/assets/okta-metadata-url.BLDzMpWn.png)
3. Sign in to <https://modal.com> and visit your [Workspace Management](/settings/workspace-management/identity-and-provisioning) pageâs `Identity and Provisioning` tab.
4. Paste the Metadata URL in the input and click âSave Changesâ

#### Step 3: Assign users / groups and test the integrationÂ

1. Navigate back to your Okta application on the Okta Admin dashboard.
2. Click on the âAssignmentsâ tab and add the appropriate people or groups.

![Okta Assign Users](/_app/immutable/assets/okta-assign-people.BhAmcJ0m.png)

3. To test the integration, sign in as one of the users you assigned in the previous step.
4. Click on the Modal application on the Okta Dashboard to initiate Single Sign-On.

#### NotesÂ

The following SAML attributes are used by the integration:

| Name | Value |
| --- | --- |
| email | user.email |
| firstName | user.firstName |
| lastName | user.lastName |

 

## SP-initiated SSOÂ

The sign-in process is initiated from <https://modal.com/login/sso>

1. Enter your workspace name in the input
2. Click âcontinue with SSOâ to authenticate with Okta

[Okta SSO](#okta-sso)[Prerequisites](#prerequisites)[Supported features](#supported-features)[Configuration](#configuration)[Read this before you enable âRequire SSOâ](#read-this-before-you-enable-require-sso)[Configuration steps](#configuration-steps)[Step 1: Add Modal app to Okta Applications](#step-1-add-modal-app-to-okta-applications)[Step 2: Link your Workspace to Okta Modal application](#step-2-link-your-workspace-to-okta-modal-application)[Step 3: Assign users / groups and test the integration](#step-3-assign-users--groups-and-test-the-integration)[Notes](#notes)[SP-initiated SSO](#sp-initiated-sso)
# Credential handling

Set Telegram and exchange credentials through the process environment or your deployment secret store. `.env.example` contains names only; this application does not automatically load `.env` files.

Credentials previously committed must be revoked at the provider. Removing a file does not remove it from Git history. Review all services, scheduled jobs, deployments and backup configurations that use the credential before introducing a replacement. Never paste credentials into issues, logs or pull requests. Security CI scans current files; audit all history separately after an incident. Never validate suspected secrets against provider APIs.

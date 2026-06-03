# Deployment variables

This project uses GitHub Actions, Ansible, Docker Hub, and a Debian VM.

## GitHub organization secrets and variables

Keep infrastructure and production environment values on the organization level
so repositories can inherit them.

Secrets:

```text
SSH_PRIVATE_KEY_B64
ENV
```

Variables:

```text
VM_HOST=77.110.117.83
VM_USER=root
DEPLOY_PATH=/opt/uml-diagram-editor
```

`SSH_PRIVATE_KEY_B64` is the private SSH key encoded as base64.

PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\User\.ssh\cloud-vm"))
```

`ENV` is the full production `.env` file content. Do not commit it to the
repository.

## GitHub repository secrets and variables

Repository secrets:

```text
DOCKER_TOKEN
GH_TOKEN
```

Repository variables:

```text
DOCKER_USER=umldiagrameditor
DOCKER_IMAGE_NAME=uml-diagram-editor-api
```

## Production `.env`

Use `.env.example` as the source checklist. Keep the file focused on values
that actually differ between environments.

For HTTP deployment by IP:

```text
FRONTEND__SCHEME=http
FRONTEND__HOST=77.110.117.83
FRONTEND__PORT=
```

After HTTPS is configured through DuckDNS and Nginx Proxy Manager:

```text
FRONTEND__SCHEME=https
FRONTEND__HOST=<duckdns-domain>
FRONTEND__PORT=
```

Generate `AUTH__JWT_PRIVATE_KEY` with:

```bash
openssl rand -hex 32
```

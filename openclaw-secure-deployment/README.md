# OpenClaw on DigitalOcean: Secure Deployment Guide

A step-by-step reference for securely deploying OpenClaw on a DigitalOcean Droplet with Tailscale, SSH hardening, and firewall configuration.

Companion guide to the YouTube video: [COMING SOON]

---

## 1. Deploy the Droplet

Go to the [DigitalOcean Marketplace](https://do.co/4swLlx2) and deploy the OpenClaw 1-Click Droplet.

Recommended plan: **4 GB RAM / 2 vCPU** (`s-2vcpu-4gb`)

Use **SSH Key** authentication (not password).

> The dashboard may show "ready" before SSH is available. Wait about 60 seconds before connecting.

---

## 2. SSH In and Configure OpenClaw

Connect to your Droplet:

```bash
ssh root@your-droplet-ip
```

The interactive setup will ask for your LLM provider (Anthropic, OpenAI, or Gradient) and API key. Follow the prompts to pair with the Gateway Dashboard.

Verify OpenClaw is running by launching the Terminal UI:

```bash
/opt/openclaw-tui.sh
```

---

## 3. Connect Telegram

In Telegram, message **@BotFather** and type `/newbot` to create a bot. Copy the **bot token**.

On the Droplet, add Telegram as a channel:

```bash
/opt/openclaw-cli.sh channels add
```

Select Telegram and paste your bot token.

Open the deep link BotFather gave you and send a message. Copy your **Telegram user ID** from the response, then add it to the **allow list** in the OpenClaw Gateway Dashboard.

---

## 4. Install and Configure Tailscale

Install Tailscale on the Droplet:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Bring it up with SSH support:

```bash
tailscale up --ssh
```

Authenticate via the link provided, then verify:

```bash
tailscale status
```

Note your Tailscale IP (e.g. `100.x.x.x`). You'll need it for the next steps.

Install Tailscale on your local machine as well and log in with the same account.

---

## 5. Harden SSH

Edit the SSH config:

```bash
sudo nano /etc/ssh/sshd_config
```

Add or update these lines:

```
ListenAddress 100.x.x.x
PasswordAuthentication no
PermitRootLogin no
```

Replace `100.x.x.x` with your actual Tailscale IP.

What each setting does:
- **ListenAddress**: SSH only accepts connections from the Tailscale interface. Public internet connections are refused.
- **PasswordAuthentication no**: Forces key-based authentication only.
- **PermitRootLogin no**: Blocks all root login attempts.

Check for cloud provider override files that can undo these settings:

```bash
ls /etc/ssh/sshd_config.d/
```

If `50-cloud-init.conf` exists, edit it:

```bash
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf
```

Ensure it contains:

```
PasswordAuthentication no
```

---

## 6. Create a Non-Root User

Create a new user:

```bash
adduser akshay
```

Grant sudo privileges:

```bash
usermod -aG sudo akshay
```

Verify:

```bash
su - akshay
sudo whoami
```

If the output is `root`, the user has sudo access but isn't running as root by default.

---

## 7. Apply Changes and Test

Restart SSH to apply all changes:

```bash
sudo systemctl restart ssh
```

From this point, SSH only works through Tailscale. Test from your local machine:

```bash
ssh akshay@your-tailscale-ip
```

Access the Terminal UI as the new user:

```bash
sudo /opt/openclaw-tui.sh
```

---

## 8. Configure the DigitalOcean Firewall

In the DigitalOcean dashboard, go to **Networking**, then **Firewalls**, and create a new firewall.

Add a single inbound rule:

| Field | Value |
|---|---|
| Type | Custom |
| Protocol | UDP |
| Port | 41641 |
| Sources | All IPv4, All IPv6 (`::/0`) |

This allows only the Tailscale WireGuard tunnel. All other inbound traffic is blocked.

Attach the firewall to your Droplet.

---

## 9. Access the Gateway Dashboard

On your **local machine**, use SSH port forwarding:

```bash
ssh -N -L 18789:127.0.0.1:18789 akshay@your-tailscale-ip
```

Then open `http://localhost:18789` in your browser.

This works because the SSH connection runs through the Tailscale tunnel (UDP 41641). Port 18789 is never exposed to the public internet.

---

## 10. Set Execution Policies

SSH into your Droplet and run:

```bash
sudo /opt/openclaw-cli.sh config set tools.exec.host gateway
sudo /opt/openclaw-cli.sh config set tools.exec.ask off
sudo /opt/openclaw-cli.sh config set tools.exec.security full
```

Restart the service:

```bash
sudo systemctl restart openclaw
```

What each setting does:
- **tools.exec.host gateway**: Routes commands through the gateway process. Without this, commands have nowhere to run on a headless VPS.
- **tools.exec.ask off**: Disables approval prompts. On a headless server, nobody is there to approve, so commands would hang forever.
- **tools.exec.security full**: Gives OpenClaw the highest execution tier within its sandbox. Required for network calls, shell commands, and skill execution. This does not grant root access.

Verify your settings:

```bash
sudo /opt/openclaw-cli.sh config get tools.exec
```

---

## Security Summary

| Layer | What It Does |
|---|---|
| DigitalOcean Firewall | Blocks all inbound traffic except UDP 41641 (Tailscale) |
| Tailscale | Encrypted WireGuard tunnel. Server is invisible to the public internet |
| SSH ListenAddress | SSH only accepts connections from the Tailscale interface |
| PasswordAuthentication no | Key-based authentication only |
| PermitRootLogin no | Root login disabled |
| Non-root user | Day-to-day operations run without root privileges |
| Docker sandboxing | OpenClaw runs inside containers, isolated from the host filesystem |
| Gateway tokens + DM pairing | Only authorized users can interact with the agent |

---

## Useful Commands

| Task | Command |
|---|---|
| Check OpenClaw status | `systemctl status openclaw` |
| View live logs | `journalctl -u openclaw -f` |
| Edit environment | `nano /opt/openclaw.env` |
| Launch Terminal UI | `/opt/openclaw-tui.sh` |
| Diagnose issues | `openclaw doctor` |
| Find gateway token | `openclaw dashboard` |
| Update OpenClaw | `/opt/update-openclaw.sh` |

---

## Links

- [DigitalOcean Marketplace: OpenClaw](https://do.co/4swLlx2)
- [OpenClaw Documentation](https://docs.molt.bot/)
- [OpenClaw GitHub](https://github.com/moltbot/moltbot)
- [Tailscale](https://tailscale.com/)
- [DigitalOcean SSH Key Guide](https://do.co/4swLlx2)

# LabelSync<br>[![GitHub Actions][actions-img]][actions-url] [![Patreon][patreon-img]][patreon-url] [![PayPal][paypal-img]][paypal-url] [![Discord][discord-img]][discord-url]

LabelSync is a simple Python script that synchronizes your labels between different repos across an set of user or organization repos by leveraging GitHub actions.

## Download

`git clone https://github.com/justalemon/LabelSync.git`

## Installation

Install Python 3 and pip in your system, install the requirements with `pip install -r requirements.txt` and run te Python file.

## Usage

* Locally: Edit labels.yml to your liking, add the tokens to .env (create it if it doesn't exists) and then run `python3 labels.py`
* Actions: Fork the repo, edit and commit labels.yml to your liking, and then store the tokens as [secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)

[actions-img]: https://img.shields.io/github/actions/workflow/status/justalemon/LabelSync/main.yml?branch=master&label=actions
[actions-url]: https://github.com/justalemon/LabelSync/actions
[patreon-img]: https://img.shields.io/badge/support-patreon-FF424D.svg
[patreon-url]: https://www.patreon.com/lemonchan
[paypal-img]: https://img.shields.io/badge/support-paypal-0079C1.svg
[paypal-url]: https://paypal.me/justalemon
[discord-img]: https://img.shields.io/badge/discord-join-7289DA.svg
[discord-url]: https://discord.gg/Cf6sspj

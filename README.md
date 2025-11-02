# Expense Management App

A lightweight command-line application for managing expenses across multiple wallets in
different currencies. The app consolidates balances and spending into a single currency of
your choice using a built-in currency converter that currently supports the five most common
currencies (USD, EUR, GBP, JPY, AUD).

## Features

- Maintain multiple wallets, each in its own currency and with an independent balance.
- Record expenses against a wallet and track remaining balances automatically.
- View a consolidated dashboard converted into a single target currency.
- Inspect individual wallet reports with automatic currency conversion.
- Persist data to a simple JSON file for easy backups and manual editing.

## Getting Started

### Requirements

- Python 3.11+

No third-party dependencies are required.

### Installation

Clone the repository (or open it in a GitHub Codespace) and navigate to the
project directory:

```bash
cd ProjectVeo1
```

### Usage

All CLI commands should be executed from the project root—the directory that
contains ``README.md`` and ``main.py`` after cloning or opening the repo in a
Codespace. The GitHub web UI alone cannot run these commands; you need a local
terminal or the integrated terminal in Codespaces/GitHub Desktop.

Use the ``main.py`` entry point to interact with the application. By default, data is stored in
``expense_data.json`` in the project root. Supply ``--data-file`` to use a different location.

Create a wallet:

```bash
python main.py create-wallet Personal USD --balance 1500
```

Add an expense:

```bash
python main.py add-expense Personal 45 "Groceries" --category food
```

List wallets:

```bash
python main.py list-wallets
```

View the consolidated dashboard in a target currency (e.g., EUR):

```bash
python main.py dashboard EUR
```

Quickly preview the consolidated dashboard (defaults to USD, override with `--currency`).
The output now includes a `using_demo_data` flag so you can tell when the
summary was generated from live data versus the sample dataset:

```bash
python main.py preview --currency EUR
```

Preview the app with ready-made sample data—ideal for kicking the tires without
creating wallets first:

```bash
python main.py preview --demo
```

Show a detailed wallet report with conversion:

```bash
python main.py wallet-report Personal --currency USD
```

Display the supported currencies:

```bash
python main.py supported-currencies
```

### Running Tests

Execute the unit tests with ``pytest`` or the Python unittest runner:

```bash
python -m pytest
```

### Uploading the project to GitHub

The repository includes a helper script that can create (or reuse) a GitHub
repository and push the current branch in a single step. Provide a personal
access token with the ``repo`` scope either through the ``GITHUB_TOKEN``
environment variable or the ``--token`` option:

```bash
python scripts/upload_to_github.py my-expense-app --token YOUR_TOKEN
```

By default the script will create a private repository in your personal
account, configure the ``origin`` remote, and push the branch that is
currently checked out. When a brand new repository is created, the content is
pushed to the remote ``main`` branch so GitHub shows your files immediately,
even if your local branch has a different name. Use ``--public`` for a public
repository, ``--owner`` to target an organization, or ``--branch`` to push a
specific local branch. Provide ``--remote-branch`` if you need to push to a
remote branch other than the default ``main``/current branch pairing.

## Data Format

The application stores data in JSON format. A sample structure looks like:

```json
{
  "wallets": [
    {
      "name": "Personal",
      "currency": "USD",
      "balance": 1380.0,
      "expenses": [
        {
          "description": "Groceries",
          "amount": 120.0,
          "category": "food"
        }
      ]
    }
  ]
}
```

You can safely edit this file by hand if you need to make bulk updates.

## Supported Currencies

- USD — United States Dollar
- EUR — Euro
- GBP — British Pound Sterling
- JPY — Japanese Yen
- AUD — Australian Dollar

## Newsletter Template

A standalone Apple News-inspired newsletter mockup is available at
`templates/newsletter.html`. Open the file in a browser to preview the layout or
use it as a starting point for your own HTML email design.

# Nova AI 🤖

Nova AI est un assistant conversationnel expérimental développé en Python.

## Fonctionnalités

- Conversation en français par règles prédéfinies
- Mémoire persistante en JSON
- Calculatrice avec analyse sécurisée des expressions
- Historique des 100 derniers échanges
- Tests automatiques avec unittest

## Prérequis

Python 3.10 ou une version ultérieure.

Aucune bibliothèque externe n'est nécessaire.

## Installation

Clone le dépôt :

```bash
git clone https://github.com/wwatson205/python.git
cd python
```

## Lancement

```bash
python main.py
```

## Exemples

```text
Toi > bonjour
Nova > Salut ! Je suis Nova AI.

Toi > calcule 12 * (5 + 3)
Nova > Résultat : 56

Toi > retiens que Paris est une capitale
Nova > D'accord, je retiens que Paris est une capitale.

Toi > que sais-tu sur Paris
Nova > Dans ma mémoire, paris est une capitale.
```

## Tests

```bash
python -m unittest -v
```

## Confidentialité

Les informations mémorisées sont enregistrées localement
dans `data/memory.json`. Ne publie pas de données personnelles.

## Licence

MIT
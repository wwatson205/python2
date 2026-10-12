import ast
import json
import operator
import random
import re
from datetime import datetime
from pathlib import Path

APP_NAME = "Nova AI"
DATA_DIR = Path(__file__).parent / "data"
MEMORY_FILE = DATA_DIR / "memory.json"

# Opérations autorisées dans la calculatrice.
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression):
    """Évalue une expression mathématique sans utiliser eval()."""
    if len(expression) > 100:
        raise ValueError("Expression trop longue.")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Nombre invalide.")
            return node.value

        if isinstance(node, ast.BinOp):
            op = OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError("Opération interdite.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow):
                if abs(right) > 10 or abs(left) > 1_000_000:
                    raise ValueError("Puissance trop grande.")

            result = op(left, right)

            if abs(result) > 1e100:
                raise ValueError("Résultat trop grand.")
            return result

        if isinstance(node, ast.UnaryOp):
            op = OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError("Opération interdite.")
            return op(evaluate(node.operand))

        raise ValueError("Expression non autorisée.")

    return evaluate(tree)


class NovaAI:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.memory = self.load_memory()

    def load_memory(self):
        if not MEMORY_FILE.exists():
            return {"facts": {}, "history": []}

        try:
            data = json.loads(
                MEMORY_FILE.read_text(encoding="utf-8")
            )
            if not isinstance(data, dict):
                raise ValueError("Mémoire invalide")

            data.setdefault("facts", {})
            data.setdefault("history", [])
            return data
        except (OSError, ValueError, json.JSONDecodeError):
            print("Mémoire illisible : démarrage avec une mémoire vide.")
            return {"facts": {}, "history": []}

    def save_memory(self):
        MEMORY_FILE.write_text(
            json.dumps(
                self.memory,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    def remember(self, key, value):
        self.memory["facts"][key] = value
        self.save_memory()

    def respond(self, message):
        original = message.strip()
        text = original.lower()

        if not original:
            return "Écris un message pour commencer."

        # Mémoriser une information.
        match = re.fullmatch(
            r"retiens que ([a-zA-ZÀ-ÿ0-9 _-]{1,40}) "
            r"est (.{1,200})",
            original,
            flags=re.IGNORECASE
        )
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            self.remember(key, value)
            return f"D'accord, je retiens que {key} est {value}."

        # Interroger la mémoire.
        match = re.fullmatch(
            r"(?:que sais-tu sur|qui est) (.{1,100})\??",
            text
        )
        if match:
            key = match.group(1).strip().lower()
            value = self.memory["facts"].get(key)
            if value is not None:
                return f"Dans ma mémoire, {key} est {value}."
            return "Je ne connais pas encore cette information."

        if text in {"bonjour", "salut", "hello", "coucou"}:
            return random.choice([
                "Bonjour ! Comment puis-je t'aider ?",
                "Salut ! Je suis Nova AI.",
                "Hello ! Que souhaites-tu faire aujourd'hui ?"
            ])

        if "ton nom" in text or "qui es-tu" in text:
            return (
                "Je suis Nova AI, une intelligence artificielle "
                "expérimentale écrite en Python."
            )

        if "quelle heure" in text:
            return datetime.now().strftime(
                "Il est %H:%M:%S."
            )

        if text in {"aide", "/help", "help"}:
            return (
                "Commandes disponibles :\n"
                "- calcule 12 * (5 + 3)\n"
                "- retiens que Paris est une ville\n"
                "- que sais-tu sur Paris\n"
                "- mémoire\n"
                "- oublier Paris\n"
                "- aide\n"
                "- quitter"
            )

        # Calculatrice : seulement les caractères mathématiques utiles.
        if text.startswith("calcule "):
            expression = text[len("calcule "):].strip()
            if not re.fullmatch(r"[0-9+\-*/().% \t]+", expression):
                return "Expression invalide. Exemple : calcule 2 + 3 * 4"
            try:
                result = calculate(expression)
                return f"Résultat : {result}"
            except (ValueError, SyntaxError, ZeroDivisionError,
                    OverflowError):
                return "Je ne peux pas calculer cette expression."

        if text == "mémoire":
            facts = self.memory["facts"]
            if not facts:
                return "Ma mémoire est vide."
            return "Informations mémorisées :\n" + "\n".join(
                f"- {key} : {value}"
                for key, value in facts.items()
            )

        match = re.fullmatch(r"oublier (.{1,100})", text)
        if match:
            key = match.group(1).strip().lower()
            if key in self.memory["facts"]:
                del self.memory["facts"][key]
                self.save_memory()
                return f"J'ai oublié l'information sur {key}."
            return f"Je n'avais aucune information sur {key}."

        # Réponses simples à règles.
        if any(word in text for word in ("merci", "je te remercie")):
            return "Avec plaisir !"

        if "météo" in text:
            return (
                "Je n'ai pas encore accès aux données météo en direct. "
                "Cette fonction pourrait être ajoutée plus tard."
            )

        return (
            "Je ne connais pas encore la réponse à cette question. "
            "Essaie « aide » pour voir mes commandes."
        )

    def chat(self):
        print(f"\n{'=' * 35}")
        print(f"  Bienvenue sur {APP_NAME}")
        print("  Tape « aide » pour les commandes.")
        print("  Tape « quitter » pour terminer.")
        print(f"{'=' * 35}\n")

        while True:
            try:
                message = input("Toi > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nNova > À bientôt !")
                break

            if message.lower() in {"quitter", "exit", "quit"}:
                print("Nova > À bientôt !")
                break

            response = self.respond(message)
            self.memory["history"].append({
                "user": message,
                "assistant": response,
                "time": datetime.now().isoformat(timespec="seconds")
            })

            # Conserver les 100 derniers échanges.
            self.memory["history"] = self.memory["history"][-100:]
            self.save_memory()

            print(f"Nova > {response}\n")


if __name__ == "__main__":
    NovaAI().chat()
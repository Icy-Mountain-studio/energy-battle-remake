# Project Ark & The Noah Kernel

Welcome to **Energy War - Remake**, a classic turn-based strategy game brought to life in your terminal! At its heart, this project is a tale of two key components:

*   **Ark (`ark.py`)**: The frontend and game-specific logic for "Energy War". It defines the rules, the actions, and the player experience.
*   **Noah (`noah.py`)**: The powerful, decoupled, turn-based game kernel that drives the action. It's the engine under the hood.

This document focuses primarily on the **Noah Kernel**, the architectural centerpiece of this project.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
![Status](https://img.shields.io/badge/status-in_development-orange)

---

## ✨ Features

*   **Classic Turn-Based Combat**: Engage in tactical battles with multiple AI opponents.
*   **Resource Management**: Juggle your energy to perform powerful actions.
*   **Positional Strategy**: Move between different layers of the battlefield to gain an advantage.
*   **Highly Extensible Game Logic**: Thanks to the Noah Kernel, adding new actions or changing game rules is surprisingly simple.
*   **Pure Python, Zero Dependencies**: Runs anywhere Python does, right out of the box.

## 🚀 The Noah Kernel: An Architectural Deep Dive

The Noah Kernel is more than just a backend; it's a design philosophy. The core principle is the **strict separation of the game engine from the game logic**. Noah knows *how* to run a turn-based game, but it has no idea *what* the game is about. It doesn't know about "shooting" or "defending"; it only knows about "Actions" with priorities, costs, and execution steps.

This makes the kernel incredibly reusable for other turn-based games.

### 的核心组件 (Key Components)

The kernel is built around a few elegant core classes:

1.  **`Core`**: The master conductor. This class orchestrates the entire game flow. It holds the game state (`BattleEnv`), manages all players (`PlDict`), and processes the main game loop turn after turn.

2.  **`Player`**: Represents any participant in the game. It tracks state like HP, energy, position, and the actions chosen for the current turn. It can be a human or an AI.

3.  **`Act`**: A data object representing a single action chosen by a player (e.g., "Player 1 chose to perform Action '1'"). It's a lightweight container for what needs to be done.

4.  **`IO`**: A surprisingly versatile Input/Output handler. It manages all terminal output, including text formatting, dynamic string substitution (`$0`, `$1`), and even that cool typewriter effect!

### 🔄 The Lifecycle of a Turn

A single turn in the Noah Kernel follows a clear, predictable lifecycle, managed entirely by the `Core` object:

1.  **Selection Phase (`SelectAct`)**: The kernel iterates through every active player. For each player, it determines a list of possible actions and their AI weights (for decision-making). It then prompts human players for input or uses a weighted random choice for AI players. The chosen actions are registered in the `ActSign` registry, sorted by priority.

2.  **Resolution Phase (`DealAct`)**: This is where the magic happens. The kernel processes the registered actions in strict order of their **priority** (higher priority numbers go first). Actions with the same priority are resolved together. This is where attacks land, defenses are checked, and players move.

3.  **Cleanup Phase (`rm_deaths`, `clean_round`)**: The kernel removes any players whose HP has dropped to zero, announces the casualties, and then resets all temporary turn-based states (like a player's "defending" status) to prepare for the next round.

This loop continues until a victory condition is met.

### 🤖 The Data-Driven Heart: The `ActDict`

How does Noah remain game-agnostic? The secret is the **Action Dictionary (`ActDict`)**.

When `ark.py` initializes the `Core`, it passes a large dictionary that defines every single possible action in the game. Noah simply reads this dictionary to understand the "rules of the world."

Here's a simplified look at the structure for a single action:

```python
"1": { // The key players type to select this action
    "price": charge_price,      // A function to calculate the energy cost
    "priority": 0,              // Execution priority (higher runs first)
    "able": able_forever,       // A function that returns True if the action is usable
    "ai": charge_ai,            // A function that returns a weight for AI decision-making
    "s_exec": charge_s,         // The function to run during the Selection phase
    "d_exec": [charge_d],       // A list of functions to run during the Resolution phase
},

By changing this dictionary, you can fundamentally change the game without ever touching the noah.py kernel file.
⛓️ The Resolution Pipeline: d_exec & StreamProcessor

This is arguably the most powerful feature of the Noah Kernel.

Notice that d_exec is a list of functions. When an action is resolved, the kernel doesn't just call one function. Instead, it uses the StreamProcessor to create a processing pipeline.

The StreamProcessor takes an initial data stream (e.g., information about an attack) and passes it to the first function in the list. The output of that function becomes the input for the second function, and so on.

Let's take ark.py's Shoot action as a perfect example. Its d_exec list is:
*.py
Python

"d_exec": [
    crossfire_evaluate,  // 1. Calculate initial damage and who gets hit.
    crossfire_crash,     // 2. Check if a target is also shooting back, and annihilate projectiles.
    crossfire_reflect,   // 3. Check if the target reflected the damage.
    crossfire_defend,    // 4. Check if the target defended, reducing damage.
    crossfire_final      // 5. Apply the final, calculated damage and print results.
]

This pipeline approach makes complex interactions clean, readable, and easy to modify. Want to add a new "Dodge" mechanic? Just insert a crossfire_dodge function into the pipeline!
🎮 How Ark Uses Noah

ark.py serves as the perfect example of a "client" for the Noah Kernel. Its main responsibilities are:

    Defining the Expression dictionary with all the game's text for the IO class.
    Defining the InitBattleEnv dictionary with the game's initial parameters (player count, map size, etc.).
    Defining the master BaseActDict which contains all game actions, linking them to their respective logic functions.
    Initializing the noah.Core with this environment and these actions.
    Starting the main game loop.

🛠️ Getting Started

You don't need any special libraries, just Python!

    Clone the repository:

*.bash
Shell

git clone <your-repo-url>
cd <your-repo-folder>

Run the game:
*.bash
Shell

    python ark.py

    That's it! Follow the on-screen instructions and start your battle.

🤝 How to Contribute

This project is a work in progress and all contributions are welcome! Whether it's adding a new action, fixing a bug, or improving the documentation, feel free to:

    Fork the repository.
    Create a new branch (git checkout -b feature/your-amazing-feature).
    Make your changes and commit them (git commit -m 'Add some amazing feature').
    Push to the branch (git push origin feature/your-amazing-feature).
    Open a Pull Request.

📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

A final note from the creator: This project was born from a love for classic games and clean code. It has been rewritten multiple times to arrive at the current architecture with the Noah kernel at its center. It's still far from complete, but hopefully, its design can be as fun to explore as the game is to play!

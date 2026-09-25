# Energy Battle - Remake

🌐 [简体中文 (Simplified Chinese)](README_zh.md)

**Energy Battle - Remake** is a highly customizable, turn-based, command-line strategy game written in Python. Powered by a custom-built game engine known as the **Noah Kernel**, this game supports complex multi-agent combat, allowing human players to fight alongside or against multiple AI opponents in a layered battlefield.

## ✨ Features

- **Strategic Turn-Based Combat:** Manage your Health Points (HP), Energy, and Position (Levels/Floors) to outsmart your opponents.
- **Rich Action System:** A rock-paper-scissors-like deep combat system including actions like *Charge*, *Shoot*, *Defend*, *Move*, *Reflect*, *Energy Wave*, and *Black Hole*.
- **Noah Kernel & Ark Frontend:** A robust, modular architecture designed for extensibility.
- **In-Game Modding & Settings:** Dynamically change game rules (HP, map size, AI teams) and hot-swap mods without restarting the game.
- **Immersive CLI UI:** Typewriter text effects, ANSI-colored outputs, and auto-collapsing battle logs for a clean experience.
- **Multi-language Support:** Native support for English, Simplified Chinese, Traditional Chinese, and Japanese.

## 📋 Requirements

- **Python 3.12 or higher** is strictly required.
- A terminal/command prompt that supports ANSI colors (most modern terminals on Windows, macOS, and Linux do).
- No third-party dependencies required! (Built entirely with Python standard libraries).

## 🚀 Installation & Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/Ryzdump/energy-battle-remake.git
   ```
2. Navigate into the project directory:
   ```bash
   cd energy-battle-remake
   ```
3. Run the game via the Ark frontend:
   ```bash
   python ark.py
   ```
   *(Upon running, you will be prompted to select your preferred language.)*

## 🎮 How to Play

By default, the game pits 1 human player against 9 AI players in a free-for-all battle. 

Every turn, you must input the number corresponding to the action you want to take. If you just press `Enter` without typing anything, your AI assistant will make the best decision for you.

### Core Resources:
- **HP:** You are eliminated when this reaches 0.
- **Energy:** Used to pay for attacks and advanced skills. Gathered by *Charging*.
- **Position:** The map consists of multiple vertical levels. You can only hit enemies if you aim in the correct direction (Up, Straight, Down) and if they are within range.

### Basic Actions (Cost):
1. **Charge (+1 Energy):** Draw energy from the void.
2. **Shoot (1 Energy/shot):** Fire up to 3 energy projectiles at a target.
3. **Defend (0 Energy):** Block incoming damage for the current turn.
4. **Move (1 Energy):** Change your vertical position to dodge or chase.
5. **Reflect (2 Energy):** Bounce incoming attacks back to the attacker.
6. **Energy Wave (6 Energy):** A devastating Area-of-Effect (AoE) attack.
7. **Black Hole (5 Energy):** Completely swallow and disable a target's action for the turn.

*(You can view detailed rules in-game by selecting the "View Game Rules" action).*

## 🛠️ Mod Development

Want to create your own actions, tweak the kernel, or write new admin tools? The Noah Kernel is built from the ground up for modding!

Check out the official **[Mod Development Guide](MODDING.md)** to get started.

## 📜 License

This project is open-sourced under the [MIT License](LICENSE).



# 🟡 PyPacman – A Custom Pacman Clone

**PyPacman** is a fully playable Pacman clone built in Python using **PyQt5**. While inspired by the original arcade classic, all visual assets in this version were custom-made. This project showcases the combination of Python game logic and a GUI framework to create a fun, retro-style gaming experience.

![Game Preview](pacman.jpg)

---

## 🎮 Features

* 🧠 **Classic Pacman Gameplay**: Eat points, dodge ghosts, and collect power-ups.
* 👾 **Custom Ghost AI**: Ghosts move semi-randomly with basic collision and respawn logic.
* 💥 **Power Mode**: Turn the tables by eating a power-up and chasing the ghosts instead.
* 💾 **High Score System**: Persistent leaderboard saved to file.
* 🧱 **Tile-Based Map**: Readable and editable map structure via text files.
* ❤️ **Lives System**: Start with 3 lives. Game over when they’re gone.
* 🔄 **Restart Option**: Press `R` after game over to try again.
* ⬜ **Fullscreen Toggle**: Press `F11` to toggle fullscreen.
* 💻 **Custom Graphics**: All game assets and sprites were made by the developer.

---

## 🕹️ Controls

| Key   | Action                     |
| ----- | -------------------------- |
| `W`   | Move Up                    |
| `A`   | Move Left                  |
| `S`   | Move Down                  |
| `D`   | Move Right                 |
| `R`   | Restart after Game Over    |
| `ESC` | Quit the Game & Save Score |
| `F11` | Toggle Fullscreen Mode     |

---

## 🧠 How It Works

* The game loop runs via a **QTimer**, updating both player and ghost states.
* Player and ghost movements are grid-based and follow tile-based collision rules.
* The map is read from a text file, allowing easy level design.
* When a player collects all `•` and `@` points on the map, the level is reloaded.
* High scores are stored in a plain text file, keeping the top 10 results.

## ✅ To Do

* [ ] Implement a **Load Game** feature in the main menu
* [ ] Add **Sound Effects / Music** (currently commented out)
* [ ] Create a **GUI-based Main Menu**
* [ ] Improve **Ghost AI** pathfinding

---

## 📦 License

This project is created by **Willi Müller** for educational and entertainment purposes. All artwork included is original.

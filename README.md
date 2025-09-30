# 🛒 Supermarket Showdown: An AI Educational Game

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-complete-brightgreen.svg)

Welcome to **Supermarket Showdown**, a turn-based educational game designed to teach financial literacy concepts through the practical application of Artificial Intelligence search algorithms. This project was developed as a submission for the Artificial Intelligence course at the Federal University of Technology - Paraná (UTFPR).

The game challenges you to a shopping duel against an intelligent AI agent. With a shared product inventory and a randomly assigned target budget each round, you must think strategically to fill your cart and get closer to the target value than the AI. Can you outsmart the machine?

***

## 📋 Table of Contents
* [Live Preview](#-live-preview)
* [✨ Key Features](#-key-features)
* [🧠 The AI Engine: A* vs. Greedy Search](#-the-ai-engine-a-vs-greedy-search)
* [🛠️ Tech Stack](#-tech-stack)
* [🚀 Getting Started](#-getting-started)
* [🎮 How to Play](#-how-to-play)
* [📂 Project Structure](#-project-structure)
* [Acknowledgements](#-acknowledgements)

---

## 🎥 Live Preview

Get a glimpse of the gameplay! The AI's choices and final results differ significantly based on the algorithm you select.

<p align="center">
  <b>Greedy Search in Action (Fast but Shortsighted)</b><br>
  <em>The Greedy algorithm gets close to the R$50.50 target but settles for R$50.00, unable to find a perfect match with its next best move.</em><br>
  <img src="[https://i.imgur.com/uS3hY7g.png](https://i.imgur.com/uS3hY7g.png)" alt="Greedy Search Simulation" width="400"/>
</p>

<p align="center">
  <b>A* Search in Action (Strategic and Optimal)</b><br>
  <em>The A* algorithm plans ahead, finding the perfect combination of items to hit the R$50.50 target exactly.</em><br>
  <img src="[https://i.imgur.com/46VlSjX.png](https://i.imgur.com/46VlSjX.png)" alt="A* Search Simulation" width="400"/>
</p>

> A GIF showcasing the turn-based gameplay and voice command features would be a great addition here!

---

## ✨ Key Features

* **♟️ Strategic Turn-Based Gameplay:** You add an item, then the AI adds an item. With a shared and limited stock for all products, every choice matters!
* **🤖 Dual AI Opponents:** Choose your challenge! Pit your wits against two classic search algorithms:
    * **Greedy Search:** A fast, impulsive AI that always makes the move that looks best right now.
    * **A\* Search:** A clever, strategic AI that plans multiple steps ahead to find the optimal path to the target value.
* **🖥️ Interactive Graphical Interface:** A user-friendly and visually appealing GUI built with Python's native Tkinter library.
* **🎤 Voice Commands:** Add and remove items from your cart hands-free! The game uses speech recognition with fuzzy string matching to understand you, even with imprecise pronunciation.
* **🔊 Audio Feedback:** The game provides audio feedback, including a text-to-speech feature to announce your remaining balance.
* **🧾 Dynamic Gameplay:** With a randomized target value and product inventory for every round, no two games are ever the same.

---

## 🧠 The AI Engine: A\* vs. Greedy Search

[cite_start]This project's core is the implementation and comparison of two informed search algorithms[cite: 24]. [cite_start]The problem is modeled as a state-space search where the goal is to find a set of products (a path) whose total cost is as close as possible to the target value[cite: 25, 209].

### Greedy Search

[cite_start]The Greedy algorithm is a "myopic" or shortsighted strategy[cite: 222]. [cite_start]At every turn, it asks: "Which single product can I add to my cart right now to get my total *as close as possible* to the target?"[cite: 96, 98]. It doesn't think about future moves.

* [cite_start]**Strategy:** Minimize the heuristic function $h(n)$ at each step[cite: 211, 212].
* [cite_start]**Heuristic $h(n)$:** The absolute difference between the target value and the current cart total, multiplied by a constant factor to balance its magnitude[cite: 86, 91].
    $$
    h(n) = | \text{target\_value} - \text{current\_total} | * 100
    $$

### A\* Search

[cite_start]The A\* algorithm is far more strategic[cite: 52]. [cite_start]It seeks to find the absolute best *combination* of products[cite: 53]. [cite_start]It evaluates nodes by combining the cost of the path so far with an estimate of the cost remaining to reach the goal[cite: 214].

* [cite_start]**Strategy:** Minimize the evaluation function $f(n)$, which balances path cost and the heuristic[cite: 57, 125].
    $$
    f(n) = g(n) + h(n)
    $$
* [cite_start]**Path Cost $g(n)$:** The number of items currently in the cart[cite: 56, 126]. [cite_start]This serves as a tie-breaker, favoring solutions with fewer products[cite: 127].
* [cite_start]**Heuristic $h(n)$:** The same heuristic as the Greedy search, estimating the remaining "distance" to the target value[cite: 55, 129].

[cite_start]As demonstrated in the project, **A\*** consistently delivers more optimal and precise results by planning its path in advance[cite: 215, 221].

---

## 🛠️ Tech Stack

* [cite_start]**Core Language:** **Python** [cite: 65]
* [cite_start]**Graphical Interface (GUI):** **Tkinter** [cite: 31, 66]
* **AI & Logic:**
    * **heapq:** For the priority queue (min-heap) in the A\* search implementation.
* **Voice & Audio:**
    * [cite_start]**gTTS (Google Text-to-Speech):** For converting text announcements into speech[cite: 68].
    * [cite_start]**playsound:** For playing the generated audio files[cite: 69].
    * [cite_start]**SpeechRecognition:** For capturing and processing microphone input[cite: 71].
* **Text Processing:**
    * [cite_start]**thefuzz:** For fuzzy string matching, allowing for robust voice command recognition[cite: 72].
    * [cite_start]**unidecode:** For removing accents from strings to standardize text for comparison[cite: 73].

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

* Python 3.8 or newer
* `pip` (Python package installer)
* A working microphone for voice commands.

### Installation & Execution

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/supermarket-showdown.git
    cd supermarket-showdown
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```sh
    pip install tkinter gTTS playsound SpeechRecognition thefuzz unidecode
    ```
    *Note: You may also need to install `PyAudio` if `SpeechRecognition` fails, and on some Linux systems, you might need `portaudio` (`sudo apt-get install portaudio19-dev`).*

4.  **Run the application:**
    ```sh
    python mercadoFinal.py
    ```

---

## 🎮 How to Play

1.  Launch the game by running the `mercadoFinal.py` script.
2.  On the welcome screen, select the AI algorithm you want to compete against ("Algoritmo A\*" or "Busca Gulosa").
3.  Click **INICIAR JOGO** to start a new round.
4.  The game is turn-based. [cite_start]On your turn, you can add **one** item to your cart[cite: 19].
5.  **Add items** by clicking the "Adicionar" button on a product card or by using the microphone button to say "add [product name]".
6.  [cite_start]After your move, the AI will take its turn, and the shared product stock will be updated[cite: 20].
7.  The goal is to get your total cart value closer to the **VALOR-ALVO** (Target Value) than the robo. The player with the smallest absolute difference wins. [cite_start]In case of a tie, the player with fewer items in their cart wins[cite: 56, 127].

---

## 📂 Project Structure
.
├── mercadoFinal.py        # The main Python script containing all game logic and GUI code.
└── RelatorioFinal.pdf     # The original technical report (in Portuguese) detailing the project's development.

---

## 🙏 Acknowledgements

* [cite_start]This project was created by **Emanuel Henrique de Macedo** and **Geraldo Baranoski Junior**[cite: 2, 3].
* [cite_start]Developed for the Artificial Intelligence course at the **Universidade Tecnológica Federal do Paraná (UTFPR)**[cite: 1, 15].

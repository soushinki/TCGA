# Official Game Rules of Shadowverse (Classic)

This document outlines the core rules for the classic version of the Shadowverse TCG. It is based on the official Game Guide and expanded with the community Fandom wiki. This serves as the design blueprint for the `SvEngine`.

### 1. The Objective

A player wins the game by achieving one of the following conditions:
* The enemy leader's defense is reduced from **20** to **0**.
* The opponent is forced to draw a card but has no cards left in their deck ("deck out").
* A card or effect's **special win condition** is met.

### 2. Starting the Game

* **Deck Size:** 40 cards. A maximum of 3 copies of any single card is allowed.
* **Starting Hand:** Both players draw **3 cards**.
* **Mulligan:** Players can choose any cards in their opening hand to shuffle back into the deck, then draw an equal number of new cards.
* **Going First vs. Second:**
    * The 1st Player draws **one card** on their first turn.
    * The 2nd Player draws **two cards** on their first turn.

### 3. The Turn Cycle

1.  **Start of Turn:**
    * Gain 1 empty Play Point Orb (up to a maximum of 10).
    * Refill all Play Points to match the current maximum.
    * Draw one card.
    * Handle any "start of your turn" effects.
2.  **Main Phase:**
    * The player can take actions in any order: play cards, attack with followers, and evolve (once per turn).
3.  **End of Turn:**
    * The player taps the "End Turn" button.
    * Handle any "end of your turn" effects.

### 4. Resources

* **Play Points (PP):** The primary resource for playing cards.
* **Evolution Points (EP):** The secondary resource for evolving followers.
    * **1st player:** Gets **2 EP**, usable from **Turn 5**.
    * **2nd player:** Gets **3 EP**, usable from **Turn 4**.

### 5. The Board (Area) & Combat

* **Board Size:** A maximum of **5 cards** (followers and/or amulets) per player.
* **Combat:** Followers attack targets; damage is simultaneous and persists. A follower is destroyed when its defense reaches 0.
* **Summoning Sickness:** A follower cannot attack on the turn it is played unless it has **Storm** or **Rush**.

### 6. Evolution Mechanic

* A player can spend 1 EP to evolve one of their followers **once per turn**.
* Evolving grants a stat boost, **Rush** (allowing it to attack enemy followers), and may trigger special `on_evolve` effects.

### 7. Card Types

* **Followers:** Stay on the board to attack and defend.
* **Spells:** One-time effects.
* **Amulets:** Stay on the board and provide persistent effects.

### 8. Core Keywords and Abilities

* **Fanfare:** An effect that triggers when the card is played from your hand.
* **Last Words:** An effect that triggers when the card is destroyed.
* **Ward:** Enemy followers must attack followers with this keyword first.
* **Storm:** Can attack both followers and the enemy leader on the turn it is played.
* **Rush:** Can **only** attack enemy followers on the turn it is played.
* **Bane:** Instantly destroys any follower it deals damage to.
* **Drain:** Heals your leader for the amount of damage this follower deals.
* **Aura:** Cannot be targeted by enemy spells or effects.
* **Ambush:** The follower cannot be attacked or targeted by enemy spells or effects until it attacks.
* **Accelerate:** An effect on a high-cost follower that allows you to play it as a spell with a lower PP cost.
* **Crystallize:** An effect on a high-cost follower that allows you to play it as an amulet with a lower PP cost.
* **Countdown:** A property of some Amulets that causes their **Last Words** to trigger after a set number of turns.

### 9. Class Identity & Mechanics

Each of the 8 classes has a unique core mechanic the engine must model.
* **Forestcraft:** Effects are based on the **number of cards played** in a single turn.
* **Swordcraft:** Focuses on two distinct follower types: **Officers** and **Commanders**.
* **Runecraft:** Utilizes **Spellboost**, which powers up cards in hand whenever a spell is played.
* **Dragoncraft:** Uses **Overflow**, a state that is active when the player has 7 or more max PP.
* **Shadowcraft:** Manages **Necromancy**, which spends "shadows" (cards in the cemetery) to pay for effects.
* **Bloodcraft:** Manages **Vengeance**, a state that is active when the player's leader has 10 or less defense.
* **Havencraft:** Specializes in **Countdown Amulets**.
* **Portalcraft:** Manages **Resonance**, a state that alternates each time a card is drawn from the deck.
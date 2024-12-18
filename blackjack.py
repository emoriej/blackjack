import requests
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk  # Install with `pip install pillow`

# API Base URL
API_URL = "https://deckofcardsapi.com/api/deck"

class Card:
    def __init__(self, value, suit, image_url):
        self.value = value
        self.suit = suit
        self.image_url = image_url

    def __str__(self):
        return f"{self.value} of {self.suit}"

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack with API")
        self.deck_id = self.create_deck()
        self.players = [[] for _ in range(4)]  # 4 players
        self.current_player = 0

        self.message = tk.Label(root, text="Welcome to Blackjack!", font=("Arial", 16))
        self.message.pack(pady=10)

        self.card_display = tk.Frame(root)
        self.card_display.pack()

        self.controls = tk.Frame(root)
        self.controls.pack()
        tk.Button(self.controls, text="Hit", command=self.hit).grid(row=0, column=0, padx=5)
        tk.Button(self.controls, text="Stand", command=self.stand).grid(row=0, column=1, padx=5)

        self.start_game()

    def create_deck(self):
        """Create a new deck and return the deck ID."""
        response = requests.get(f"{API_URL}/new/shuffle/?deck_count=1")
        response.raise_for_status()
        return response.json()["deck_id"]

    def draw_cards(self, count):
        """Draw cards from the deck."""
        response = requests.get(f"{API_URL}/{self.deck_id}/draw/?count={count}")
        response.raise_for_status()
        cards_data = response.json()["cards"]
        return [Card(card["value"], card["suit"], card["image"]) for card in cards_data]

    def start_game(self):
        """Initialize hands for all players."""
        for i in range(4):  # Deal 2 cards to each player
            self.players[i] = self.draw_cards(2)
        self.update_ui()

    def calculate_hand_value(self, hand):
       """Calculate the total value of a hand."""
       value = 0
       aces = 0
       for card in hand:
           if card.value in ['JACK', 'QUEEN', 'KING']:
               value += 10
           elif card.value == 'ACE':
               value += 11
               aces += 1
           else:
               value += int(card.value)
       
       # Adjust for Aces if the total value exceeds 21
       while value > 21 and aces > 0:
           value -= 10
           aces -= 1
       
       return value


    def update_ui(self):
        """Update the game UI."""
        for widget in self.card_display.winfo_children():
            widget.destroy()

        current_hand = self.players[self.current_player]
        for card in current_hand:
            response = requests.get(card.image_url)
            card_image = Image.open(BytesIO(response.content))
            card_image = card_image.resize((100, 150))  # Resize for display
            tk_image = ImageTk.PhotoImage(card_image)

            label = tk.Label(self.card_display, image=tk_image)
            label.image = tk_image  # Keep reference to avoid garbage collection
            label.pack(side=tk.LEFT, padx=5)

        hand_value = self.calculate_hand_value(self.players[self.current_player])
        self.message.config(text=f"Player {self.current_player + 1}'s turn! Hand value: {hand_value}")

    def hit(self):
       """Add a card to the current player's hand."""
       self.players[self.current_player].append(self.draw_cards(1)[0])
       hand_value = self.calculate_hand_value(self.players[self.current_player])
       if hand_value > 21:
           self.message.config(text=f"Player {self.current_player + 1} busts! Moving to next player...")
           self.current_player = (self.current_player + 1) % 4
           self.update_ui()

       else:
           self.update_ui()

    def stand(self):
        """Move to the next player's turn."""
        self.current_player = (self.current_player + 1) % 4
        self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()

"""War_game module."""
from random import shuffle

from card_deck_manager.card import Card
from card_deck_manager.exceptions.stack_exceptions import NoSuchCardError
from card_deck_manager.game import Game
from card_deck_manager.player import Player
from card_deck_manager.stack import BOTTOM, RANDOM, Stack


class WarGame(Game):
    """Represents a war game."""

    def __init__(self, initial_decks_cards: list[list[Card]] | None = None) -> None:
        """Init war object."""
        super().__init__(players=self.create_players(), initial_decks_cards=initial_decks_cards)
        self.p1 = self.players[0]
        self.p2 = self.players[1]
        self.war_prize: Stack = Stack("War prize")

    @staticmethod
    def create_players() -> list[Player]:
        """Create both players."""
        p1 = Player(name="Player1", stack_names=["Cards to play", "War cards"])
        p2 = Player(name="Player2", stack_names=["Cards to play", "War cards"])
        return [p1, p2]

    @staticmethod
    def pick_won_cards(winner: Player, won_cards: list[Card]) -> None:
        """Shuffle and pick won cards."""
        shuffle(won_cards)
        winner.stacks["Cards to play"].add_cards(new_cards=won_cards, position=BOTTOM)

    @staticmethod
    def safe_pick_card(player: Player, other_player: Player) -> Card:
        """Pick a card if exists else, draw random card in other_player stack."""
        try:
            return player.stacks["Cards to play"].pick_card()
        except NoSuchCardError:
            player.draw_card(
                origin_stack=other_player.stacks["Cards to play"],
                dest_stack=player.stacks["Cards to play"],
                origin_position=RANDOM,
            )
            return player.stacks["Cards to play"].pick_card()

    def initiate_game(self) -> None:
        """Initiate the game."""
        deck = self.dealer.decks[0]
        deck.shuffle()
        while deck:
            self.dealer.give_card(deck=deck, dest_stack=self.p1.stacks["Cards to play"])
            self.dealer.give_card(deck=deck, dest_stack=self.p2.stacks["Cards to play"])

    def war(self, c1: Card, c2: Card) -> None:
        """Handle war mecanic."""
        self.p1.stacks["War cards"].add_cards(
            [
                c1,
                self.safe_pick_card(player=self.p1, other_player=self.p2),
            ],
        )
        self.war_prize.add_cards(new_cards=self.p1.stacks["War cards"].empty())
        c1 = self.safe_pick_card(player=self.p1, other_player=self.p2)
        self.p2.stacks["War cards"].add_cards(
            [
                c2,
                self.safe_pick_card(player=self.p2, other_player=self.p1),
            ],
        )
        self.war_prize.add_cards(new_cards=self.p2.stacks["War cards"].empty())
        c2 = self.safe_pick_card(player=self.p2, other_player=self.p1)
        if c1 > c2:
            self.pick_won_cards(winner=self.p1, won_cards=[c1, c2, *self.war_prize.empty()])
        elif c1 < c2:
            self.pick_won_cards(winner=self.p2, won_cards=[c1, c2, *self.war_prize.empty()])
        elif c1 == c2:
            self.war(c1, c2)

    def play_round(self) -> None:
        """Play a round."""
        c1 = self.p1.stacks["Cards to play"].pick_card()
        c2 = self.p2.stacks["Cards to play"].pick_card()
        if c1 > c2:
            self.pick_won_cards(winner=self.p1, won_cards=[c1, c2])
        elif c1 < c2:
            self.pick_won_cards(winner=self.p2, won_cards=[c1, c2])
        elif c1 == c2:
            self.war(c1, c2)

    def get_winner(self) -> Player:
        """Get the winner object."""
        if self.p1.stacks["Cards to play"]:
            return self.p1
        return self.p2

    def run(self) -> None:
        """Run the game."""
        self.initiate_game()
        round_nb = 0
        while self.p1.stacks["Cards to play"] and self.p2.stacks["Cards to play"]:
            self.play_round()
            round_nb += 1
        print(f"Game is finished in {round_nb} rounds and {self.get_winner().name} won!")


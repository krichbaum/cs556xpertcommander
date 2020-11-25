from rlcard.games.thegame.utils import cards2list, targets2list
from rlcard.games.thegame.card import TheGameCard as Card

class TheGameRound(object):

    def __init__(self, dealer, num_players, np_random, deck_size=98):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''

        d_card = str(deck_size + 2)
        self.np_random = np_random
        self.dealer = dealer
        self.target = {'a1': Card('1'), 'a2': Card('1'), 'd1': Card(d_card), 'd2': Card(d_card)}
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False
        self.is_win = False
        # how many cards the current player has played in its turn
        self.num_cards_played = 0
        self.min_move_size = 2

    def proceed_round(self, players, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            players (list): list of Player
            action (str): string of legal action
        '''
        player = players[self.current_player]

        # player has ended their turn
        # draw cards and clear cards played this turn
        if action == 'draw':
            # draw cards
            # if deck is empty lower min move requirement
            self.dealer.deal_cards(player, num=self.num_cards_played)
            self.num_cards_played = 0
            if not self.dealer.deck:
                self.min_move_size = 1

                # check if any players have cards left
                # if not the game was a win
                player_cards_remaining = False
                for player in players:
                    if len(player.hand) > 0:
                        player_cards_remaining = True
                self.is_over = not player_cards_remaining
                self.is_win = self.is_over

            self.current_player = (self.current_player + self.direction) % self.num_players


        else:
            action_info = action.split('-')
            pile = action_info[0]
            rank = action_info[1]

            # remove corresponding card
            remove_index = player.hand.index(rank)
            card = player.hand.pop(remove_index)

            self.played_cards.append(card)
            self.num_cards_played += 1

            # update target
            self.target[pile] = card

    def get_legal_actions(self, players, player_id):
        legal_actions = []
        hand = players[player_id].hand

        # if card hasn't already been played then check which deck in can go to
        # -1 is a placeholder used for when the deck has been emptied
        for card in hand:
            # asending or +-10
            if card > self.target['a1'] or card.diff_ten(self.target['a1']):
                legal_actions.append('a1-' + card.rank)
            if card > self.target['a2'] or card.diff_ten(self.target['a2']):
                legal_actions.append('a2-' + card.rank)
            # descending or +-10
            if card < self.target['d1'] or card.diff_ten(self.target['d1']):
                legal_actions.append('d1-' + card.rank)
            if card < self.target['d2'] or card.diff_ten(self.target['d2']):
                legal_actions.append('d2-' + card.rank)

        # if there are no legal actions, the min amount of cards haven't been played
        # and there are still cards in the deck, the game has been lost
        if not legal_actions \
                and self.num_cards_played < self.min_move_size \
                and hand:
            self.is_over = True

        # if the player has played min number of cards, or does not have a hand, they may pass
        if self.num_cards_played >= self.min_move_size \
                or not hand:
            legal_actions.append('draw')

        return legal_actions

    def get_playable_cards(self):

        num_playable_cards = 0
        deck = self.dealer.deck

        for card in deck:
            # asending or +-10
            if card > self.target['a1'] or card.diff_ten(self.target['a1']):
                num_playable_cards += 1
            elif card > self.target['a2'] or card.diff_ten(self.target['a2']):
                num_playable_cards += 1
            # descending or +-10
            elif card < self.target['d1'] or card.diff_ten(self.target['d1']):
                num_playable_cards += 1
            elif card < self.target['d2'] or card.diff_ten(self.target['d2']):
                num_playable_cards += 1

        return num_playable_cards

    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            players (list): The list of TheGamePlayer
            player_id (int): The id of the player
        '''
        state = {}
        player = players[player_id]
        state['hand'] = cards2list(player.hand)
        state['target'] = targets2list(self.target) # a1, a2, d1, d2
        playable_cards = []

        # have to make sure you include cards in other player's hands
        for other_player in players:
            if other_player is player:
                pass
            else:
                playable_cards.extend(other_player.hand)

        playable_cards.extend(self.dealer.deck)
        state['playable_cards'] = cards2list(playable_cards)
        state['played_cards'] = cards2list(self.played_cards)
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        return state

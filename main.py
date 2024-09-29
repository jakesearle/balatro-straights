import random

RANKS = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
RANK_VALS = {
    'K': 13,
    'Q': 12,
    'J': 11,
}
ACE = 'A'


def default_deck():
    return RANKS * 4


def convert_to_set(hand_as_strs):
    cards = []
    for c in hand_as_strs:
        if c == ACE:
            cards.extend((1, 14))
        elif c.isdigit():
            cards.append(int(c))
        else:
            cards.append(RANK_VALS[c])
    return set(cards)


def hand_has_straight(hand, straight_length=5, shortcut=False):
    hand = convert_to_set(hand)

    # Recursively check from the top down if there's a straight
    def helper(curr_val=None, n_remaining=0):
        if n_remaining == 1:
            return True
        next_val = curr_val - 1
        if next_val in hand:
            return helper(curr_val=next_val, n_remaining=n_remaining - 1)
        if shortcut:
            next_val = curr_val - 2
            if next_val in hand:
                return helper(curr_val=next_val, n_remaining=n_remaining - 1)
        return False

    has_straight = any([helper(curr_val=start, n_remaining=straight_length) for start in hand])
    # if has_straight:
    #     print(hand)
    #     for c in hand:
    #         print(f'On {c}: {helper(curr_val=c, n_remaining=straight_length)}')
    return has_straight


def get_hand(deck, hand_size=8):
    deck_copy = deck.copy()
    random.shuffle(deck_copy)
    return deck_copy[:hand_size]


def evaluate_deck(deck):
    num_straight = 0
    for _ in range(100_000):
        hand = get_hand(deck)
        if hand_has_straight(hand):
            num_straight += 1
    print(f'{num_straight}/100_000')


def main():
    evaluate_deck(default_deck())


if __name__ == '__main__':
    main()

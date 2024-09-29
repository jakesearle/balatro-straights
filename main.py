import random
from collections import Counter

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


def hand_has_straight(hand, straight_length, shortcut):
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

    return any([helper(curr_val=start, n_remaining=straight_length) for start in hand])


def get_hand(deck, hand_size):
    deck_copy = deck.copy()
    random.shuffle(deck_copy)
    return deck_copy[:hand_size]


# Returns a success rate, the percentage of hands which contained a straight
def evaluate_deck(deck: list, n_tests: int, straight_length, has_shortcut, hand_size) -> float:
    return sum([1 for _ in range(n_tests) if hand_has_straight(get_hand(deck, hand_size), straight_length, has_shortcut)]) / n_tests


def create_new_generation(top_cut, cache, min_deck_size, num_children_per_parent):
    suggestion_sets = [suggest_children(t['deck'], num_children_per_parent) for t in top_cut]
    all_suggestions = set.union(*suggestion_sets)
    new_suggestions = all_suggestions.difference(cache)

    big_enough_decks = [q for q in new_suggestions if sum(q) >= min_deck_size]

    children = [{'deck': to_deck(q)} for q in big_enough_decks]
    return children


def suggest_children(deck, n_children):
    quantities = to_quantities(deck)
    children = set()
    for i in range(n_children):
        deck_copy = list(quantities)
        # These are not necessarily choices that a Balatro player would be presented with in-game, but rather just
        # ways to "switch up" the deck to try and test new things
        change = random.choice(['add_one', 'remove_one', 'remove_all', 'death', 'swap_all'])
        if change == 'add_one':
            random_i = random.randrange(0, len(deck_copy))
            deck_copy[random_i] += 1
        elif change == 'remove_one':
            random_i = random.randrange(0, len(deck_copy))
            if deck_copy[random_i] == 0:
                continue
            deck_copy[random_i] -= 1
        elif change == 'remove_all':
            random_i = random.randrange(0, len(deck_copy))
            deck_copy[random_i] = 0
        elif change == 'death':
            random_from = random.randrange(0, len(deck_copy))
            random_to = random.randrange(0, len(deck_copy))
            if deck_copy[random_from] == 0:
                continue
            deck_copy[random_from] -= 1
            deck_copy[random_to] += 1
        elif change == 'swap_all':
            random_from = random.randrange(0, len(deck_copy))
            random_to = random.randrange(0, len(deck_copy))
            deck_copy[random_from], deck_copy[random_to] = deck_copy[random_to], deck_copy[random_from]
        children.add(tuple(deck_copy))
    return children


# deck = ['A', '5', 'J',...]
# returns = [4, 5, ...] (Has 4 Aces, 5 Kings, etc.)
def to_quantities(deck):
    counter = Counter(deck)
    return tuple(counter[k] for k in RANKS)


def to_string(deck):
    qs = to_quantities(deck)
    strs = [f'{k}: {v}' for k, v in zip(RANKS, qs)]
    return ', '.join(strs)


def to_deck(quantities):
    deck = []
    for v, q in zip(RANKS, quantities):
        deck.extend([v] * q)
    return deck


def cache_generation(cache, generation):
    qs = [to_quantities(g['deck']) for g in generation]
    return cache.union(set(qs))


# If a score threshold isn't given, just try to beat how the starting deck does
def iterate(
        # Deck info
        starting_deck=None,  # A deck in the format ['A', 'K', '10', '2', 'A'...]
        min_deck_size=30,  # Minimum size the deck is allowed to be. (Without this, the optimal deck is just to have 5 cards that form a straight)
        straight_length=5,  # Number of cards required to form a straight
        has_shortcut=False,  # Straights may skip numbers. (Ace, Queen, Jack, 10, 8) would be a valid straight
        hand_size=8,  # Number of cards dealt in a hand

        # Testing info
        success_rate=None,  # If there's a chance of drawing a straight higher than this on the test, stop and output the generated deck
        num_test_hands=1_000,  # Number of hands which are dealt when testing. Higher number, more accurate result
        num_retained_per_generation=10,  # The nth best children from a generation which will be used to generate new decks
        num_children_per_parent=10):  # The number of children which are attempted to be generated from each "winner" in a generation

    if starting_deck is None:
        starting_deck = default_deck()
    if success_rate is None or not (0 < success_rate < 1):
        success_rate = evaluate_deck(starting_deck, num_test_hands, straight_length, has_shortcut, hand_size)
    if min_deck_size > len(starting_deck):
        min_deck_size = len(starting_deck)

    curr_gen = 1

    origin = {
        'deck': starting_deck
    }
    generation = [origin]
    cache = set()
    while True:
        print(f'Generation #{curr_gen} -- size: {len(generation)}')
        # Evaluate
        for child in generation:
            child['score'] = evaluate_deck(child['deck'], num_test_hands, straight_length, has_shortcut, hand_size)
        # Top cut
        top_cut = sorted(generation, key=lambda x: x['score'], reverse=True)[:num_retained_per_generation]
        if top_cut[0]['score'] >= success_rate:
            break

        # Generate new children
        cache = cache_generation(cache, generation)
        generation = create_new_generation(top_cut, cache, min_deck_size, num_children_per_parent)
        curr_gen += 1
    print(to_string(top_cut[0]['deck']))


def main():
    # Try to find a deck that will
    iterate(success_rate=.1)


if __name__ == '__main__':
    main()

import math
from collections import defaultdict
from tabulate import tabulate

def ranked_vote_verbose(user_preferences):

    def print_standings(round_number, focus_books=None):
        
        focus_books = focus_books or []
        
        print(f"Round {round_number}:")
        if focus_books:
            print(f"  Focus on: {', '.join(focus_books)}")

        for book, counts in sorted(vote_table.items(), key=lambda x: x[1][3], reverse=True):
            print(f"  {book}: {counts[3]} win counters")
        
        print("")  # Add an empty line for better readability

    def print_votetable(votetable):

        table = [(book, counts[0], counts[1], counts[2], counts[3]) for book, counts in votetable.items()]
        print("VOTE TABLE:")
        print(tabulate(table, headers=["Book", "First Choice", "Second Choice", "Third Choice", "Win Counters"]))
        
        print("")  # Add an empty line for better readability

    def elim_books_complex(vote_table):

        # Put books with the lowest number of win_counters and min vote counts in candidates to eliminate
        min_win_counter = min(counts[3] for counts in vote_table.values())
        print(f"Min Win Counters: {min_win_counter}")
        
        # Get the lowest sum of all votes
        min_vote_counts = min(sum(counts[:3]) for counts in vote_table.values())
        print(f"Min Vote Counts: {min_vote_counts}")

        # Get the candidates to eliminate with the lowest win counters and the lowest vote counts
        candidates_to_eliminate = [(book, counts) for book, counts in vote_table.items() if counts[3] == min_win_counter and sum(counts[:3]) == min_vote_counts]
        print(f"Candidates to Eliminate: {candidates_to_eliminate}")

        # Get the highest sum of weighted book vote counts
        max_wbv_sum = max((counts[0]*1 + counts[1]*2 + counts[2]*3) for books, counts in candidates_to_eliminate)
        print(f"Maximum Weighted Book Vote Sum: {max_wbv_sum}")

        # Choose your next books to eliminate by picking the candidates to eliminate with the highest weighted book vote sums
        books_to_eliminate = [book for book, counts in candidates_to_eliminate if (counts[0]*1 + counts[1]*2 + counts[2]*3) == max_wbv_sum]
        print(f"Books to Eliminate: {books_to_eliminate} \n")

        return books_to_eliminate

    # Eliminates books just by weighting the 1st, 2nd, and 3rd place votes they have
    # --- ISSUE, DON'T ACCOUNT FOR TIES
    def elim_books_simple(vote_table):

        # Choose the book(s) to eliminate based on the minimum weighted book vote sum
        books_to_eliminate = min(vote_table.items(), key=lambda item: (item[1][0]*3 + item[1][1]*2 + item[1][2]*1))
        print(f"Book to Eliminate: {books_to_eliminate[0]}\n")

        return [books_to_eliminate[0]]

    # Eliminates books based on the instant-runoff voting method
    def elim_books_irv(vote_table):
        # Choose the books to eliminate based on who has the lowest number of first place votes (item[1][0] = first place votes)
        books_to_eliminate = min(vote_table.items(), key=lambda item: item[1][0])

        return [books_to_eliminate[0]]


    # Calculate the vote threshold
    threshold = math.ceil(len(user_preferences) / 2)

    # Create a vote table
    vote_table = defaultdict(lambda: [0, 0, 0, 0])  # First 3 positions for votes, 4th for win_counter

    # Count initial votes
    for prefs in user_preferences.values():
        for i, book in enumerate(prefs[:3]):
            vote_table[book][i] += 1

    # Update win_counter
    for book in list(vote_table):
        vote_table[book][3] = vote_table[book][0]  # Set win_counter

    round_number = 0  # To keep track of rounds
    print_votetable(vote_table) # Initial vote table
    print_standings(round_number)  # Initial standings
    
    # Remove books with 0 win counters from the start
    vote_table = {book: counts for book, counts in vote_table.items() if counts[3] > 0}
    user_preferences = {user: [pref for pref in prefs if pref in vote_table] for user, prefs in user_preferences.items()}
    
    round_number += 1  # Iterate one round after removing 0 win-counter books
    print_standings(round_number)  # Initial standings

    while True:
        # Check for a winner
        for book, counts in vote_table.items():
            if counts[3] >= threshold:
                print(f"Winner found: {book} with {counts[3]} win counter(s)")
                return book

        # Find books with the lowest win_counters and prepare for elimination
        if not vote_table:
            print("No winner could be determined with the given preferences.")
            return None

        # Run elim_books to get candidates to eliminate
        books_to_eliminate = elim_books_irv(vote_table)

        # NEED TO RECOMMENT BELOW, CONFUSING
        # Reallocation of votes for users whose active vote is on an eliminated book
        for user, prefs in user_preferences.items():
            if prefs[0] in books_to_eliminate:
                prefs.pop(0)  # Remove the eliminated book from preferences
                if prefs:  # If there are still preferences left
                    new_vote = prefs[0]
                    vote_table[new_vote][3] += 1  # Increase win counter for the next preference
                else:
                    continue  # No more preferences left for this user

        # Eliminate candidates and update the vote_table
        for book in books_to_eliminate:
            print(vote_table[book])
            del vote_table[book]

        round_number += 1
        print_standings(round_number, focus_books=books_to_eliminate)

# Example usage with the same user preferences
user_preferences = {
    "user1": ["Book A", "Book D", "Book F"],
    "user2": ["Book B", "Book E", "Book A"],
    "user3": ["Book C", "Book F", "Book D"],
    "user4": ["Book D", "Book A", "Book B"],
    "user5": ["Book E", "Book B", "Book C"],
}


ranked_vote_verbose(user_preferences)
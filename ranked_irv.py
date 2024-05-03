from collections import Counter
from collections import defaultdict

def instant_runoff_vote(user_prefs):
    
    # Defines a function which takes the dict of a user and their current vote and...
    # ...outputs a dict with a book and its current vote count
    def count_votes(user_votes):
        
        # Initialize a vote_counts dictionary
        vote_counts = {vote: 0 for vote in user_votes.values()}

        # Count votes from the current dict of users and their votes
        for vote in user_votes.values():
            vote_counts[vote] += 1

        return vote_counts
    
    # Defines a function that prints the current standings from our vote counts
    def print_standings(first_vote_counts):

        # Print the standings
        for book, vote in first_vote_counts.items():
            print(f"{book}: {vote} votes")

        # Add line break to space things out
        print("")

        return
    
    # Defines a function that gets the list of the books with the max votes, 
    # returns that and the max vote count
    def most_votes(vote_counts):

        # A count of the votes for each book, excluding eliminated books
        # non_elimed_vote_counts = {book: count for book, count in vote_counts.items() if book not in eliminated_books}

        # Find the maximum vote count
        max_votes = max(vote_counts.values(), default=0)
        
        # Get all books that have this maximum count
        most_voted_books = [book for book, count in vote_counts.items() if count == max_votes]
        
        return most_voted_books, max_votes
    
    # Defines a function that gets the list of the books with the minimum votes, 
    # returns that and the minimum vote count
    def least_votes(vote_counts, eliminated_books):

        # A count of the votes for each book, excluding eliminated books
        non_elimed_vote_counts = {book: count for book, count in vote_counts.items() if book not in eliminated_books}

        # Find the minimum vote count
        min_votes = min(non_elimed_vote_counts.values(), default=0)
        
        # Get all books that have this minimum count
        least_voted_books = [book for book, count in non_elimed_vote_counts.items() if count == min_votes]
        
        return least_voted_books, min_votes 

    # Initialize user_votes as a dict of just the users and their first place votes
    user_votes = {user: prefs[0] for user, prefs in user_prefs.items() if prefs}

    # Initialize a vote_counts dictionary
    vote_counts = count_votes(user_votes)

    # Print initial standings
    print("Initial Votes")
    print_standings(vote_counts)

    # Initialize eliminated book list
    eliminated_books = []

    # Initialize Round Counter
    rounds = 0
    
    while True:

        # Get the list of most_voted books and the number of votes they received
        most_voted_books, max_votes = most_votes(vote_counts)

        # If there is only one book in the most-voted list...
        if len(most_voted_books) == 1:
            # ...WE HAVE A WINNER!!!
            print(f"Winner found: {most_voted_books} with {max_votes} votes")
            return most_voted_books

        # Otherwise, do a round of eliminations...
        # ...start by finding the list of books with the least votes
        least_voted_books, min_votes = least_votes(vote_counts, eliminated_books)

        # Check for a tie--this is the case in IRV if we have the same
        # list for most voted and least voted books
        if least_voted_books == most_voted_books:
            print("There is a tie, a winner could not be determined by the Instant-runoff Voting Method.")
            return
        
        # If we don't have a tie, add the list of least voted books to the eliminated book function
        eliminated_books.extend(least_voted_books)
        print(f"We eliminated {least_voted_books} with {min_votes} votes each.")
        print(f"All Eliminated Books: {eliminated_books}\n")

        # Distribute the votes users had for least-voted books to new books
        for user in user_prefs.keys():
            
            # Use next() with a generator expression to find the first non-eliminated book for the user
            user_votes[user] = next((prefs for prefs in user_prefs.get(user, "This user does not exist.") if prefs not in eliminated_books), None)

        # Get new vote_counts based on the updated user_votes
        vote_counts = count_votes(user_votes)

        # Iterate Rounds
        rounds += 1

        # Print standings
        print(f"Round {rounds} Standings")
        print_standings(vote_counts)

        
user_prefs = {
    "user1": ["Book A", "Book D", "Book F"],
    "user2": ["Book B", "Book E", "Book A"],
    "user3": ["Book C", "Book A", "Book D"],
    "user4": ["Book D", "Book C", "Book H"],
    "user5": ["Book E", "Book C", "Book D"],
    "user6": ["Book A", "Book F", "Book E"],
    "user7": ["Book B", "Book C", "Book G"],
}

instant_runoff_vote(user_prefs)
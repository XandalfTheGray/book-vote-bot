Ranked Voting System for Book Club Picks
This Python script implements a ranked voting system designed to facilitate decision-making in choosing books for a book club. Users rank their preferred books, and the system iteratively determines the most favored book based on the collective preferences.

How It Works
The script operates by taking each user's list of preferred books in order of preference. It then performs a series of rounds where books with the fewest win counters (i.e., first-place votes) and overall votes are considered for elimination. The process continues until a book achieves a majority threshold, making it the selected choice for the book club.

Key Functions
ranked_vote_verbose: The main function that orchestrates the voting process. It accepts a dictionary of user preferences, performs voting rounds, and outputs the winning book.
print_standings: Prints the current standings of books at the end of each round, including the number of win counters for each book and highlighting the books that are the focus of the current round.
elim_books: Identifies books to be eliminated based on specific criteria, such as the lowest number of win counters and the lowest sum of votes.
Input Format
The input should be a dictionary where each key is a user's name and each value is a list of that user's book preferences ranked from most to least preferred.

Example:

python
Copy code
user_preferences = {
    "user1": ["Book A", "Book D", "Book F"],
    "user2": ["Book B", "Book E", "Book A"],
    "user3": ["Book C", "Book F", "Book D"],
    # Add more users and preferences as needed
}
Usage
Ensure Python is installed on your system.
Copy the script into a .py file, for example, ranked_vote.py.
Create a dictionary of user preferences according to the input format.
Call the ranked_vote_verbose(user_preferences) function with your dictionary of preferences.
Example:

python
Copy code
ranked_vote_verbose(user_preferences)
The script will print the standings after each round and announce the winning book once a majority is reached.

Requirements
Python 3.x
This script uses standard Python libraries (math and collections) and does not require external dependencies.

Notes
The system assumes that each user ranks their top three books.
Books with the lowest win counters are at risk of elimination each round. In case of ties, books with the lowest sum of first and second-place votes are considered for elimination.
The process ensures that the most collectively preferred book is chosen, accounting for the ranked preferences of all participants.

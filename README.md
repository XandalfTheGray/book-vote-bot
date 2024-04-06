# Ranked Voting System for Book Club Picks

This Python script implements a ranked voting system designed to facilitate decision-making in choosing books for a book club. Users rank their preferred books, and the system iteratively determines the most favored book based on the collective preferences.


## How It Works

This script follows a **Ranked Choice Voting (RCV)** algorithm (also known as **Instant Runoff Voting (IRV)**), which you can read more about [here](https://en.wikipedia.org/wiki/Instant-runoff_voting).

The script operates by taking a list of each user's preferred books in order of preference. It then performs a series of rounds where books with the fewest win counters (i.e., first-place votes) and overall votes are considered for elimination. The process continues until a book achieves a majority threshold, making it the selected choice for the book club.


## Key Functions

**ranked_vote_verbose**:
the main function that orchestrates the voting process. It accepts a dictionary of user preferences, performs voting rounds, and outputs the winning book.

**print_standings**:
prints the current standings of books at the end of each round, including the number of win counters for each book and highlighting the books that are the focus of the current round.

**elim_books**:
identifies books to be eliminated based on specific criteria, such as the lowest number of win counters and the lowest sum of votes.


## Input Format
The input should be a dictionary where each key is a user's name and each value is a list of that user's book preferences ranked from most to least preferred.


## Usage
1.  Ensure Python is installed on your system.

    - Run `python --version` in your terminal to verify that Python is installed

2.  Copy the script into a .py file, for example: *ranked_vote.py*.

    - Create a dictionary of user preferences according to the input format.

            user_preferences = {
                "user1": ["Book A", "Book D", "Book F"],
                "user2": ["Book B", "Book E", "Book A"],
                "user3": ["Book C", "Book F", "Book D"],
                # Add more users and preferences as needed
            }

    - Call the `ranked_vote_verbose(user_preferences)` function with your dictionary of preferences.

            ranked_vote_verbose(user_preferences)

    - Running the script will print the standings after each round and announce the winning book once a majority is reached.      


## Requirements
Python 3.x : This script uses standard Python libraries (math and collections) and does not require external dependencies.


## Notes
The system assumes that each user ranks their top three books.
Books with the lowest win counters are at risk of elimination each round. In case of ties, books with the lowest sum of first and second-place votes are considered for elimination.
The process ensures that the most collectively preferred book is chosen, accounting for the ranked preferences of all participants.


<style type="text/css">
    ul { list-style-type: lower-alpha; }
</style>
def proper_case(input_string):
    
    # Create a list of articles, conjunctions, and prepositions words that should remain lowercase in Proper Case
    lowercase_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 'with', 'in', 'of', 'from'}
    
    # Split the input string into words
    words = input_string.split()
    
    # Capitalize the first word and other significant words
    result = [words[0].capitalize()]
    for word in words[1:]:
        if word.lower() in lowercase_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
            
    # Join the words back into a single string
    return ' '.join(result)
def get_hashtags(tweet_text):
    '''
    Returns hashtagged terms without punctuation and stripped of '#'
    '''
    hashtags = set()

    # Possible scenarios:
    #   1. #hello ifh3ouhf #hifio3hif
    #   2. #hello#hello2
    #   3. ######hello

    tweet_text = tweet_text.replace("#", " #")
    split_text = tweet_text.split()
    for text in split_text:
        text = text.strip() # Remove any whitespace chars from term
        if "#" in text:
            for term in text.split("#"):
                filtered_term = filter(str.isalnum, term) # Filter out non-alphanumeric characters
                term = "".join(filtered_term).strip() # Remove any whitespace again
                lower_term = term.lower()

                if lower_term not in hashtags and term:
                    hashtags.add(lower_term)

    return list(hashtags)
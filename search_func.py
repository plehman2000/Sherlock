from fuzzywuzzy import process

def fuzzy_search(query, entities, limit=-1):
    
    process_limit = len(entities)
    if limit != -1:
        assert limit > 0 and type(limit) is int, "Limit should be an integer greater than 0."
        process_limit = limit
        
    keywords = query.split(";")
    print(keywords)
    sorted_dict = {}

    for word in keywords:
        sorted_dict[word] = process.extract(word, entities, limit=process_limit)

    return sorted_dict


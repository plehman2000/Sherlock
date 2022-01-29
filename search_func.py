from fuzzywuzzy import process

def getEntTsPairs(entities_from_transcript):
    """
    Returns a dictionary with key = entity name and value = list of timestamps assocaited with entity
    Takes input from the result of getTranscriptFromURL
    """


    ent_ts_pairs = dict()
    for ent_list in entities_from_transcript:
        entity = ent_list[0][0][0]
        timestamp = ent_list[1]
        
        if entity not in ent_ts_pairs.keys():
            ent_ts_pairs[entity] = []
        ent_ts_pairs[entity].append(timestamp)
    return ent_ts_pairs
            
def fuzzySearch(query, ent_ts_pairs, limit=-1):
    """
    Returns a dictionary with key = query word and value = list of lists (kw_rel_ts_list).

    kw_rel_ts_list has 3 values:
        kw_rel_ts[0] = entity name
        kw_rel_ts[1] = relevance relative to query of entity
        kw_rel_ts[2] = list of timestamps where query appears in video
    """

    entities_list = ent_ts_pairs.keys()
    process_limit = len(entities_list)
    if limit != -1:
        assert limit > 0 and type(limit) is int, "Limit should be an integer greater than 0."
        process_limit = limit
        
    keywords = query.split(";")
    sorted_dict = {}

    for word in keywords:
        sorted_dict[word] = process.extract(word, entities_list, limit=process_limit)
        
    kw_rel_ts_sorted_dict = dict()
    for kw, kw_relevance_tuples_list in sorted_dict.items():
        kw_rel_ts_list = []
        for kw_relevance_tuple in kw_relevance_tuples_list:
            curr_entity = kw_relevance_tuple[0]
            kw_rel_ts = [curr_entity, kw_relevance_tuple[1], ent_ts_pairs[curr_entity]]
            kw_rel_ts_list.append(kw_rel_ts)
    kw_rel_ts_sorted_dict[kw] = kw_rel_ts_list
    
    return kw_rel_ts_sorted_dict

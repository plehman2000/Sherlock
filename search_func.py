from fuzzywuzzy import process
import re

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

def getIDFromURL(youtube_url):
    pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
    result = re.findall(pattern, youtube_url, re.IGNORECASE)
    
    return result[0]

def getURLFromQuery(query, vid_url):
    
    vid_id = getIDFromURL(vid_url)
    base_ts_url = f"https://youtu.be/{vid_id}?t="
    transcript = getTranscriptFromURL(vid_url)
    entities_from_transcript = stampsToEnts(transcript)
    
    ent_ts_pairs = get_ent_ts_pairs(entities_from_transcript)
    kw_rel_ts_sorted_dict = fuzzy_search(query, ent_ts_pairs)
    
    entity_tslink_dict = {}
    for kw in kw_rel_ts_sorted_dict.keys():
        for kw_rel_ts_list in kw_rel_ts_sorted_dict[kw]:
            tslink_list = []
            curr_entity = kw_rel_ts_list[0]
            for ts in kw_rel_ts_list[2]:
                tslink = base_ts_url + str(round(float(ts)))
                tslink_list.append(tslink)
            
            # Add relevance to list
            tslink_rel_list = [tslink_list, kw_rel_ts_list[1]]
            entity_tslink_dict[curr_entity] = tslink_rel_list
    
    return entity_tslink_dict
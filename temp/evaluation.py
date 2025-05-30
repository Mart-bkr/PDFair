from datasketch import MinHash, MinHashLSH

def get_minhash(sentence, num_perm=256):
    """Generate a MinHash object for a given sentence."""
    m = MinHash(num_perm=num_perm)
    for word in sentence.split():
        m.update(word.encode('utf8'))  # Hash each word
    return m

def minhash_match_sentences(sentences_a, sentences_b, threshold=0.7, num_perm=128):
    """Match sentences using MinHash + Locality-Sensitive Hashing (LSH)."""
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    
    # Add all sentences from B to the LSH index
    for i, sentence in enumerate(sentences_b):
        m = get_minhash(sentence, num_perm)
        lsh.insert(str(i), m)

    matches = {}  # Store matched indices
    for i, sentence in enumerate(sentences_a):
        m_a = get_minhash(sentence, num_perm)
        results = lsh.query(m_a)  # Find similar sentences in B
        
        print(results)

        if results:
            best_match_idx = int(results[0])  # Take the first match
            matches[i] = best_match_idx
    
    return matches

import re
import json
import unicodedata
import os

def parse_anhviet_entry(raw_entry):
    if not raw_entry.strip():
        return None
    lines = raw_entry.strip().split('\n')
    header = lines[0].lstrip('@').strip()
    
    pron = ''
    pron_match = re.search(r'/(.*?)/', header)
    if pron_match:
        pron = '/' + pron_match.group(1).strip() + '/'
        word = header[:pron_match.start()].strip()
    else:
        word = header.strip()
    
    word = unicodedata.normalize('NFC', word.lower()).strip()
    # Filter headwords: standard English words, reasonable length
    if not word or len(word) > 40 or not re.match(r'^[a-z0-9][a-z0-9\s\-_]*$', word):
        return None
    
    word_type = 'noun'
    meanings = []
    example = None
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('*'):
            wt = line.lstrip('*').strip()
            if 'danh từ' in wt: word_type = 'noun'
            elif 'động từ' in wt: word_type = 'verb'
            elif 'tính từ' in wt: word_type = 'adjective'
            elif 'phó từ' in wt or 'trạng từ' in wt: word_type = 'adverb'
            elif 'giới từ' in wt: word_type = 'preposition'
            elif 'mạo từ' in wt: word_type = 'article'
            elif 'liên từ' in wt: word_type = 'conjunction'
        elif line.startswith('-'):
            m = line.lstrip('-').strip()
            if m:
                clean_m = re.sub(r'\(.*?\)', '', m).strip(' .,;:-')
                if clean_m:
                    meanings.append(clean_m)
                else:
                    meanings.append(m.strip(' .,;:-'))
        elif line.startswith('=') and not example:
            ex = line.lstrip('=').strip()
            parts = ex.split('+')
            if len(parts) >= 2:
                example = f"{parts[0].strip()} ({parts[1].strip()})"
            else:
                example = ex
    
    if not meanings:
        return None
        
    meaning_text = '; '.join(meanings[:4])
    return {
        'word': word,
        'meaning': meaning_text,
        'pronunciation': pron if pron else None,
        'word_type': word_type,
        'example': example if example else f"Example sentence using the word '{word}'."
    }

def main():
    # 1. Start with the existing verified dictionary dataset (2,218 entries)
    existing_path = 'data/dictionary.json'
    combined = {}
    if os.path.exists(existing_path):
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        for item in existing_data:
            combined[item['word']] = item
        print(f"Loaded {len(combined)} existing verified dictionary entries.")

    # 2. Parse anhviet109K.txt
    txt_path = 'data/anhviet109K.txt'
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    raw_entries = content.split('\n@')
    print('Raw entry blocks in 109K:', len(raw_entries))

    # Add single-word headwords first (most common dictionary words)
    single_word_pool = []
    compound_pool = []

    for block in raw_entries:
        parsed = parse_anhviet_entry(block)
        if not parsed:
            continue
        w = parsed['word']
        if w in combined:
            continue
        if ' ' not in w and '_' not in w and '-' not in w:
            single_word_pool.append(parsed)
        else:
            compound_pool.append(parsed)

    print(f"Extracted {len(single_word_pool)} single-word headwords, {len(compound_pool)} compounds.")

    # Select single-word headwords up to target total ~22,000
    target_count = 22000
    needed = target_count - len(combined)

    for p in single_word_pool[:needed]:
        combined[p['word']] = p

    # If still needed, take from compounds
    if len(combined) < target_count:
        rem = target_count - len(combined)
        for p in compound_pool[:rem]:
            combined[p['word']] = p

    # Convert to sorted list
    final_list = sorted(combined.values(), key=lambda x: x['word'])
    print(f"Final combined dictionary count: {len(final_list)} entries.")

    with open('data/dictionary_expanded.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    print("Saved to data/dictionary_expanded.json successfully.")

if __name__ == '__main__':
    main()

from typing import List, Dict, Tuple, Union

from fuzzywuzzy import fuzz
import random


def get_random(pdb_codes:List, number:int) -> List:
    """
    This function returns a random selection of pdb_codes from the pdb code list

    Args:
        pdb_codes (List) - the list of pdb codes
        number (int) - the number of random pdb codes to return
    
    Returns:
        List - a list of randomly selected pdb codes
    """
    return random.sample(pdb_codes, number)


def lookup_pdb_code(pdb_code:str, pdb_codes:List) -> Dict:
    if pdb_code in pdb_codes:
        return_data = {
            'match':'exact',
            'best_matches':[pdb_code]
        }
    else:
        best_matches = []
        matches = []
        for this_pdb_code in pdb_codes:
            score = fuzz.ratio(pdb_code, this_pdb_code)
            if score >= 75:
                best_matches.append(this_pdb_code)
            elif score >= 50:
                matches.append(this_pdb_code)
        if len(matches) > 10:
            matches = get_random(matches, 10)
        if len(matches) == 0 and len(best_matches) == 0:
            matches = get_random(pdb_codes, 10)
        return_data = {
            'match':'fuzzy',
            'matches':matches,
            'best_matches':best_matches
        }
    return return_data


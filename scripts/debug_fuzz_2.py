
from rapidfuzz import fuzz, process

choices = ["en", "esa", "cuenta", "que", "se", "llama", "aliexpress", "ahora", "registra", "que", "compre", "un", "carro", "de", "lego"]
account_name = "alieress"

# Check if we can find the account name in the list of words
match = process.extractOne(account_name, choices, scorer=fuzz.ratio)
print(f"Match 'alieress' against words: {match}")

# Also try with "nequi"
match_nequi = process.extractOne("nequi", choices, scorer=fuzz.ratio)
print(f"Match 'nequi' against words: {match_nequi}")

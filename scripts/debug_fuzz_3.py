
from rapidfuzz import fuzz, process

message = "en esa cuenta que se llama aliexpress, ahora registra que compre un carro de lego y me gaste 170000 pesos."
words = message.split()

# Generate n-grams (up to 3 words)
ngrams = []
for n in range(1, 4):
    for i in range(len(words) - n + 1):
        ngrams.append(" ".join(words[i:i+n]))

print(f"Generated {len(ngrams)} n-grams")
# print(ngrams)

account_name = "alieress"
match = process.extractOne(account_name, ngrams, scorer=fuzz.ratio)
print(f"Match 'alieress' against n-grams: {match}")

# Test multi-word account
message_2 = "paga con mi banco de bogota por favor"
words_2 = message_2.split()
ngrams_2 = []
for n in range(1, 4):
    for i in range(len(words_2) - n + 1):
        ngrams_2.append(" ".join(words_2[i:i+n]))

account_name_2 = "banco bogota" # Real name
match_2 = process.extractOne(account_name_2, ngrams_2, scorer=fuzz.ratio)
print(f"Match 'banco bogota' against 'banco de bogota': {match_2}")
# Expected: 'banco de bogota' (closest n-gram) vs 'banco bogota'.
# Ratio of "banco bogota" vs "banco de bogota" is high?
print(f"Ratio: {fuzz.ratio('banco bogota', 'banco de bogota')}")

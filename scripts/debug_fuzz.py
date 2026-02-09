
try:
    from rapidfuzz import fuzz, process
    print("Rapidfuzz imported successfully")
except ImportError:
    print("Rapidfuzz NOT installed")
    exit()

choices = ["alieress", "nequi"]
message = "en esa cuenta que se llama aliexpress, ahora registra que compre un carro de lego y me gaste 170000 pesos."

print(f"Choices: {choices}")
print(f"Message: {message}")

# Test partial_ratio
match = process.extractOne(message, choices, scorer=fuzz.partial_ratio)
print(f"Partial Ratio Match: {match}")

# Test ratio (exact match of the substring?)
match_ratio = process.extractOne(message, choices, scorer=fuzz.ratio)
print(f"Ratio Match: {match_ratio}")

# Test direct match between 'aliexpress' and 'alieress'
print(f"Direct match 'aliexpress' vs 'alieress': {fuzz.ratio('aliexpress', 'alieress')}")
print(f"Direct partial 'aliexpress' vs 'alieress': {fuzz.partial_ratio('aliexpress', 'alieress')}")

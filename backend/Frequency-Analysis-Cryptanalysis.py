from collections import Counter
import string

# Input ciphertext
ciphertext = input("Enter the ciphertext: ")

# Convert to uppercase
ciphertext = ciphertext.upper()

# Count frequency of each alphabet
frequency = Counter(ciphertext)

print("\nFrequency Analysis:")
print("-------------------")

# Display frequency of all alphabets
for alphabet in string.ascii_uppercase:
    print(f"{alphabet} : {frequency[alphabet]}")

# Display histogram
print("\nHistogram:")
print("-------------------")

for alphabet in string.ascii_uppercase:
    count = frequency[alphabet]
    print(f"{alphabet} : {'*' * count}")

# Find the most frequent character
letters_only = {char: count for char, count in frequency.items()
                if char in string.ascii_uppercase}

if letters_only:
    most_frequent = max(letters_only, key=letters_only.get)
    print("\nMost Frequent Character:")
    print(f"{most_frequent} occurs {letters_only[most_frequent]} times.")
else:
    print("\nNo alphabet characters found.")
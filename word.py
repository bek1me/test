class WordDifficultyAnalyzer:
    def __init__(self):
        self.common_prefixes = ('un', 'in', 'dis', 'en', 'non', 'pre', 'post', 'over', 'under', 're', 'semi', 'anti', 'mid', 'mis')
        self.common_suffixes = ('ing', 'ly', 'ed', 'ion', 'er', 'ment', 'ness', 'ship', 's', 'es')
        self.rare_words = set(['ubiquitous', 'quintessential', 'ephemeral', 'serendipity'])  # Misol uchun

    def count_syllables(self, word):
        word = word.lower()
        vowel_count = sum(1 for char in word if char in "aeiouy")
        for i in range(1, len(word)):
            if word[i] in "aeiouy" and word[i-1] in "aeiouy":
                vowel_count -= 1
        return max(1, vowel_count)

    def has_affixes(self, word):
        return any(word.startswith(prefix) for prefix in self.common_prefixes) or any(word.endswith(suffix) for suffix in self.common_suffixes)

    def is_rare_word(self, word):
        return word.lower() in self.rare_words

    def evaluate_word_difficulty(self, word):
        syllables = self.count_syllables(word)
        affix = self.has_affixes(word)
        rare = self.is_rare_word(word)
        difficulty_score = 5  # Eng oson so'zlar uchun boshlang'ich ball

        if syllables >= 3 or affix or rare:
            difficulty_score = 1.5
        elif syllables == 2:
            difficulty_score = 3
        elif syllables == 1:
            difficulty_score = 4

        return difficulty_score

import nltk
from nltk.corpus import wordnet as wn
import re

nltk.download('wordnet')
nltk.download('omw-1.4')


class BaseGoalExpander:
    def __init__(self, parser, ontology):
        self.parser = parser
        self.ontology = ontology

    def clean_term(self, term):
        """Rimuove i caratteri non alfabetici e converte in CamelCase."""
        term = re.sub(r'[^a-zA-Z\s]', '', term)
        words = term.split()
        return ''.join(word.capitalize() for word in words)

    def get_wordnet_expansions(self, term):
        expansions = set()

        for synset in wn.synsets(term):
            # Aggiunge sinonimi
            for lemma in synset.lemmas():
                expansion = self.clean_term(lemma.name().replace('_', ' '))
                try:
                    parsed_expansion = self.parser.parse(expansion)
                    if parsed_expansion in self.ontology.classes():
                        expansions.add(expansion)
                except:
                    continue

            # Aggiunge iponimi (hyponyms)
            for hyponym in synset.hyponyms():
                for lemma in hyponym.lemmas():
                    expansion = self.clean_term(lemma.name().replace('_', ' '))
                    try:
                        parsed_expansion = self.parser.parse(expansion)
                        if parsed_expansion in self.ontology.classes():
                            expansions.add(expansion)
                    except:
                        continue

            # Aggiunge iperonimi (hypernyms)
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    expansion = self.clean_term(lemma.name().replace('_', ' '))
                    try:
                        parsed_expansion = self.parser.parse(expansion)
                        if parsed_expansion in self.ontology.classes():
                            expansions.add(expansion)
                    except:
                        continue

        return expansions

    def expand_goal_term(self, term):
        # Se il termine esiste nell'ontologia, lo lasciamo invariato
        if self.parser.parse(term) in self.ontology.classes():
            expansions = {term}
            # Aggiungiamo anche i sinonimi, iponimi e iperonimi trovati con WordNet che esistono nell'ontologia
            expansions.update(self.get_wordnet_expansions(term))
        else:
            # Altrimenti, cerchiamo solo i sinonimi, iponimi e iperonimi presenti nell'ontologia
            expansions = self.get_wordnet_expansions(term)
        return " or ".join(expansions) if expansions else ""

    def expand_goal(self, goal_string):
        parts = goal_string.split()
        expanded_parts = []

        for part in parts:
            if part.lower() in ["and", "or", "not"]:
                expanded_parts.append(part.lower())
            else:
                expanded_term = self.expand_goal_term(part)
                if expanded_term:  # Aggiungiamo solo se c'è almeno un termine valido
                    expanded_parts.append(f"({expanded_term})")

        expanded_goal = " ".join(expanded_parts)
        print(f"Expanded goal: {expanded_goal}")  # Debugging output
        return expanded_goal
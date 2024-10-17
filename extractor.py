import os
import re
import spacy
import tqdm

nlp = spacy.load("en_core_web_sm")

# Columns for spaCy items

spacy_pos = ['PROPN', 'NOUN', 'PRON', 'VERB', 'AUX', 'ADJ', 'ADV', 'ADP', 'CCONJ', 'SCONJ', 'INTJ', 'DET', 'PART', 'PUNCT', 'NUM', 'SYM', 'X']

result = []
for element in spacy_pos:
    result.append(f"{element.lower()}_elements")
    result.append(f"{element.lower()}_quantity")

spacy_pos = result.copy()

# Columns for book elements

books = ['sentence', 'words_quantity', 'source']

# Total

cols = books + spacy_pos

class BookProcessor:
    
    """
        Base class for processing books and extracting sentences.
    """

    def __init__(self, folder, label):
        self.folder = folder
        self.label = label
        self.file_list_paths = [os.path.join(folder, file) for file in os.listdir(folder)]
        self.sentences = []
        self.separator = '/'

    def get_sentences(self, book):
        
        """
            Extract sentences from the processed book text.
        """

        sentence_end_chars = ['.', '!', '?']
        sentences = []
        i = 0

        for index, char in enumerate(book):

            if char in sentence_end_chars:

                # Passing if "..." in sentence
                if (index + 1 < len(book) and (book[index + 1] in sentence_end_chars or book[index - 1] in sentence_end_chars)):
                    continue

                sentence = book[i + 1:index + 1]
                sentences.append(sentence.strip())
                i = index

        return sentences

    def process_books(self):
        
        """
            Process all books in the folder by transforming and extracting sentences.
        """

        books = [self.transform_book(book) for book in self.file_list_paths]

        for book in books:
            stncs = self.get_sentences(book)
            self.sentences.extend(stncs)

    def extract_pos(self, sentence):
    
        """
            Extracts parts of speech (POS) from a given document and categorizes them into the following groups:
            
            - PROPN: Proper noun (e.g., names of people, places)
            - NOUN: Noun (e.g., objects, subjects, or things)
            - ADJ: Adjective (e.g., descriptive words like "beautiful", "fast")
            - VERB: Verb (e.g., actions like "run", "write")
            - ADV: Adverb (e.g., words describing verbs like "quickly", "very")
            - ADP: Adposition (prepositions like "in", "on", "to")
            - CCONJ: Coordinating conjunction (e.g., "and", "but", "or")
            - SCONJ: Subordinating conjunction (e.g., "because", "although")
            - INTJ: Interjection (e.g., "wow", "oh", "ah")
            - AUX: Auxiliary verb (e.g., "is", "have", "will")
            - DET: Determiner (e.g., "the", "a", "some")
            - PART: Particle (e.g., "not", "to" in infinitive form like "to run")
            - PUNCT: Punctuation (e.g., ".", "!", "?" used in writing)
            - PRON: Pronoun (e.g., "he", "she", "it")
            - NUM: Numeral (e.g., numbers like "one", "two", "three")
            - SYM: Symbol (e.g., "$", "%", "+")
            - X: Other (for parts of speech that are not clearly identified, e.g., foreign words, fillers)

        """

        doc = nlp(sentence) 

        pos = dict(
            PROPN = [],  # Proper noun
            NOUN = [],   # Noun
            PRON = [],   # Pronoun
            VERB = [],   # Verb
            AUX = [],    # Auxiliary verb
            ADJ = [],    # Adjective
            ADV = [],    # Adverb
            ADP = [],    # Adposition (preposition)
            CCONJ = [],  # Coordinating conjunction
            SCONJ = [],  # Subordinating conjunction
            INTJ = [],   # Interjection
            DET = [],    # Determiner
            PART = [],   # Particle
            PUNCT = [],  # Punctuation
            NUM = [],    # Numeral
            SYM = [],    # Symbol
            X = []       # Other (unidentified part of speech)
        )

        for key in pos.keys():
            for token in doc:
                if token.pos_ == key:
                    pos[key].append(token.text)
        
        pos = [(self.separator.join(value), str(len(value))) for value in pos.values()]
        pos = [self.separator.join(tup) for tup in pos]

        return pos

    def save_sentences(self, output_file):

        """
            Save the extracted sentences to a file.
        """

        with open("sentences.txt", 'w', encoding = 'utf-8') as file:
            head = self.separator.join(cols) + '\n'
            file.write(head)

        with open(output_file, 'a', encoding = 'utf-8') as file:

            for sentence in tqdm(self.sentences):

                if sentence.startswith("' '") or sentence.startswith("’ ‘"):
                    sentence = sentence.replace("' '", "").replace("’ ‘", "")

                if sentence.startswith("' ") or sentence.startswith("’ "):
                    sentence = sentence.replace("' ", "").replace("’ ", "")

                blockers = [':', ';', ',', '.', '!', '?', '—', '-', '(', ')']

                if (not sentence[0].islower() or sentence[0] in blockers) and not sentence.startswith('…'):
                    words_number = len(sentence.split(' '))

                    if words_number > 5:
                        pos_extractor = self.extract_pos(sentence)
                        row = self.separator.join([sentence, str(words_number), self.label] + pos_extractor) + '\n'
                        file.write(row)


class GameOfThronesProcessor(BookProcessor):
    
    """
        Class for processing Game of Thrones books.
    """

    def __init__(self, folder):
        super().__init__(folder, 'GOT')

    def transform_book(self, file_path, start_word_lower = 'prologue', end_word_lower = 'appendix'):
        
        with open(file_path, 'r') as file:
            book = file.read()

            book = (
                book.replace('\n', '')
                    .replace('"', '')
                    .replace('. . .', '...')
                    .replace('/', '')
                    .replace('”', '')
                    .replace('“', '')
            )

            book_lower = book.lower()
            str_index = book_lower.rfind(start_word_lower)
            end_index = book_lower.rfind(end_word_lower)

            if str_index != -1 and end_index != -1:
                book = book[str_index + len(start_word_lower) - 1:end_index]
            elif str_index != -1 and end_index == -1:
                book = book[str_index + len(start_word_lower) - 1:]
            elif str_index == -1 and end_index != -1:
                book = book[:end_index]

            result = re.sub(r"Page \d+", "", book)
            result = " ".join(result.split())

            return result


class HarryPotterProcessor(BookProcessor):
    
    """
        Class for processing Harry Potter books.
    """

    def __init__(self, folder):
        super().__init__(folder, 'HP')

    def transform_book(self, file_path, start_word_lower = 'prologue', end_word_lower = 'epilogue'):

        with open(file_path, 'r', encoding = 'utf-8') as file:
            
            lines = file.read().split('\n')
            lines = [line for line in lines if line != '']
            lines = [line for line in lines if not line.lower().startswith('chapter')]
            lines = [line for line in lines if 'Harry Potter and the' not in line]
            lines = [line for line in lines if any(punct in line for punct in ['.', '!', '?', '—'])]

            book = " ".join(lines)

            book = (
                book.replace('Mr.', 'Mr')
                    .replace('Mrs.', 'Mrs')
                    .replace('Ms.', 'Ms')
                    .replace('...', ' ... ')
                    .replace('\n', '')
                    .replace('"', '')
                    .replace('/', '')
                    .replace('”', '')
                    .replace('“', '')
                    .replace("`", "'")
                    .replace("--", " ")
            )

            book_lower = book.lower()
            str_index = book_lower.rfind(start_word_lower)
            end_index = book_lower.rfind(end_word_lower)

            if str_index != -1 and end_index != -1:
                book = book[str_index + len(start_word_lower) - 1:end_index]
            elif str_index != -1 and end_index == -1:
                book = book[str_index + len(start_word_lower) - 1:]
            elif str_index == -1 and end_index != -1:
                book = book[:end_index]

            return book

if __name__ == "__main__":

    # Processing Game of Thrones books

    got_folder = 'GameOfThrones'
    got_processor = GameOfThronesProcessor(got_folder)
    got_processor.process_books()
    got_processor.save_sentences("sentences.txt")

    # Processing Harry Potter books

    hp_folder = 'HarryPotter'
    hp_processor = HarryPotterProcessor(hp_folder)
    hp_processor.process_books()
    hp_processor.save_sentences("sentences.txt")
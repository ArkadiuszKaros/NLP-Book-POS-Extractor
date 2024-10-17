import os
import re

class BookProcessor:
    
    """
        Base class for processing books and extracting sentences.
    """

    def __init__(self, folder, label):
        self.folder = folder
        self.label = label
        self.file_list_paths = [os.path.join(folder, file) for file in os.listdir(folder)]
        self.sentences = []

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

    def save_sentences(self, output_file, separator = '/'):

        """
            Save the extracted sentences to a file.
        """

        with open(output_file, 'w', encoding = 'utf-8') as file:

            for sentence in self.sentences:

                words_number = len(sentence.split(' '))

                if words_number > 5:
                    row = separator.join([sentence, str(words_number), self.label]) + '\n'
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
            )

            book_lower = book.lower()
            str_index = book_lower.rfind(start_word_lower) + len(start_word_lower) - 1
            end_index = book_lower.rfind(end_word_lower) + len(end_word_lower)

            if str_index != -1 and end_index != -1:
                book = book[str_index:end_index]
            elif str_index != -1 and end_index == -1:
                book = book[str_index:]
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

    def transform_book(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            book = file.read()
            book = (
                book.replace('Mr.', 'Mr')
                    .replace('Mrs.', 'Mrs')
                    .replace('Ms.', 'Ms')
                    .replace('...', ' ... ')
                    .replace('\n', '')
                    .replace('"', '')
                    .replace('/', '')
            )
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

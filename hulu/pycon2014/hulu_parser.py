from collections import Counter
from json import dumps

FILE = "tv_show_groups.in"


class HuluParser(object):
    """
    NOTE: This file makes assumptions about the input that is true of the
          input file but definitely may not be true of all files.
    """

    # The divider being used to separate the regular lines from the "search
    # word" lines.
    _word_divider = "####"

    # A list of sets containing words we are looking for on each regular line.
    _search_sets = []

    # The accumulated set of all non-search words in each line where all search
    # words of a particular set were found.
    # <sarcasm>+1 for confusing explanation</sarcasm>
    _cumulative_sets = {}

    def __init__(self):
        self._file = open(FILE)

    def parse_search_words(self):
        self._seek_to_search_words()

        for line in self._file.read().splitlines():
            if line: # is not empty
                self._search_sets.append(frozenset(line.split(',')))

    def process_lines(self):
        self._file.seek(0)

        for line in self._file.read().split('\n'):
            try:
                self._validate_line(line)
            # Defining a custom EOF based on this particular file format. I
            # like this way better because it allows me to do the minimal
            # amount of work on each line until a line "proves" itself as being
            # a needed line.
            except StopAtDivider:
                break

            line_set = set(line.split(','))

            for word_set in self._search_sets:
                common_words = line_set & word_set

                # If all of the search words were found in the line...
                if len(common_words) == len(word_set):
                    # Remove all of the search words
                    unique_words = line_set - word_set

                    try:
                        self._cumulative_sets[word_set].update(unique_words)
                    except KeyError:
                        self._cumulative_sets[word_set] = Counter(unique_words)

    def write_out_results(self):
        with open('hulu_results.txt', 'wb') as out_file:
            out_file.writelines((dumps(self._cumulative_sets[word_set], sort_keys=True) + '\n'
                                for word_set in self._search_sets))

    def _validate_line(self, line):
        if line.find(self._word_divider) > -1:
            raise StopAtDivider()

    def _seek_to_search_words(self):
        start = self._file.read().find(self._word_divider)
        search_words = start + len(self._word_divider) + 1 # newline

        self._file.seek(search_words)


class StopAtDivider(Exception):
    """
    The exception used to break out of the file iteration, when we've reached
    our custom EOF line.
    """
    pass


def main():
    parser = HuluParser()

    parser.parse_search_words()
    parser.process_lines()
    parser.write_out_results()


if __name__ == '__main__':
    main()
import re
import json
import sys
from argparse import ArgumentParser, ArgumentTypeError, FileType
from io import TextIOWrapper
from typing import Dict, List, Set

DEFAULT_PATH_TO_STORE_INVERTED_INDEX = "inverted.index"


STOP_WORDS = {"a", "an", "the", "is", "in", "at", "of", "on", "and", "or", "as", "to"}

def clean_text(text: str) -> List[str]:
    """Clean text by removing punctuation and stop words."""
    words = re.split(r"\W+", text.lower())
    return [word for word in words if word and word not in STOP_WORDS]

class EncodedFileType(FileType):
    """File encoder"""
    def __call__(self, string):
        if string == "-":
            if "r" in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            if "w" in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            msg = 'argument "-" with mode %r' % self._mode
            raise ValueError(msg)
        try:
            return open(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as exception:
            args = {"filename": string, "error": exception}
            message = "can't open '%(filename)s': %(error)s"
            raise ArgumentTypeError(message % args)

    def print_encoder(self):
        print(self._encoding)

class InvertedIndex:
    def __init__(self, words_ids: Dict[str, Set[int]]):
        self.words_ids = words_ids

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query."""
        result_sets = [self.words_ids.get(word, set()) for word in words]
        if not result_sets:
            return []
        return sorted(set.intersection(*result_sets))

    def dump(self, filepath: str) -> None:
        """Save the inverted index to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.words_ids, f)

    @classmethod
    def load(cls, filepath: str):
        """Load an inverted index from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            words_ids = json.load(f)
        # Convert JSON lists back to sets for consistency
        words_ids = {word: set(doc_ids) for word, doc_ids in words_ids.items()}
        return cls(words_ids)

def load_documents(filepath: str) -> Dict[int, str]:
    """Load documents from a tab-delimited file."""
    documents = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            doc_id, content = line.strip().split("\t", 1)
            documents[int(doc_id)] = content
    return documents

def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Build an inverted index from documents."""
    words_ids = {}
    for doc_id, content in documents.items():
        words = clean_text(content)
        for word in words:
            words_ids.setdefault(word, set()).add(doc_id)
    return InvertedIndex(words_ids)

def callback_build(arguments) -> None:
    return process_build(arguments.dataset, arguments.output)

def process_build(dataset, output) -> None:
    documents = load_documents(dataset)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(output)

def callback_query(arguments) -> None:
    process_query(arguments.query, arguments.index)

def process_query(queries, index) -> None:
    inverted_index = InvertedIndex.load(index)
    for query in queries:
        if isinstance(query, str):
            query = clean_text(query)
        doc_indexes = ",".join(map(str, inverted_index.query(query)))
        print(doc_indexes)

def setup_subparsers(parser) -> None:
    subparser = parser.add_subparsers(dest="command")
    build_parser = subparser.add_parser(
        "build",
        help="Load, build, and save an inverted index based on documents",
    )
    build_parser.add_argument(
        "-d",
        "--dataset",
        required=True,
        help="Path to the file with documents."
    )
    build_parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_PATH_TO_STORE_INVERTED_INDEX,
        help="Path to save the inverted index. Default: %(default)s",
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparser.add_parser(
        "query", help="Load and apply inverted index"
    )
    query_parser.add_argument(
        "--index",
        default=DEFAULT_PATH_TO_STORE_INVERTED_INDEX,
        help="Path to the inverted index. Default: %(default)s",
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument(
        "-q",
        "--query",
        dest="query",
        action="append",
        nargs="+",
        help="Sequence of queries to process",
    )
    query_file_group.add_argument(
        "--query_from_file",
        dest="query",
        type=EncodedFileType("r", encoding="utf-8"),
        help="Query file to get queries for the inverted index",
    )
    query_parser.set_defaults(callback=callback_query)

def main():
    parser = ArgumentParser(
        description="Inverted Index CLI to build and query inverted indexes"
    )
    setup_subparsers(parser)
    arguments = parser.parse_args()

    if not hasattr(arguments, "callback"):
        parser.print_help()
        sys.exit(1)

    arguments.callback(arguments)


if __name__ == "__main__":
    main()

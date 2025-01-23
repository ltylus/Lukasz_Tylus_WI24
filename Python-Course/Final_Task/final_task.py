import sys
from argparse import ArgumentParser, ArgumentTypeError, FileType
from io import TextIOWrapper
from typing import Dict, List
import re
import json

DEFAULT_PATH_TO_STORE_INVERTED_INDEX = "inverted.index"

class EncodedFileType(FileType):
    """File encoder"""

    def __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        if string == "-":
            if "r" in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            if "w" in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            msg = 'argument "-" with mode %r' % self._mode
            raise ValueError(msg)

        # all other arguments are used as file names
        try:
            return open(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as exception:
            args = {"filename": string, "error": exception}
            message = "can't open '%(filename)s': %(error)s"
            raise ArgumentTypeError(message % args)

    def print_encoder(self):
        """printer of encoder"""
        print(self._encoding)


class InvertedIndex:
    """
    This module is necessary to extract inverted indexes from documents.
    """

    def __init__(self, words_ids: Dict[str, List[int]]):
        self.words_ids = words_ids

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        result = set()
        for word in words:
            if word in self.words_ids:
                result.update(self.words_ids[word])
        return list(result)

    def dump(self, filepath: str) -> None:
        """
        Allow us to write inverted indexes documents to temporary directory or local storage
        :param filepath: path to file with documents
        :return: None
        """
        with open(filepath, "w") as f:
            json.dump(self.words_ids, f)

    @classmethod
    def load(cls, filepath: str):
        """
        Allow us to upload inverted indexes from either temporary directory or local storage
        :param filepath: path to file with documents
        :return: InvertedIndex
        """
        with open(filepath, "r") as f:
            words_ids = json.load(f)
        return cls(words_ids)


def load_documents(filepath: str) -> Dict[int, str]:
    """
    Allow us to upload documents from either temporary directory or local storage
    :param filepath: path to file with documents
    :return: Dict[int, str]
    """
    documents = {}
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            doc_id, content = line.lower().split("\t", 1)
            doc_id = int(doc_id)
            documents[doc_id] = content.strip()
    return documents


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """
    Builder of inverted indexes based on documents
    :param documents: dict with documents
    :return: InvertedIndex class
    """
    inverted_index = {}
    for doc_id, content in documents.items():
        words = re.split(r"\W+", content)
        for word in words:
            if word:
                if word not in inverted_index:
                    inverted_index[word] = []
                inverted_index[word].append(doc_id)
    return InvertedIndex(inverted_index)


def callback_build(arguments) -> None:
    """process build runner"""
    return process_build(arguments.dataset, arguments.output)


def process_build(dataset, output) -> None:
    """
    Function is responsible for running of a pipeline to load documents,
    build and save inverted index.
    :param arguments: key/value pairs of arguments from 'build' subparser
    :return: None
    """
    documents: Dict[int, str] = load_documents(dataset)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(output)


def callback_query(arguments) -> None:
    """ "callback query runner"""
    process_query(arguments.query, arguments.index)


def process_query(queries, index) -> None:
    """
    Function is responsible for loading inverted indexes
    and printing document indexes for key words from arguments.query
    :param arguments: key/value pairs of arguments from 'query' subparser
    :return: None
    """
    inverted_index = InvertedIndex.load(index)
    for query in queries:
        print(f"Query: {query}")
        if isinstance(query, str):
            query = query.strip().split()

        doc_indexes = ",".join(str(value) for value in inverted_index.query(query))
        print(f"Documents: {doc_indexes}")


def setup_subparsers(parser) -> None:
    """
    Initial subparsers with arguments.
    :param parser: Instance of ArgumentParser
    """
    subparser = parser.add_subparsers(dest="command")
    
    build_parser = subparser.add_parser(
        "build",
        help="this parser is needed to load, build"
        " and save inverted index based on documents",
    )
    build_parser.add_argument(
        "-d",
        "--dataset",
        required=True,
        help="You should specify path to file with documents. ",
    )
    build_parser.add_argument(
        "-s",
        "--stop_words",
        required=True,
        help="You should specify path to stop words file. ",
    )
    build_parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_PATH_TO_STORE_INVERTED_INDEX,
        help="You should specify path to save inverted index. "
        "The default: %(default)s",
    )
    build_parser.set_defaults(callback=callback_build)  

    query_parser = subparser.add_parser(
        "query", help="This parser is needed to load and apply inverted index"
    )
    query_parser.add_argument(
        "--index",
        default=DEFAULT_PATH_TO_STORE_INVERTED_INDEX,
        help="Specify the path where inverted indexes are. "
        "The default: %(default)s",
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument(
        "-q",
        "--query",
        dest="query",
        action="append",
        nargs="+",
        help="You can specify a sequence of queries to process them overall",
    )
    query_file_group.add_argument(
        "--query_from_file",
        dest="query",
        type=EncodedFileType("r", encoding="utf-8"),
        help="Query file to get queries for inverted index",
    )
    query_parser.set_defaults(callback=callback_query)  

def main():
    """
    Starter of the pipeline
    """
    parser = ArgumentParser(
        description="Inverted Index CLI is need to load, build,"
        "process query inverted index"
    )
    setup_subparsers(parser)
    arguments = parser.parse_args()
    
    if hasattr(arguments, 'callback'):
        arguments.callback(arguments)
    else:
        print("No valid command given.")


if __name__ == "__main__":
    main()

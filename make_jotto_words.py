#!/usr/bin/env python3

WORDS_FILE_NAME = "words.txt"
JOTTO_FILE_NAME = "jotto_words.txt"


def is_valid_jotto_word(word: str) -> bool | None:
    if "'" in word:
        return False
    word = word.strip()
    if len(word) == 5:
        return True


def main() -> None:
    # pass
    # read through words.txt
    # toss out words with apostrophes
    # toss out words that are not 5 letters long
    # write to jotto_words.txt
    with (
        open(WORDS_FILE_NAME, "r") as orig,
        open(
            JOTTO_FILE_NAME,
            "w",
        ) as jotto,
    ):
        for word in orig:
            word = str.upper(word)
            if is_valid_jotto_word(word):
                jotto.write(word)


if __name__ == "__main__":
    main()

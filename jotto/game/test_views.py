from .views import evaluate_guess


def test_eval_no_matches() -> None:
    secret = "abcde"
    guess = "vwxyz"

    eval = evaluate_guess(guess, secret)

    assert eval.green == 0
    assert eval.yellow == 0


def test_eval_5_green() -> None:
    secret = "abcde"
    guess = "abcde"

    eval = evaluate_guess(guess, secret)

    assert eval.green == 5
    assert eval.yellow == 0


def test_eval_1_green_1_yellow() -> None:
    secret = "award"
    guess = "chair"

    eval = evaluate_guess(guess, secret)

    assert eval.green == 1
    assert eval.yellow == 1


def test_eval_1_green_2_yellow() -> None:
    secret = "forte"
    guess = "swore"

    eval = evaluate_guess(guess, secret)

    assert eval.green == 1
    assert eval.yellow == 2


def test_eval_0_green_5_yellow() -> None:
    secret = "tough"
    guess = "ought"

    eval = evaluate_guess(guess, secret)

    assert eval.green == 0
    assert eval.yellow == 5

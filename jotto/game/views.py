import random
from django.http import HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from dataclasses import dataclass


@dataclass
class Eval:
    green: int
    yellow: int


@dataclass
class Letter:
    char: str
    color: str


@dataclass
class Guess:
    letters: list[Letter]
    eval: Eval


@dataclass
class Game:
    score: int
    status: str  # playing, won, lost


def gen_secret_word():
    with open("jotto_words.txt", "r") as words:
        secret = random.choice(words.readlines())
        secret = secret.strip()
        return secret


def evaluate_guess(guess: str, secret: str):
    green = yellow = 0
    remaining_secret = ""
    remaining_guess = ""
    # First calculate greens and skip them when counting yellows
    for g, s in zip(guess, secret):
        if g == s:
            green += 1
        else:
            remaining_guess += g
            remaining_secret += s

    # Next calculate yellow, and keep removing matched letters
    for ltr in remaining_guess:
        if ltr in remaining_secret:
            yellow += 1
            remaining_secret = remaining_secret.replace(ltr, "", 1)

    return Eval(green, yellow)


def populate_keyboard(ctx, namespace):
    # keyboard
    row_1, row_2, row_3 = [], [], []
    for letter in "QWERTYUIOP":
        row_1.append((letter, cache.get(f"{namespace}:k_{letter}_color")))
    for letter in "ASDFGHJKL":
        row_2.append((letter, cache.get(f"{namespace}:k_{letter}_color")))
    for letter in "ZXCVBNM":
        row_3.append((letter, cache.get(f"{namespace}:k_{letter}_color")))

    ctx["row_1"] = row_1
    ctx["row_2"] = row_2
    ctx["row_3"] = row_3


def populate_colors(ctx, namespace):
    color = cache.get(f"{namespace}:color")
    ctx["green_class"] = "color-deselected"
    ctx["yellow_class"] = "color-deselected"
    ctx["red_class"] = "color-deselected"
    if color:
        if color == "green":
            ctx["green_class"] = "color-selected"
        elif color == "yellow":
            ctx["yellow_class"] = "color-selected"
        elif color == "red":
            ctx["red_class"] = "color-selected"
    else:
        ctx["mode"] = "input"


def home(request):
    ctx = {}

    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key
    namespace = f"game:{session_id}"

    game = cache.get(f"{namespace}:game")
    if not game:
        game = Game(100, "playing")
        cache.set(f"{namespace}:game", game)

    ctx["game"] = game

    populate_all_game_elements(ctx, namespace)

    return render(request, "home.html", ctx)


def populate_all_game_elements(ctx, namespace):
    # secret word
    secret_word = cache.get(f"{namespace}:secret_word")
    if not secret_word:
        secret_word = gen_secret_word()
        cache.set(f"{namespace}:secret_word", secret_word)

    # guesses list
    guesses = cache.get(f"{namespace}:guesses", [])
    ctx["guesses"] = list(reversed(guesses))

    # input letters
    current_guess = cache.get(f"{namespace}:current_guess", "")
    current_guess = current_guess.ljust(5)
    ctx["guess"] = current_guess

    # keyboard in context
    populate_keyboard(ctx, namespace)

    # colors in context
    populate_colors(ctx, namespace)


def keyboard_clicked(request):
    session_id = request.session.session_key
    namespace = f"game:{session_id}"

    color = cache.get(f"{namespace}:color")
    letter = request.GET["letter"]
    current_key_color = cache.get(f"{namespace}:k_{letter}_color")
    ctx = {"letter": letter}

    if not color:
        # input mode
        ctx["mode"] = "input"
        # render the current letters added for this guess + the new letter just submitted
        current_guess = cache.get(f"{namespace}:current_guess", "")
        # handle already have 5 letters - return 204
        if len(current_guess) == 5:
            return HttpResponse(status=204)
        current_guess += letter
        # store the current letters
        cache.set(f"{namespace}:current_guess", current_guess)
        # pad to 5 characters (only for UI)
        current_guess = current_guess.ljust(5)
        ctx["guess"] = current_guess
        return render(request, "input.html", ctx)
    else:
        # highlight mode
        current_key_color = cache.get(f"{namespace}:k_{letter}_color")

        if color == current_key_color:
            # clear the letter color
            cache.delete(f"{namespace}:k_{letter}_color")
        else:
            # save the state of this letter
            cache.set(f"{namespace}:k_{letter}_color", color)
            # update the correct letter
            ctx.update({"color": color})

        return render(request, "key.html", ctx)


def backspace_clicked(request):
    session_id = request.session.session_key
    namespace = f"game:{session_id}"

    current_guess = cache.get(f"{namespace}:current_guess", "")

    # nothing to do if current guess has no letters
    if len(current_guess) == 0:
        return HttpResponse(status=204)
    # remove the last letter from the guess
    current_guess = current_guess[0 : len(current_guess) - 1]

    # store current letters
    cache.set(f"{namespace}:current_guess", current_guess)
    # pad to 5 for UI
    current_guess = current_guess.ljust(5)
    ctx = {"guess": current_guess}

    return render(request, "input.html", ctx)


def enter_clicked(request):
    session_id = request.session.session_key
    namespace = f"game:{session_id}"
    current_guess = cache.get(f"{namespace}:current_guess", "")

    # nothing to do if current guess is not 5 letters
    if len(current_guess) != 5:
        return HttpResponse(status=204)

    # score the guess against our secret word
    secret_word = cache.get(f"{namespace}:secret_word")
    assert secret_word
    eval = evaluate_guess(current_guess, secret_word)
    letters = []

    for letter in current_guess:
        # set the color based on the current keyboard values
        color = cache.get(f"{namespace}:k_{letter}_color")
        letters.append(Letter(letter, color))

    guess = Guess(letters, eval)
    guesses = cache.get(f"{namespace}:guesses", [])
    guesses.append(guess)

    game = cache.get(f"{namespace}:game")
    game.score -= 5

    if eval.green == 5:
        game.status = "won"
    elif game.score == 0:
        game.status = "lost"

    cache.set(f"{namespace}:game", game)

    ctx = {}

    ctx["game"] = game
    cache.set(f"{namespace}:guesses", guesses)
    ctx["guesses"] = list(reversed(guesses))

    # clear out current guess
    cache.delete(f"{namespace}:current_guess")
    ctx["guess"] = " " * 5

    populate_keyboard(ctx, namespace)
    populate_colors(ctx, namespace)

    return render(request, "game.html", ctx)


def guess_letter_clicked(request):
    session_id = request.session.session_key
    namespace = f"game:{session_id}"
    guesses = cache.get(f"{namespace}:guesses")
    ctx = {}
    current_color = cache.get(f"{namespace}:color")
    ctx["color"] = current_color
    ctx["id"] = request.htmx.target
    ctx["letter"] = request.GET["letter"]
    _, guess_idx, letter_idx = ctx["id"].split("_")
    guess_idx = int(guess_idx)
    letter_idx = int(letter_idx)
    guess = guesses[guess_idx]
    letter = guess.letters[letter_idx]
    letter_color = letter.color
    if current_color == letter_color:
        # clear guess letter color
        letter.color = None
    else:
        letter.color = current_color

    # update the color in the UI
    ctx["color"] = letter.color

    # persist it all for later
    cache.set(f"{namespace}:guesses", guesses)

    return render(request, "guess_letter.html", ctx)


def color_clicked(request):
    ctx = {}
    session_id = request.session.session_key
    namespace = f"game:{session_id}"
    color = cache.get(f"{namespace}:color")
    clicked_color = request.GET["color"]

    ctx["green_class"] = "color-deselected"
    ctx["yellow_class"] = "color-deselected"
    ctx["red_class"] = "color-deselected"

    if color == clicked_color:
        cache.delete(f"{namespace}:color")
        ctx["mode"] = "input"
    else:
        selected = f"{clicked_color}_class"
        ctx[selected] = "color-selected"
        cache.set(f"{namespace}:color", clicked_color)

    # guesses list
    guesses = cache.get(f"{namespace}:guesses")
    ctx["guesses"] = list(reversed(guesses))

    # input letters
    current_guess = cache.get(f"{namespace}:current_guess", "")
    current_guess = current_guess.ljust(5)
    ctx["guess"] = current_guess

    # keyboard in context
    populate_keyboard(ctx, namespace)

    game = cache.get(f"{namespace}:game")
    ctx["game"] = game

    return render(request, "game.html", ctx)


def new_game(request):
    ctx = {}

    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key
    namespace = f"game:{session_id}"

    # clear out all keys for this game only
    cache.delete_pattern(f"{namespace}*")

    game = Game(100, "playing")
    cache.set(f"{namespace}:game", game)
    ctx["game"] = game

    populate_all_game_elements(ctx, namespace)

    return render(request, "home.html", ctx)

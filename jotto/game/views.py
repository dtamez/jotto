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


def home(request):
    ctx = {}

    # guesses list
    guesses = cache.get("guesses")

    # keyboard
    row_1, row_2, row_3 = [], [], []
    for letter in "QWERTYUIOP":
        row_1.append((letter, cache.get(f"k_{letter}_color")))
    for letter in "ASDFGHJKL":
        row_2.append((letter, cache.get(f"k_{letter}_color")))
    for letter in "ZXCVBNM":
        row_3.append((letter, cache.get(f"k_{letter}_color")))
    ctx = {
        "guesses": guesses,
        "row_1": row_1,
        "row_2": row_2,
        "row_3": row_3,
    }

    # colors
    color = cache.get("color")
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

    return render(request, "home.html", ctx)


def keyboard_clicked(request):
    color = cache.get("color")
    letter = request.GET["letter"]
    current_key_color = cache.get(f"k_{letter}_color")
    ctx = {"letter": letter}

    if not color:
        # input mode
        return render(request, "input.html", ctx)
    else:
        # highlight mode
        current_key_color = cache.get(f"k_{letter}_color")

        if color == current_key_color:
            # clear the letter color
            cache.delete(f"k_{letter}_color")
        else:
            # save the state of this letter
            cache.set(f"k_{letter}_color", color)
            # update the correct letter
            ctx.update({"color": color})

        return render(request, "key.html", ctx)


def guess_letter_clicked(request):
    guesses = cache.get("guesses")
    ctx = {}
    current_color = cache.get("color")
    ctx["color"] = cache.get("color")
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
    cache.set("guesses", guesses)

    return render(request, "guess_letter.html", ctx)


def color_clicked(request):
    ctx = {}
    color = cache.get("color")
    clicked_color = request.GET["color"]

    ctx["green_class"] = "color-deselected"
    ctx["yellow_class"] = "color-deselected"
    ctx["red_class"] = "color-deselected"

    if color == clicked_color:
        cache.delete("color")
    else:
        selected = f"{clicked_color}_class"
        ctx[selected] = "color-selected"
        cache.set("color", clicked_color)

    return render(request, "colors.html", ctx)

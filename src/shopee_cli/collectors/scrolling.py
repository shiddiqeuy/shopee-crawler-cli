"""Conservative search-result scrolling."""

from collections.abc import Callable


def scroll_until_complete(
    page: object,
    get_unique_count: Callable[[], int],
    requested_limit: int,
    max_scrolls: int,
) -> int:
    """Scroll gradually until limit, max scrolls, or repeated no-growth is reached."""
    scrolls = 0
    stagnant_scrolls = 0
    previous_count = get_unique_count()

    while previous_count < requested_limit and scrolls < max_scrolls:
        page.mouse.wheel(0, 900)
        page.wait_for_timeout(900)
        scrolls += 1
        current_count = get_unique_count()
        if current_count <= previous_count:
            stagnant_scrolls += 1
        else:
            stagnant_scrolls = 0
        previous_count = current_count
        if stagnant_scrolls >= 2:
            break

    return scrolls

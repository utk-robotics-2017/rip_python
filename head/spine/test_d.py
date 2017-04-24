from decorators import type_check


@type_check
def test(i: int) -> int:
    return i

test('str')

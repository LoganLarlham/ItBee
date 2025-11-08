from it_spelling_bee.letters import mask_of, uses_only


def test_mask_basic():
    assert mask_of("abc") != 0
    assert uses_only(mask_of("aba"), mask_of("abc"))

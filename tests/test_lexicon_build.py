import sqlite3
from pathlib import Path
import os

import pytest

from it_spelling_bee.lexicon import build as build_module


def test_parse_dic_and_lists(tmp_path):
    dic_file = tmp_path / "test.dic"
    dic_file.write_text("""
# comment
cane/VERB
mela
L'AMICO/NN
""")

    s = build_module._parse_dic(dic_file, min_len=2)
    assert "cane" in s
    assert "mela" in s
    # apostrophe forms are normalized but contain apostrophe and are rejected by isalpha()
    assert "lamico" not in s

    wl = tmp_path / "wl.txt"
    wl.write_text("""
# whitelist
speciale
Cane
""")
    wset = build_module._parse_list(wl, min_len=2)
    assert "speciale" in wset
    assert "cane" in wset


def test_build_small_end_to_end(tmp_path, monkeypatch):
    # prepare fake wordfreq
    def fake_top_n_list(lang, limit):
        # includes: cane (in dict), mela (in dict), speciale (in whitelist), facebook (blacklist)
        return ["cane", "mela", "speciale", "facebook", "x"]

    def fake_zipf(tok, lang):
        return {"cane":5.0, "mela":6.0, "speciale":3.0, "facebook":8.0, "x":1.0}.get(tok, 1.0)

    # Inject a fake wordfreq module into sys.modules so build() imports it
    import types, sys
    fake_mod = types.ModuleType("wordfreq")
    fake_mod.top_n_list = fake_top_n_list
    fake_mod.zipf_frequency = fake_zipf
    fake_mod.__version__ = "0.0"
    sys.modules["wordfreq"] = fake_mod

    # create dict, whitelist, blacklist
    dict_file = tmp_path / "dict.dic"
    dict_file.write_text("cane\nmela\n")
    wl_file = tmp_path / "wl.txt"
    wl_file.write_text("speciale\n")
    bl_file = tmp_path / "bl.txt"
    bl_file.write_text("facebook\n")

    out_db = tmp_path / "lexicon.sqlite"

    # run build
    build_module.build(out_db, dict_file, wl_file, bl_file, limit=10, min_len=1)

    # inspect DB
    conn = sqlite3.connect(str(out_db))
    cur = conn.cursor()
    cur.execute("SELECT clean_form, zipf, source FROM words ORDER BY clean_form")
    rows = cur.fetchall()
    conn.close()

    # expected: cane (dictionary), mela (dictionary), speciale (whitelist)
    forms = {r[0]: (r[1], r[2]) for r in rows}
    assert "cane" in forms and forms["cane"][1] == "dictionary"
    assert "mela" in forms and forms["mela"][1] == "dictionary"
    assert "speciale" in forms and forms["speciale"][1] == "whitelist"
    assert "facebook" not in forms

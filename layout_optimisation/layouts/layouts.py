from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import Layout
from layout_optimisation.layouts.mapper import generate_key_map_template

template = generate_key_map_template(cfg)
# Remove all modifiers from layouts for fair comparison
# TODO: Need to refactor this, since it is tied to particular arrangement might as well convert it with default cfg

DEFAULT_D = list("!@#$%^&*()")
DEFAULT_D += list("1234567890")
DEFAULT_D += list('`~|\?_:"<>')
DEFAULT_D += [None, "{", "'", "+", "-", "=", "}", None]
DEFAULT_D += [None] * 6

QWERTY_N = list("qwertyuiop")
QWERTY_N += list("asdfghjkl;")
QWERTY_N += list("zxcvbnm,./")
QWERTY_N += [None, "[", "↓", "↑", "←", "→", "]", None]
QWERTY_N += [None, "\t", None, "\b", " ", "\n"]
QWERTY = Layout([template(QWERTY_N), template(DEFAULT_D)])

DVORAK_N = list("/,.pyfgcrl")
DVORAK_N += list("aoeuidhtns")
DVORAK_N += list(";qjkxbmwvz")
DVORAK_N += [None, "[", "↓", "↑", "←", "→", "]", None]
DVORAK_N += [None, "\t", None, "\b", " ", "\n"]
DVORAK = Layout([template(DVORAK_N), template(DEFAULT_D)])

COLEMAK_N = list("qwfpgjluy;")
COLEMAK_N += list("arstdhneio")
COLEMAK_N += list("zxcvbkm,./")
COLEMAK_N += [None, "[", "↓", "↑", "←", "→", "]", None]
COLEMAK_N += [None, "\t", None, "\b", " ", "\n"]
COLEMAK = Layout([template(COLEMAK_N), template(DEFAULT_D)])

WORKMAN_N = list("qdrwbjfup;")
WORKMAN_N += list("ashtgyneoi")
WORKMAN_N += list("zxmcvkl,./")
WORKMAN_N += [None, "[", "↓", "↑", "←", "→", "]", None]
WORKMAN_N += [None, "\t", None, "\b", " ", "\n"]
WORKMAN = Layout([template(WORKMAN_N), template(DEFAULT_D)])

MTGAP_N = list("/pouqxdlcw")
MTGAP_N += list("inea.mhtsr")
MTGAP_N += list("jkzy,bfvg;")
MTGAP_N += [None, "[", "↓", "↑", "←", "→", "]", None]
MTGAP_N += [None, "\t", None, "\b", " ", "\n"]
MTGAP = Layout([template(MTGAP_N), template(DEFAULT_D)])

RSTHD_N = list("jcyfkzl,uq")
RSTHD_N += list("rsthdmnaio")
RSTHD_N += list("/vgpbxw.;") + [None]
RSTHD_N += [None, "[", "↓", "↑", "←", "→", "]", None]
RSTHD_N += ["\b", "e", None, "\t", " ", "\n"]
RSTHD = Layout([template(RSTHD_N), template(DEFAULT_D)])

HALMAK_N = list("wlrbz;qudj")
HALMAK_N += list("shnt,.aeoi")
HALMAK_N += list("fmvc/gpxky")
HALMAK_N += [None, "[", "↓", "↑", "←", "→", "]", None]
HALMAK_N += [None, "\t", None, "\b", " ", "\n"]
HALMAK = Layout([template(HALMAK_N), template(DEFAULT_D)])

BEAKL_N = list("qhouxgcrfz")
BEAKL_N += list("yiea.dstnb")
BEAKL_N += list("j/,k;wmlpv")
BEAKL_N += [None, "[", "↓", "↑", "←", "→", "]", None]
BEAKL_N += [None, "\t", None, "\b", " ", "\n"]
BEAKL = Layout([template(BEAKL_N), template(DEFAULT_D)])

LAYOUTS = {
    "QWERTY": QWERTY,
    "DVORAK": DVORAK,
    "COLEMAK": COLEMAK,
    "WORKMAN": WORKMAN,
    "MTGAP": MTGAP,
    "RSTHD": RSTHD,
    "HALMAK": HALMAK,
    "BEAKL": BEAKL,
}

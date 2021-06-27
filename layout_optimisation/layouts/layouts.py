from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import KeyMap, Layout, generate_key_map_template

template = generate_key_map_template(cfg)
# Remove all modifiers from layouts for fair comparison
# TODO: Need to refactor this, since it is tied to particular arrangement might as well convert it with default cfg

# UK version
QWERTY_N = list("`1234567890-=") + ["\b"]
QWERTY_N += ["\t"] + list("qwert") + [None] * 2 + list("yuiop#")
QWERTY_N += [None] + list("asdfg") + [None] * 2 + list("hjkl;'")
QWERTY_N += [None] + list("\zxcvbnm,./")
QWERTY_N += [None] * 5 + list("[]") + [None] * 3
QWERTY_N += [None] * 4 + [" "] + ["\n"]
QWERTY_S = [None] + list("!@£$%^&*()_+") + [None]
QWERTY_S += [None] * 13 + ["~"]
QWERTY_S += [None] * 12 + list(':"')
QWERTY_S += [None] + ["|"] + [None] * 7 + list("<>?")
QWERTY_S += [None] * 5 + list("{}") + [None] * 3
QWERTY_S += [None] * 6
QWERTY = Layout([template(QWERTY_N), template(QWERTY_S)])


COLEMAK_N = list("`1234567890-=") + ["\b"]
COLEMAK_N += ["\t"] + list("qwfpg") + [None] * 2 + list("jluy;#")
COLEMAK_N += [None] + list("arstd") + [None] * 2 + list("hneio'")
COLEMAK_N += [None] + list("\zxcvbkm,./")
COLEMAK_N += [None] * 5 + list("[]") + [None] * 3
COLEMAK_N += [None] * 4 + [" "] + ["\n"]
COLEMAK_S = [None] + list("!@£$%^&*()_+") + [None]
COLEMAK_S += [None] * 12 + list(":~")
COLEMAK_S += [None] * 13 + ['"']
COLEMAK_S += [None] + ["|"] + [None] * 7 + list("<>?")
COLEMAK_S += [None] * 5 + list("{}") + [None] * 3
COLEMAK_S += [None] * 6
COLEMAK = Layout([template(COLEMAK_N), template(COLEMAK_S)])

RSTHD_N = list("`78905") + [None] * 2 + list("61234\\")
RSTHD_N += ["\t"] + list("jcyfk") + [None] * 2 + list("zl,uq=")
RSTHD_N += ["\e"] + list("rsthd") + [None] * 2 + list("mnaio'")
RSTHD_N += [None] + list("/vgpbxw.;-") + [None]
RSTHD_N += ["fn", None, "[", "↓", "↑", "←", "→", "]", None, None]
RSTHD_N += ["e", "\b", None, None, "\n", " "]
RSTHD_S = list("~&*()%") + [None] * 2 + list("^!@#$|")
RSTHD_S += [None] * 10 + ["<"] + [None] * 2 + ["+"]
RSTHD_S += [None] * 13 + ['"']
RSTHD_S += [None] + ["?"] + [None] * 6 + list(">:_") + [None]
RSTHD_S += [None] * 2 + ["{"] + [None] * 4 + ["}"] + [None] * 2
RSTHD_S += [None] * 6
RSTHD = Layout([template(RSTHD_N), template(RSTHD_S)])

BEALK_N = [r"\e"] + list("40123") + [None] * 2 + list("76598") + [None]
BEALK_N += [None] + list("qhoux") + [None] + ["\b"] + list("gcrfz") + [None]
BEALK_N += list("-yiea@") + [None] + ["\d"] + list("dstnb;")
BEALK_N += [None] + list("j?!k.wmlpv") + [None]
BEALK_N += [None] * 10
BEALK_N += [" ", "\n", None, None, r"\t", None]
BEALK = Layout([template(BEALK_N)])

LAYOUTS = {"QWERTY": QWERTY, "COLEMAK": COLEMAK, "RSTHD": RSTHD, "BEALK": BEALK}

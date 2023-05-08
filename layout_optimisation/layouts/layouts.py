from __future__ import annotations

from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import Layout
from layout_optimisation.layouts.mapper import generate_key_map_template

template = generate_key_map_template(cfg)
# Remove all modifiers from layouts for fair comparison
# TODO: Need to refactor this, since it is tied to particular arrangement might as well convert it with default cfg

DEFAULT_D = list("!@#$%^&*()")
DEFAULT_D += list("9753/?2468")
DEFAULT_D += list("`~|10_:<>") + [None]
DEFAULT_D += [None, "{", "'", "+", "-", "", "}", None]
DEFAULT_D += [None] * 6

DEFAULT_BOTTOM = ["=", '"', "↓", "↑", "←", "→", "[", "]"]
DEFAULT_BOTTOM += ["\t", None, "\x1b", "\b", " ", "\n"]


QWERTY_N = list("qwertyuiop")
QWERTY_N += list("asdfghjkl;")
QWERTY_N += list("zxcvbnm,.\\")
QWERTY_N += DEFAULT_BOTTOM
QWERTY = Layout([template(QWERTY_N), template(DEFAULT_D)])

DVORAK_N = list("\\,.pyfgcrl")
DVORAK_N += list("aoeuidhtns")
DVORAK_N += list(";qjkxbmwvz")
DVORAK_N += DEFAULT_BOTTOM
DVORAK = Layout([template(DVORAK_N), template(DEFAULT_D)])

COLEMAK_N = list("qwfpgjluy;")
COLEMAK_N += list("arstdhneio")
COLEMAK_N += list("zxcvbkm,.\\")
COLEMAK_N += DEFAULT_BOTTOM
COLEMAK = Layout([template(COLEMAK_N), template(DEFAULT_D)])

WORKMAN_N = list("qdrwbjfup;")
WORKMAN_N += list("ashtgyneoi")
WORKMAN_N += list("zxmcvkl,.\\")
WORKMAN_N += DEFAULT_BOTTOM
WORKMAN = Layout([template(WORKMAN_N), template(DEFAULT_D)])

MTGAP_N = list("\\pouqxdlcw")
MTGAP_N += list("inea.mhtsr")
MTGAP_N += list("jkzy,bfvg;")
MTGAP_N += DEFAULT_BOTTOM
MTGAP = Layout([template(MTGAP_N), template(DEFAULT_D)])

RSTHD_N = list("jcyfkzl,uq")
RSTHD_N += list("rsthdmnaio")
RSTHD_N += list("\\vgpbxw.;") + [None]
RSTHD_N += ["=", '"', "↓", "↑", "←", "→", "[", "]"]
RSTHD_N += ["\t", "e", "\x1b", "\b", " ", "\n"]
RSTHD = Layout([template(RSTHD_N), template(DEFAULT_D)])

HALMAK_N = list("wlrbz;qudj")
HALMAK_N += list("shnt,.aeoi")
HALMAK_N += list("fmvc\\gpxky")
HALMAK_N += DEFAULT_BOTTOM
HALMAK = Layout([template(HALMAK_N), template(DEFAULT_D)])

BEAKL_N = list("qhouxgcrfz")
BEAKL_N += list("yiea.dstnb")
BEAKL_N += list("j\\,k;wmlpv")
BEAKL_N += DEFAULT_BOTTOM
BEAKL = Layout([template(BEAKL_N), template(DEFAULT_D)])

MK1_N = list('^h"xzvwfkq')
MK1_N += list("inar=.dsty")
MK1_N += list("umol:,cgpb")
MK1_N += list("#j↓↑←→[]")
MK1_N += ["\t", "e", "\x1b", "\b", " ", "\n"]
MK1_D = [None, "}", "|", None, None, "\\", "`", "{", ";", "$"]
MK1_D += list("9753+-2468")
MK1_D += list(")>'1*/0(_<")
MK1_D += list("&~@") + [None] + list("?!%") + [None] * 7
MK1 = Layout([template(MK1_N), template(MK1_D)])

MK2_N = list('&h"xzvwfbq')
MK2_N += list("inal=,dsty")
MK2_N += list("umor:.cgpk")
MK2_N += list("'j↓↑←→[]")
MK2_N += ["\t", "e", "\x1b", "\b", " ", "\n"]
MK2_D = [None, "}", "#", None, None, None] + list("?;{~")
MK2_D += list("9753+-2468")
MK2_D += list(")>`1*/0(_\\")
MK2_D += list("<|@") + [None] + list("!%^$") + [None] * 6
MK2 = Layout([template(MK2_N), template(MK2_D)])

MK3_N = list('|h"jxvwfpq')
MK3_N += list("iran=.dsty")
MK3_N += list("umol:,cgbk")
MK3_N += list("'z↓↑←→[]")
MK3_N += ["\t", "e", "\x1b", "\b", " ", "\n"]
MK3_D = [None] + list(">#&@$?(_") + [None]
MK3_D += list("9753+-2468")
MK3_D += list(")}`1*/0;{\\")
MK3_D += ["<", None, None] + list("^!%") + [None, "~"]
MK3_D += [None] * 6
MK3 = Layout([template(MK3_N), template(MK3_D)])

MK4_N = list("xj\"y'vwfpq")
MK4_N += list("cian=,dstl")
MK4_N += list("muoh:.rgbk")
MK4_N += list("#z↓↑←→[]")
MK4_N += ["\t", "e", "\x1b", "\b", " ", "\n"]
MK4_D = [None, "}", "&", None, None, None] + list("?;{~")
MK4_D += list("9753+-2468")
MK4_D += list(")>`1*/0(_\\")
MK4_D += list("<|@") + [None] + list("!%^$")
MK4_D += [None] * 6
MK4 = Layout([template(MK4_N), template(MK4_D)])

MK5_N = list("jfuv%qkldb")
MK5_N += list("maio=,stnc")
MK5_N += list("zwyh:.rgpx")
MK5_N += [None] + list("#↓↑←→[]")
MK5_N += ["\t", "e", "\x1b", "\b", " ", "\n"]
MK5_D = list("`'\"}|${_(>")
MK5_D += list("9753+-2468")
MK5_D += list("&;)1*/0?!\\")
MK5_D += [None] + list("~^<") + [None, "@", None, None]
MK5_D += [None] * 6
MK5 = Layout([template(MK5_N), template(MK5_D)])

MK6_N = list("jfuz`qkdlb")
MK6_N += list("maio=,stnc")
MK6_N += list("vwyh:.rgpx")
MK6_N += [None, "#", "↓", "↑", "←", "→", "[", "]"]
MK6_N += ["\t", "e", "\x1b", "\x08", " ", "\n"]
MK6_D = ["%", "'", '"', ">", "<", None, "{", "_", "(", "}"]
MK6_D += list("9753+-2468")
MK6_D += list("&;)1*/0?!\\")
MK6_D += [None, "^", "|", None, "~", "@", "$", None]
MK6_D += [None, None, None, None, None, None]
MK6 = Layout([template(MK6_N), template(MK6_D)])

MK7_N = list("jfuz&qkldb")
MK7_N += list("maio=,stnp")
MK7_N += list("vywh:.rgcx")
MK7_N += [None, "#", "↓", "↑", "←", "→", "[", "]"]
MK7_N += ["\t", "e", "\x1b", "\x08", " ", "\n"]
MK7_D = ["}", "'", '"', "|", "~", None, "{", "_", "(", "%"]
MK7_D += list("9753+-2468")
MK7_D += list("`;)1*/0?!\\")
MK7_D += ["<", "^", ">", None, None, "@", "$", None]
MK7_D += [None, None, None, None, None, None]
MK7 = Layout([template(MK7_N), template(MK7_D)])

MK8_0 = list("jfuz&qxldb")
MK8_0 += list("maio=,stnp")
MK8_0 += list("vywh:.rgck")
MK8_0 += list("!#↓↑←→[]")
MK8_0 += ["\t", "e", "\x1b", "\x08", " ", "\n"]
MK8_1 = ["<", ";", '"', "|", "~", None, "{", "_", "(", "%"]
MK8_1 += list("9753+-2468")
MK8_1 += ["`", "'", ")", "1", "*", "/", "0", "?", None, "\\"]
MK8_1 += ["}", "^", ">", None, None, "@", "$", None]
MK8_1 += [None, None, None, None, None, None]
MK8 = Layout([template(MK8_0), template(MK8_1)])

MK9_0 = list("jfuz&qkldb")
MK9_0 += list("mhio=,stnp")
MK9_0 += list("vywa:.rgcx")
MK9_0 += list('"#↓↑←→[]')
MK9_0 += ["\t", "e", "\x1b", "\x08", " ", "\n"]
MK9_1 = ["}", "'", "!", "?", "~", None, "^", "_", "(", "%"]
MK9_1 += list("9753+-2468")
MK9_1 += ["`", "{", ")", "1", "*", "/", "0", None, None, ";"]
MK9_1 += ["<", "\\", ">", "|", None, "@", "$", None]
MK9_1 += [None, None, None, None, None, None]
MK9 = Layout([template(MK9_0), template(MK9_1)])

MK10_0 = list("'fu\"q;kdlb")
MK10_0 += list("mhio=,stnc")
MK10_0 += list("vpya:.rwgx")
MK10_0 += list("zj↓↑←→[]")
MK10_0 += ["\t", "e", "\x1b", "\x08", " ", "\n"]
MK10_1 = list("|!%>~?}_(@")
MK10_1 += list("9753+-2468")
MK10_1 += ["&", "{", ")", "1", "*", "/", "0", None, None, None]
MK10_1 += ["^", "`", "<", "#", None, "\\", "$", None]
MK10_1 += [None, None, None, None, None, None]
MK10 = Layout([template(MK10_0), template(MK10_1)])

MK11_0 = list('jfu"qzkldb')
MK11_0 += list("mhio=,stnc")
MK11_0 += list("vpya:.rwgx")
MK11_0 += [None, None, "↓", "↑", "←", "→", None, None]
MK11_0 += ["\t", "e", "\x1b", "\x08", " ", "\n"]
MK11_1 = list("}'%^~?`(_{")
MK11_1 += list("9753+-2468")
MK11_1 += list("&])1*/0;![")
MK11_1 += ["|", "$", "<", None, "\\", "#", ">", "@"]
MK11_1 += [None, None, None, None, None, None]
MK11 = Layout([template(MK11_0), template(MK11_1)])

TMP_0 = list('jfu"qzkdlb')
TMP_0 += list("mhio=,stnc")
TMP_0 += list("vpya:.rwgx")
TMP_0 += [None, None, *list("↓↑←→"), None, None]
TMP_0 += ["\t", "e", "\x1b", "\x08", " ", "\n"]
TMP_1 = list("|!%>~?}_(@")
TMP_1 += list("9753+-2468")
TMP_1 += ["&", "{", ")", "1", "*", "/", "0", ";", "'", None]
TMP_1 += ["^", "`", "<", "#", "$", "\\", "[", "]"]
TMP_1 += [None, None, None, None, None, None]
TMP = Layout([template(TMP_0), template(TMP_1)])

LAYOUTS = {
    "QWERTY": QWERTY,
    "DVORAK": DVORAK,
    "COLEMAK": COLEMAK,
    "WORKMAN": WORKMAN,
    "MTGAP": MTGAP,
    "RSTHD": RSTHD,
    "HALMAK": HALMAK,
    "BEAKL": BEAKL,
    "MK1": MK1,
    "MK2": MK2,
    "MK3": MK3,
    "MK4": MK4,
    "MK5": MK5,
    "MK6": MK6,
    "MK7": MK7,
    "MK8": MK8,
    "MK9": MK9,
    "MK10": MK10,
    "MK11": MK11,
    "TMP": TMP,
}

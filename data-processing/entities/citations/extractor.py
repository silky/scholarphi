import logging
import re
from typing import Iterator, List, Optional, Set

from TexSoup import RArg, TexNode, TexSoup, TokenWithPosition

from common.parse_tex import TexSoupParseError, parse_soup
from common.scan_tex import Pattern, scan_tex

from .types import Bibitem


class BibitemExtractor:
    def __init__(self) -> None:
        self.current_bibitem_label: Optional[str] = None
        self.bibitem_text = ""
        self.nodes_scanned: Set[TexNode] = set()
        self.bibitems: List[Bibitem] = []

    def parse(self, tex: str) -> Iterator[Bibitem]:
        bibitem_pattern = Pattern("bibitem", r"\\bibitem.*?(?=\\bibitem|\n\n|$|\\end{)")
        for bibitem in scan_tex(tex, [bibitem_pattern]):
            try:
                bibitem_soup = parse_soup(bibitem.text)
            except TexSoupParseError:
                continue
            key = self._extract_key(bibitem_soup)
            tokens = self._extract_text(bibitem_soup)
            if key is None:
                logging.warning(
                    "Detected bibitem with null key %s. Skipping.", str(bibitem_soup)
                )
                continue
            yield Bibitem(
                id_=key,
                text=tokens,
                start=-1,
                end=-1,
                tex_path="N/A",
                tex="N/A",
                context_tex="N/A",
            )

    def _extract_key(self, bibitem: TexSoup) -> Optional[str]:
        for arg in bibitem[0].args:
            if isinstance(arg, RArg):
                return str(arg.value)
        return None

    def _extract_text(self, bibitem: TexSoup) -> str:
        text = ""
        for content in list(bibitem.contents)[1:]:
            if isinstance(content, TexNode) and content.string is not None:
                text += content.string
            # One common pattern in TeX is to force capitalization for a bibliography entry by
            # surrounding tokens with curly braces. This gets interpreted (incorrectly)
            # by TeXSoup as an RArg. Here, the contents of an RArg are extracted as literal
            # text. A space is appended after the RArg's value because TeXSoup will remove the
            # spaces between what it interprets as RArgs. As only approximate matching will be
            # performed on the text, erroneous insertion of spaces shouldn't be an issue.
            if isinstance(content, RArg):
                text += content.value + " "
            elif isinstance(content, TokenWithPosition):
                text += str(content)
        return _clean_bibitem_text(text)


def _clean_bibitem_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

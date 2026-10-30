"""
CV text extraction.

Supported formats:
  * PDF  (PyMuPDF)
  * DOCX / DOCM / DOTX (Word 2007+), read straight from the XML so text in
    text boxes, nested tables, headers and footers is included. Most CV
    templates (Word, Canva exports) put their content in text boxes, which
    python-docx's paragraph/table API never sees.
  * DOC  (Word 97-2003), via the document's piece table (olefile)
  * ODT  (LibreOffice / Google Docs "OpenDocument")
  * RTF
  * TXT

The format is detected from the file's content, not its name, because
people's files are often misnamed: an old .doc saved as ".docx", or a
WhatsApp download with no extension at all.

Also performs light section detection (experience / education / projects /
skills) using heading heuristics, so downstream evidence analysis can use
section context (e.g. a skill mentioned inside "Experience" carries more
weight than one mentioned in an unrelated section).
"""
from __future__ import annotations

import io
import re
import struct
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import fitz  # PyMuPDF


class CVExtractionError(Exception):
    """Raised when a CV file cannot be read or contains no usable text."""


SUPPORTED_FORMATS_TEXT = "PDF, Word (.docx or .doc), OpenDocument (.odt), RTF or plain text"

# Guard against zip bombs: no single XML part of a CV needs to be this big.
MAX_XML_PART_BYTES = 25 * 1024 * 1024

SECTION_HEADINGS = {
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "education": ["education", "academic background", "qualifications"],
    "projects": ["projects", "personal projects", "portfolio"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "summary": ["summary", "profile", "about", "objective"],
}


@dataclass
class ExtractedCV:
    raw_text: str
    sections: Dict[str, str] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return len(self.raw_text.strip()) < 30


def _detect_sections(lines: List[str]) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {key: [] for key in SECTION_HEADINGS}
    sections["other"] = []
    current = "other"

    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower().strip(":").strip()
        matched_section = None
        if 0 < len(lowered) <= 40:
            for key, headings in SECTION_HEADINGS.items():
                if lowered in headings:
                    matched_section = key
                    break
        if matched_section:
            current = matched_section
            continue
        sections[current].append(stripped)

    return {key: "\n".join(v) for key, v in sections.items()}


def _build(lines: List[str], empty_message: str) -> ExtractedCV:
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l]
    raw_text = "\n".join(lines)
    if not raw_text.strip():
        raise CVExtractionError(empty_message)
    return ExtractedCV(raw_text=raw_text, sections=_detect_sections(lines))


# --------------------------------------------------------------------- PDF

def extract_from_pdf(file_bytes: bytes) -> ExtractedCV:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # noqa: BLE001
        raise CVExtractionError("We couldn't open this PDF. It may be damaged or password-protected.") from exc

    try:
        if doc.needs_pass:
            raise CVExtractionError("This PDF is password-protected. Please upload a copy without a password.")
        text_parts = [page.get_text("text") for page in doc]
        raw_text = "\n".join(text_parts)
    finally:
        doc.close()

    if not raw_text.strip():
        raise CVExtractionError(
            "This PDF has no readable text. It's probably a scan or a photo of your CV. "
            "Please upload the Word file you typed it in, or a PDF saved from Word or Google Docs."
        )

    return ExtractedCV(raw_text=raw_text, sections=_detect_sections(raw_text.splitlines()))


# ----------------------------------------------------- zip-based formats

def _read_zip_part(zf: zipfile.ZipFile, name: str) -> bytes:
    info = zf.getinfo(name)
    if info.file_size > MAX_XML_PART_BYTES:
        raise CVExtractionError("This file is too large to read.")
    return zf.read(name)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _ns(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _wordml_lines(xml_bytes: bytes) -> List[str]:
    """Walk WordprocessingML in document order. Every <w:p> becomes a line,
    including paragraphs nested in text boxes and tables (to any depth).
    mc:Fallback is skipped because it repeats the same text box as VML."""
    root = ET.fromstring(xml_bytes)
    lines: List[str] = []

    def walk(el: ET.Element, buf: Optional[List[str]]) -> None:
        tag = el.tag
        if _ns(tag) == MC_NS and _local(tag) == "Fallback":
            return
        if _ns(tag) == W_NS:
            name = _local(tag)
            if name == "p":
                own: List[str] = []
                for child in el:
                    walk(child, own)
                lines.append("".join(own))
                return
            if buf is not None:
                if name == "t":  # w:delText (tracked deletions) is left out
                    buf.append(el.text or "")
                elif name == "tab":
                    buf.append("\t")
                elif name in ("br", "cr"):
                    buf.append("\n")
                elif name == "noBreakHyphen":
                    buf.append("-")
            if name == "tc":
                # Table cells: keep each cell on its own line(s).
                for child in el:
                    walk(child, None)
                return
        for child in el:
            walk(child, buf)

    walk(root, None)
    out: List[str] = []
    for line in lines:
        out.extend(line.split("\n"))
    return out


def extract_from_docx(file_bytes: bytes) -> ExtractedCV:
    try:
        zf = zipfile.ZipFile(io.BytesIO(file_bytes))
    except zipfile.BadZipFile as exc:
        raise CVExtractionError("We couldn't open this Word file. It may be damaged.") from exc

    with zf:
        names = zf.namelist()
        main = "word/document.xml"
        if main not in names:
            # Some generators name the main part differently; find it via [Content_Types].
            candidates = [n for n in names if n.startswith("word/") and n.endswith(".xml") and "document" in n]
            if not candidates:
                raise CVExtractionError("We couldn't find any text in this Word file.")
            main = candidates[0]

        def part_lines(name: str) -> List[str]:
            try:
                return _wordml_lines(_read_zip_part(zf, name))
            except ET.ParseError:
                return []

        headers = sorted(n for n in names if re.fullmatch(r"word/header\d*\.xml", n))
        footers = sorted(n for n in names if re.fullmatch(r"word/footer\d*\.xml", n))

        try:
            body = _wordml_lines(_read_zip_part(zf, main))
        except ET.ParseError as exc:
            raise CVExtractionError("We couldn't read this Word file. It may be damaged.") from exc

        lines: List[str] = []
        seen = set()
        for name in headers:  # name and contact details often live in the header
            for l in part_lines(name):
                if l.strip() and l not in seen:
                    seen.add(l)
                    lines.append(l)
        lines.extend(body)
        for name in footers:
            for l in part_lines(name):
                if l.strip() and l not in seen:
                    seen.add(l)
                    lines.append(l)

    return _build(lines, "This Word file has no readable text. If your CV is a picture inside Word, please type it out or upload the original file.")


TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def extract_from_odt(file_bytes: bytes) -> ExtractedCV:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            xml_bytes = _read_zip_part(zf, "content.xml")
        root = ET.fromstring(xml_bytes)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        raise CVExtractionError("We couldn't open this OpenDocument file. It may be damaged.") from exc

    lines: List[str] = []

    def walk(el: ET.Element, buf: Optional[List[str]]) -> None:
        is_text = _ns(el.tag) == TEXT_NS
        name = _local(el.tag)
        if is_text and name in ("p", "h"):
            own: List[str] = [el.text or ""]
            for child in el:
                walk(child, own)
                own.append(child.tail or "")
            lines.extend("".join(own).split("\n"))
            return
        if buf is not None and is_text:
            if name == "s":
                buf.append(" " * int(el.get(f"{{{TEXT_NS}}}c", "1") or 1))
            elif name == "tab":
                buf.append("\t")
            elif name == "line-break":
                buf.append("\n")
            else:  # span, a, etc.
                buf.append(el.text or "")
                for child in el:
                    walk(child, buf)
                    buf.append(child.tail or "")
            return
        for child in el:
            walk(child, buf)

    walk(root, None)
    return _build(lines, "This OpenDocument file has no readable text.")


# ---------------------------------------------------------------- DOC

def extract_from_doc(file_bytes: bytes) -> ExtractedCV:
    """Word 97-2003 binary. Text is assembled from the piece table (CLX) in
    the table stream, as described in [MS-DOC] 2.4.1."""
    try:
        import olefile
    except ImportError as exc:  # pragma: no cover
        raise CVExtractionError("Old Word (.doc) files aren't supported on this server yet.") from exc

    try:
        ole = olefile.OleFileIO(io.BytesIO(file_bytes))
    except Exception as exc:  # noqa: BLE001
        raise CVExtractionError("We couldn't open this Word file. It may be damaged.") from exc

    try:
        if not ole.exists("WordDocument"):
            raise CVExtractionError("This file isn't a Word document.")
        word = ole.openstream("WordDocument").read()
        if len(word) < 0x01AA:
            raise CVExtractionError("We couldn't read this Word file. It may be damaged.")
        flags = struct.unpack_from("<H", word, 0x0A)[0]
        if flags & 0x0100:  # fEncrypted
            raise CVExtractionError("This Word file is password-protected. Please upload a copy without a password.")
        table_name = "1Table" if flags & 0x0200 else "0Table"
        if not ole.exists(table_name):
            raise CVExtractionError("We couldn't read this Word file. It may be damaged.")
        table = ole.openstream(table_name).read()
        fc_clx, lcb_clx = struct.unpack_from("<II", word, 0x01A2)
        clx = table[fc_clx : fc_clx + lcb_clx]
    finally:
        ole.close()

    # Skip any Prc entries (0x01), then read the Pcdt (0x02).
    pos = 0
    while pos < len(clx) and clx[pos] == 0x01:
        cb = struct.unpack_from("<H", clx, pos + 1)[0]
        pos += 3 + cb
    if pos >= len(clx) or clx[pos] != 0x02:
        raise CVExtractionError("We couldn't read the text in this Word file.")
    lcb = struct.unpack_from("<I", clx, pos + 1)[0]
    plc = clx[pos + 5 : pos + 5 + lcb]
    n = (lcb - 4) // 12
    cps = struct.unpack_from(f"<{n + 1}I", plc, 0)

    parts: List[str] = []
    for i in range(n):
        pcd_off = 4 * (n + 1) + 8 * i
        fc_raw = struct.unpack_from("<I", plc, pcd_off + 2)[0]
        length = cps[i + 1] - cps[i]
        if length <= 0:
            continue
        if fc_raw & 0x40000000:  # compressed: 1 byte per char, cp1252
            start = (fc_raw & 0x3FFFFFFF) // 2
            parts.append(word[start : start + length].decode("cp1252", errors="replace"))
        else:
            start = fc_raw & 0x3FFFFFFF
            parts.append(word[start : start + 2 * length].decode("utf-16-le", errors="replace"))

    text = "".join(parts)
    # Word control characters: \r paragraph, \x07 cell/row end, \x0b line
    # break, \x0c page break, \x13-\x15 field markers, \x01/\x08 objects.
    text = re.sub(r"\x13[^\x14\x15]*\x14", "", text)  # drop field codes, keep results
    text = text.translate({0x0D: "\n", 0x07: "\n", 0x0B: "\n", 0x0C: "\n", 0x1E: "-", 0x1F: ""})
    text = re.sub(r"[\x00-\x08\x0e-\x1f]", "", text)
    return _build(text.split("\n"), "This Word file has no readable text.")


# ---------------------------------------------------------------- RTF / TXT

def extract_from_rtf(file_bytes: bytes) -> ExtractedCV:
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError as exc:  # pragma: no cover
        raise CVExtractionError("RTF files aren't supported on this server yet.") from exc
    try:
        text = rtf_to_text(file_bytes.decode("latin-1"), errors="ignore")
    except Exception as exc:  # noqa: BLE001
        raise CVExtractionError("We couldn't read this RTF file.") from exc
    return _build(text.splitlines(), "This RTF file has no readable text.")


def _decode_text(file_bytes: bytes) -> Optional[str]:
    if file_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        return file_bytes.decode("utf-16", errors="replace")
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
        # Reject binary that happens to decode: too many control characters.
        sample = text[:4000]
        controls = sum(1 for c in sample if ord(c) < 32 and c not in "\r\n\t")
        if sample and controls / len(sample) < 0.02:
            return text
    return None


def extract_from_text(raw_text: str) -> ExtractedCV:
    """Build an ExtractedCV directly from plain text (used by tests and any
    future direct-text-paste feature)."""
    lines = raw_text.splitlines()
    return ExtractedCV(raw_text=raw_text, sections=_detect_sections(lines))


# ---------------------------------------------------------------- dispatch

def detect_format(filename: str, file_bytes: bytes) -> Optional[str]:
    """Return 'pdf', 'docx', 'odt', 'doc', 'rtf', 'txt', 'image' or None."""
    head = file_bytes[:8]
    if b"%PDF" in file_bytes[:1024]:
        return "pdf"
    if head.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                names = set(zf.namelist())
                if "word/document.xml" in names or any(n.startswith("word/") for n in names):
                    return "docx"
                if "content.xml" in names:
                    mimetype = zf.read("mimetype").decode("ascii", "ignore") if "mimetype" in names else ""
                    if "opendocument.text" in mimetype or not mimetype:
                        return "odt"
        except zipfile.BadZipFile:
            return None
        return None
    if head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "doc"
    if file_bytes.lstrip()[:5] == b"{\\rtf":
        return "rtf"
    if head.startswith((b"\xff\xd8\xff", b"\x89PNG", b"GIF8")) or file_bytes[8:12] in (b"WEBP", b"heic", b"heix", b"mif1"):
        return "image"
    if head[4:8] == b"ftyp":
        return "image"
    if _decode_text(file_bytes) is not None:
        return "txt"
    return None


def extract_cv(filename: str, file_bytes: bytes) -> ExtractedCV:
    """Dispatch extraction based on the file's actual content."""
    fmt = detect_format(filename or "", file_bytes)
    if fmt == "pdf":
        return extract_from_pdf(file_bytes)
    if fmt == "docx":
        return extract_from_docx(file_bytes)
    if fmt == "odt":
        return extract_from_odt(file_bytes)
    if fmt == "doc":
        return extract_from_doc(file_bytes)
    if fmt == "rtf":
        return extract_from_rtf(file_bytes)
    if fmt == "txt":
        text = _decode_text(file_bytes) or ""
        return _build(text.splitlines(), "This text file is empty.")
    if fmt == "image":
        raise CVExtractionError(
            "This looks like a photo or picture of a CV. We can only read typed text, so please "
            "upload your CV as a PDF or Word file instead."
        )
    raise CVExtractionError(
        f"We can't read this type of file. Please upload your CV as a {SUPPORTED_FORMATS_TEXT} file."
    )


YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")


def extract_years_mentioned(text: str) -> List[int]:
    """Best-effort extraction of 4-digit years for recency scoring."""
    return sorted({int(m) for m in re.findall(r"\b((?:19|20)\d{2})\b", text)})

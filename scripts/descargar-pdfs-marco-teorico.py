from __future__ import annotations

import csv
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPITULO = ROOT / "capitulos" / "02-marco-teorico.tex"
BIBS = [ROOT / "referencias.bib", ROOT / "bibliografia" / "Maestria.bib"]
OUT = ROOT / "insumos" / "pdfs-marco-teorico"
MANIFEST = OUT / "manifest-pdfs-marco-teorico.csv"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cited_keys() -> list[str]:
    tex = read_text(CAPITULO)
    keys: set[str] = set()
    for match in re.finditer(r"\\(?:textcite|parencite|cite)\{([^}]+)\}", tex):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return sorted(keys)


def bib_entries() -> dict[str, str]:
    content = "\n".join(read_text(path) for path in BIBS if path.exists())
    entries: dict[str, str] = {}
    for match in re.finditer(r"@\w+\{([^,]+),(.*?)(?=\n@\w+\{|\Z)", content, flags=re.S):
        entries[match.group(1)] = match.group(0)
    return entries


def field(entry: str, name: str) -> str:
    match = re.search(rf"{name}\s*=\s*\{{(.*?)\}}\s*,", entry, flags=re.S | re.I)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def pii_from_url(url: str) -> str:
    match = re.search(r"/pii/([A-Z0-9]+)", url)
    return match.group(1) if match else ""


def candidates(url: str, doi: str) -> list[str]:
    urls: list[str] = []
    if url:
        clean = url.rstrip("/")
        host = urllib.parse.urlparse(clean).netloc.lower()
        if host.endswith("mdpi.com"):
            urls.append(clean + "/pdf")
            mdpi_direct = mdpi_resource_pdf(clean)
            if mdpi_direct:
                urls.append(mdpi_direct)
        elif "nature.com" in host:
            urls.append(clean + ".pdf")
        elif "springer.com" in host or "springeropen.com" in host:
            if doi:
                urls.append(f"https://link.springer.com/content/pdf/{doi}.pdf")
                urls.append(f"https://link.springer.com/content/pdf/{doi}.pdf?pdf=button")
                urls.append(f"{clean}.pdf")
        elif "onlinelibrary.wiley.com" in host and doi:
            urls.append(f"https://onlinelibrary.wiley.com/doi/pdf/{doi}")
        elif "e3s-conferences.org" in host:
            urls.append(clean + "/pdf")
        elif "preprints.org" in host:
            urls.append(clean + "/download")
        elif "sagepub.com" in host and doi:
            urls.append(f"https://journals.sagepub.com/doi/pdf/{doi}")
        elif "frontiersin.org" in host:
            urls.append(clean.replace("/full", "/pdf"))
        elif "sustainabledevelopment.un.org" in host and clean.lower().endswith(".pdf"):
            urls.append(clean)

        pii = pii_from_url(clean)
        if pii:
            urls.append(f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft?isDTMRedir=true&download=true")

    if doi and doi.startswith("10.3390/"):
        # MDPI DOI pattern: 10.3390/journal-volume-article
        pass

    seen: set[str] = set()
    unique: list[str] = []
    for item in urls:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def mdpi_resource_pdf(url: str) -> str:
    journal_by_issn = {
        "2071-1050": "sustainability",
        "2075-5309": "buildings",
        "1996-1073": "energies",
        "2076-3417": "applsci",
        "2412-3811": "infrastructures",
        "2673-8392": "encyclopedia",
    }
    match = re.search(r"mdpi\.com/([^/]+)/(\d+)/(\d+)/(\d+)", url)
    if not match:
        return ""
    issn, volume, _issue, article = match.groups()
    journal = journal_by_issn.get(issn)
    if not journal:
        return ""
    article_code = article.zfill(5)
    return f"https://mdpi-res.com/d_attachment/{journal}/{journal}-{int(volume):02d}-{article_code}/article_deploy/{journal}-{int(volume):02d}-{article_code}.pdf"


def download_pdf(url: str, dest: Path) -> tuple[bool, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 thesis-reference-archiver/1.0",
            "Accept": "application/pdf,text/html;q=0.8,*/*;q=0.5",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read()
            content_type = response.headers.get("content-type", "").lower()
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, f"download_error: {exc}"

    if not data.startswith(b"%PDF") and "pdf" not in content_type:
        return False, "not_pdf_response"
    if len(data) < 20_000:
        return False, "pdf_too_small"

    dest.write_bytes(data)
    return True, f"ok:{len(data)}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    entries = bib_entries()
    rows: list[dict[str, str]] = []

    for key in cited_keys():
        entry = entries.get(key, "")
        title = field(entry, "title")
        doi = field(entry, "doi")
        url = field(entry, "url")
        status = "sin_entrada_bib" if not entry else "sin_pdf_abierto_detectado"
        pdf_url = ""
        file_name = ""

        if entry:
            for candidate in candidates(url, doi):
                dest = OUT / f"{key}.pdf"
                ok, message = download_pdf(candidate, dest)
                if ok:
                    status = "descargado"
                    pdf_url = candidate
                    file_name = dest.name
                    break
                status = message
                time.sleep(0.5)

        rows.append(
            {
                "key": key,
                "status": status,
                "file": file_name,
                "title": title,
                "doi": doi,
                "source_url": url,
                "pdf_url": pdf_url,
            }
        )

    with MANIFEST.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["key", "status", "file", "title", "doi", "source_url", "pdf_url"])
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    downloaded = sum(1 for row in rows if row["status"] == "descargado")
    print(f"PDFs descargados: {downloaded}/{total}")
    print(f"Manifiesto: {MANIFEST}")


if __name__ == "__main__":
    main()

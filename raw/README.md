# raw

The sources. People put files here; Claude reads them and never changes them.

- **Name files so they sort and say what they are:** `<doc-number>_<title>_v<version>.pdf`, for example `DS0042_example-mcu-datasheet_vC.pdf`.
- **Large PDFs** (datasheets of thousands of pages): keep the whole file here if git can handle it (consider Git LFS), or keep a link in `raw/links.md` with the document number and version, and put the chapters you use as separate files next to it.
- **Office files** (pptx, docx, xlsx): add a PDF export next to the original, so the page numbers in citations stay stable.
- **Network drives:** if a folder on a shared drive is leading, write that down in the source page (`authority: leading`) and copy a snapshot here with its date.
- **Never** put keys, passwords or certificates here. See `docs/secrets.md`.

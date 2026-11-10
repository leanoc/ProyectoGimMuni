"""Exportación de reportes de historial sin dependencias externas."""

import csv
import textwrap


def export_history_csv(path: str, rows: list[tuple]) -> None:
    """Guarda el historial como CSV compatible con hojas de cálculo."""
    with open(path, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(("Fecha y hora", "Entidad", "Movimiento", "Detalle"))
        writer.writerows(rows)


def _pdf_string(value: str) -> bytes:
    encoded = value.encode("cp1252", errors="replace")
    escaped = bytearray()
    for byte in encoded:
        if byte in (ord("\\"), ord("("), ord(")")):
            escaped.extend(b"\\" + bytes((byte,)))
        elif byte < 32 or byte > 126:
            escaped.extend(f"\\{byte:03o}".encode("ascii"))
        else:
            escaped.append(byte)
    return bytes(escaped)


def _pdf_page(lines: list[str], page_number: int) -> bytes:
    page_label = _pdf_string("Página {}".format(page_number)).decode("ascii")
    content = [
        "BT",
        "/F1 14 Tf",
        "50 755 Td",
        f"({_pdf_string('Historial de movimientos - Gimnasio Municipal').decode('ascii')}) Tj",
        "/F1 9 Tf",
        "0 -22 Td",
        f"({page_label}) Tj",
        "0 -20 Td",
    ]
    for line in lines:
        content.append(f"({_pdf_string(line).decode('ascii')}) Tj")
        content.append("0 -14 Td")
    content.append("ET")
    return "\n".join(content).encode("ascii")


def export_history_pdf(path: str, rows: list[tuple]) -> None:
    """Genera un PDF paginado del historial usando solo la biblioteca estándar."""
    lines = []
    for date, entity, action, detail in rows:
        record = f"{date} | {entity} | {action}: {detail}"
        lines.extend(textwrap.wrap(record, width=96) or [""])
    if not lines:
        lines = ["Sin movimientos registrados."]

    page_lines = [lines[index:index + 48] for index in range(0, len(lines), 48)]
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    page_ids = []
    for page_number, page_content in enumerate(page_lines, start=1):
        page_id = len(objects) + 1
        content_id = page_id + 1
        page_ids.append(page_id)
        content = _pdf_page(page_content, page_number)
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
            ).encode("ascii")
        )
        objects.append(
            b"<< /Length " + str(len(content)).encode("ascii")
            + b" >>\nstream\n" + content + b"\nendstream"
        )
    objects[1] = (
        f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
        f"/Count {len(page_ids)} >>"
    ).encode("ascii")

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_number, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_number} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    with open(path, "wb") as pdf_file:
        pdf_file.write(output)

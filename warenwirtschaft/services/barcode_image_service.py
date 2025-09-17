from io import BytesIO
import barcode
from barcode.writer import SVGWriter

DEFAULT_WRITER_OPTS = {
    "module_width": 0.7,
    "module_height": 40,
    "font_size": 24,
    "text_distance": 10,
    "quiet_zone": 2,
    "write_text": True,
}

class BarcodeImageService:
    def __init__(self, code: str, *, writer_opts: dict | None = None):
        self.barcode = code
        self.writer_opts = {**DEFAULT_WRITER_OPTS, **(writer_opts or {})}

    def render_svg_bytes(self) -> bytes:
        ean = barcode.get("code128", self.barcode, writer=SVGWriter())
        buf = BytesIO()
        ean.write(buf, self.writer_opts)
        return buf.getvalue()

    def render_svg_str(self) -> str:
        return self.render_svg_bytes().decode("utf-8")

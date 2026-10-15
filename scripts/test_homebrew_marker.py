import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_to_pdf import build_pdf, _esc
from pypdf import PdfReader

class HomebrewMarkerTest(unittest.TestCase):
 """The homebrew marker (U+2697 + U+FE0F) has no glyph in the PDF's built-in Times
 fonts and prints as two black boxes. It must render as a superscript dagger."""
 def test_escape_replaces_marker(self):
  out=_esc('Scroll \u2697\ufe0f is')
  self.assertNotIn('\u2697',out);self.assertNotIn('\ufe0f',out);self.assertIn('\u2020',out)
 def test_pdf_prints_dagger_in_paragraph_and_table(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);md=root/'test-1-adventure.md'
   md.write_text('# T\n\nThe scroll \u2697\ufe0f is homebrew.\n\n| | |\n|---|---|\n| **Foe** | Gull \u2697 |\n')
   man=root/'images.json';man.write_text('[]')
   out=root/'out.pdf';build_pdf([md],man,out,title='T')
   text=''.join((p.extract_text() or '') for p in PdfReader(out).pages)
   self.assertEqual(text.count('\u2020'),2,text)

if __name__=='__main__':unittest.main()

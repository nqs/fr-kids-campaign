import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_to_pdf import build_pdf
from pypdf import PdfReader

class PortraitLayoutTest(unittest.TestCase):
 def test_portrait_page_has_only_pdf_name_below_image(self):
  asset=Path(__file__).resolve().parents[1]/'sessions/session 7/images/brine-fiend.jpg'
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);md=root/'test-3-player-handouts.md';md.write_text('# The Brine Fiend\n\n![Brine Fiend](portrait.jpg)\n\n- This description must not appear on the portrait page.\n')
   manifest=root/'images.json';manifest.write_text(json.dumps([{'url':'portrait.jpg','file':str(asset),'aspect_ratio':'3:4','portrait_name':'Brine Fiend'}]))
   out=root/'out.pdf';build_pdf([md],manifest,out,title='Test')
   r=PdfReader(out);self.assertEqual(len(r.pages),1)
   page=r.pages[0];self.assertEqual((page.extract_text() or '').strip(),'Brine Fiend')
   self.assertEqual(len(page.images),1)
   seen=[]
   def visitor(text,cm,tm,font,size):
    if text.strip():seen.append((text.strip(),cm,tm,font,size))
   page.extract_text(visitor_text=visitor)
   self.assertEqual(len(seen),1);name,cm,tm,font,size=seen[0]
   self.assertGreaterEqual(size,24)
   self.assertIn('Bold',str(font.get('/BaseFont','')))

if __name__=='__main__':unittest.main()

import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_to_pdf import build_pdf
import pymupdf

def _md(filler_paras: int, extra_rows: int) -> str:
    filler = "\n\n".join("Filler sentence that takes up a line of body text on the page. " * 6 for _ in range(filler_paras))
    rows = "\n".join(f"| 1{i%10} | Foe {i} | 13 | 22: " + "\u2610"*22 + " | note |" for i in range(extra_rows))
    return (f"# Combat Tracker \u2014 T\n\n## Encounter 1 \u2014 Test\n\n{filler}\n\n### Round Strip & Initiative\n\n"
            "**Round:** \u2610 1 \u00b7 \u2610 2\n\nNPC initiative is pre-rolled. PCs roll live.\n\n"
            "| Init | Combatant | AC | HP | Notes |\n|---|---|---|---|---|\n" + rows + "\n\n**Conditions:** Bln \u00b7 Prn\n")

class InitTableKeepTogetherTest(unittest.TestCase):
 """The 'Round Strip & Initiative' heading was stranded at a page bottom with its table on the
 next page, and an initiative table split across two pages. The heading, its intro lines and the
 whole initiative table must land on one page."""
 def _pages(self, md_text):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); md=root/'t-2-combat-tracker.md'; md.write_text(md_text)
   man=root/'images.json'; man.write_text('[]'); out=root/'o.pdf'
   build_pdf([md],man,out,title='T')
   doc=pymupdf.open(out)
   heading=[i for i,p in enumerate(doc) if p.search_for('Round Strip')]
   first=[i for i,p in enumerate(doc) if p.search_for('Foe 0')]
   last=[i for i,p in enumerate(doc) if p.search_for('Foe 7')]
   return heading, first, last
 def test_heading_not_stranded_and_table_not_split(self):
  for filler in range(4, 15):
   h,f,l=self._pages(_md(filler, 8))
   self.assertEqual(len(h),1); self.assertEqual(h,f,f'filler={filler}: heading p{h} table starts p{f}')
   self.assertEqual(f,l,f'filler={filler}: table split p{f}..p{l}')

if __name__=='__main__':unittest.main()

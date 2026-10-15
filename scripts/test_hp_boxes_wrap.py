import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_to_pdf import _hp_cell

class HpBoxesWrapTest(unittest.TestCase):
 """HP boxes were drawn as one fixed-width row: 90 HP = ~720 pt, wider than the page.
 They must wrap at 10 per row so any HP total fits an initiative-table column."""
 def test_large_hp_wraps_to_ten_per_row(self):
  boxes=_hp_cell('90: '+'\u2610'*90)[-1]
  w,h=boxes.wrap(1000,1000)
  self.assertLessEqual(w,100,w)
  self.assertEqual(len(boxes._cellvalues),9)
 def test_partial_last_row_draws_only_n_boxes(self):
  boxes=_hp_cell('22: '+'\u2610'*22)[-1]
  self.assertEqual(len(boxes._cellvalues),3)
  n=sum(1 for cmd in boxes._linecmds if cmd[0]=='BOX')
  self.assertEqual(n,22)
 def test_small_hp_stays_one_row(self):
  boxes=_hp_cell('9: '+'\u2610'*9)[-1]
  self.assertEqual(len(boxes._cellvalues),1)

if __name__=='__main__':unittest.main()

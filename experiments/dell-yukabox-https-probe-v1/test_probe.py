import unittest
from probe import Nonces
class Tests(unittest.TestCase):
 def test_exact_and_repeat(self):
  n=Nonces();self.assertTrue(n.accept('ab'*32));self.assertFalse(n.accept('ab'*32))
 def test_malformed(self):
  for value in (None,{},1,'a'*63,'a'*65,'AB'*32,'g'*64,'a'*63+'\n'):
   self.assertFalse(Nonces().accept(value))
 def test_capacity_without_replay_eviction(self):
  n=Nonces()
  for i in range(1024):self.assertTrue(n.accept(f'{i:064x}'))
  self.assertFalse(n.accept(f'{1024:064x}'));self.assertFalse(n.accept(f'{0:064x}'));self.assertEqual(len(n.seen),1024)
if __name__=='__main__':unittest.main()

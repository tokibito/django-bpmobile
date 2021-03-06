#!/usr/bin/python2.4
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Check symbol names against Unicode character names.

Verify that
- for symbols unified with existing characters the names match
- for new symbols the names are different from existing ones
- for new symbols the names are unique
"""

__author__ = "Markus Scherer"

import unittest
import emoji4unicode
import unicode_names

class UnicodeNamesTest(unittest.TestCase):
  def setUp(self):
    emoji4unicode.Load()
    unicode_names.Load()

  def testNames(self):
    cp2n = unicode_names.code_points_to_names
    n2cp = unicode_names.names_to_code_points
    self.assertEqual("263A", n2cp["WHITE SMILING FACE"])
    self.assertEqual("WHITE SMILING FACE", cp2n["263A"])

  def testSymbolNames(self):
    cp2n = unicode_names.code_points_to_names
    n2cp = unicode_names.names_to_code_points
    differences = []
    collisions = []
    for symbol in emoji4unicode.GetSymbols():
      name = symbol.GetName()
      uni = symbol.GetUnicode()
      if uni:
        unicode_name = cp2n.get(uni)
        if unicode_name and (name != unicode_name):
          msg = "name of e-%s %s differs from U+%s %s" % (symbol.id, name,
                                                          uni, unicode_name)
          print msg
          differences.append(msg)
      else:
        uni = n2cp.get(name)
        if uni:
          msg = "name of e-%s %s collides with U+%s" % (symbol.id, name, uni)
          print msg
          collisions.append(msg)
    self.failIf(differences, differences)
    self.failIf(collisions, collisions)

  def testUniqueNames(self):
    """Verify that names of new symbols are unique."""
    new_names = set()
    for symbol in emoji4unicode.GetSymbols():
      if not symbol.in_proposal or symbol.GetUnicode(): continue
      name = symbol.GetName()
      self.failIf(name in new_names, "duplicate name: %s" % name)
      new_names.add(name)


if __name__ == "__main__":
  unittest.main()

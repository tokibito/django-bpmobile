#!/bin/bash
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
#
# Author: Markus Scherer

mkdir -p ../generated
# The full chart with all information.
./gen_html.py > ../generated/full.html
# All information, but only with the symbols that are in the proposal.
./gen_html.py --only_in_proposal > ../generated/utc.html
# All symbols, but shorter format. Omits carrier character codes.
./gen_html.py --no_codes > ../generated/short.html
# Special chart for the font and glyph design.
./gen_html.py --design > ../generated/design.html

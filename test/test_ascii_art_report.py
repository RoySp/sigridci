# Copyright Software Improvement Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
from io import StringIO
from unittest import TestCase

from sigridci.sigridci.publish_options import PublishOptions, RunMode
from sigridci.sigridci.reports.ascii_art_report import AsciiArtReport


class AsciiArtReportTest(TestCase):
    maxDiff = None

    def setUp(self):
        self.options = PublishOptions("aap", "noot", RunMode.FEEDBACK_ONLY, "/tmp", targetRating=3.5)
    
    def testGetRefactoringCandidatesForNewFormat(self):
        feedback = {
            "refactoringCandidates": [{"subject":"a/b.java::Duif.vuur()","category":"introduced","metric":"UNIT_SIZE"}]
        }
        
        report = AsciiArtReport()
        unitSize = report.getRefactoringCandidates(feedback, "UNIT_SIZE")
        
        self.assertEqual(len(unitSize), 1)
        self.assertEqual(unitSize[0]["subject"], "a/b.java::Duif.vuur()")
        
    def testFormatBaseline(self):
        report = AsciiArtReport()

        self.assertEqual(report.formatBaseline({"baseline" : "20211015"}), "2021-10-15")
        self.assertEqual(report.formatBaseline({"baseline" : None}), "N/A")
        self.assertEqual(report.formatBaseline({"baseline" : ""}), "N/A")
        self.assertEqual(report.formatBaseline({}), "N/A")

    def testFormatTextRefactoringCandidate(self):
        rc1 = {"subject" : "aap", "category" : "introduced", "metric" : "UNIT_SIZE"}
        rc2 = {"subject" : "noot\nmies", "category" : "worsened", "metric" : "DUPLICATION"}
        rc3 = {"subject" : "noot::mies", "category" : "worsened", "metric" : "UNIT_SIZE"}
        
        report = AsciiArtReport()
        
        self.assertEqual(report.formatRefactoringCandidate(rc1), "Unit Size (introduced, unknown risk)\n  aap")
        self.assertEqual(report.formatRefactoringCandidate(rc2), "Duplication (worsened, unknown risk)\n  noot\n  mies")
        self.assertEqual(report.formatRefactoringCandidate(rc3), "Unit Size (worsened, unknown risk)\n  noot\n  mies")

    def testPrintRegularReport(self):
        feedback = {
            "baseline": "20220110",
            "baselineRatings": {"DUPLICATION": 4.0, "UNIT_SIZE": 4.0, "MAINTAINABILITY": 4.0},
            "changedCodeBeforeRatings": {"DUPLICATION": 4.0, "UNIT_SIZE": 4.0, "MAINTAINABILITY": 4.0},
            "newCodeRatings": {"DUPLICATION": 5.0, "UNIT_SIZE": 2.0, "MAINTAINABILITY": 3.0},
            "overallRatings": {"DUPLICATION": 4.5, "UNIT_SIZE": 3.0, "MAINTAINABILITY": 3.5},
            "refactoringCandidates": [
                {"subject": "a.py::aap()", "category": "introduced", "metric": "UNIT_SIZE", "riskCategory": "HIGH"},
                {"subject": "a.py::aap()", "category": "fixed", "metric": "UNIT_COMPLEXITY", "riskCategory": "HIGH"},
                {"subject": "a.py::aap()", "category": "worsened", "metric": "UNIT_SIZE", "riskCategory": "MODERATE"}
            ]
        }
    
        buffer = StringIO()
        report = AsciiArtReport(buffer, ansiColors=False)
        report.generate("1234", feedback, self.options)
        
        expected = """
            -------------------------------------------------------------------------------
            What went well?
            -------------------------------------------------------------------------------
            
            Unit Complexity (fixed, high risk)
              a.py
              aap()
            
            -------------------------------------------------------------------------------
            What could be better?
            -------------------------------------------------------------------------------
            
            Unit Size (introduced, high risk)
              a.py
              aap()
            
            Unit Size (worsened, moderate risk)
              a.py
              aap()
            
            -------------------------------------------------------------------------------
            Remaining technical debt
            -------------------------------------------------------------------------------
            
            0 refactoring candidates didn't get better or worse.
            
            -------------------------------------------------------------------------------
            Maintainability ratings
            -------------------------------------------------------------------------------
            
            System property          System on 2022-01-10  Before changes  New/changed code
            Volume                   N/A                   N/A             N/A             
            Duplication              4.0                   4.0             5.0             
            Unit Size                4.0                   4.0             2.0             
            Unit Complexity          N/A                   N/A             N/A             
            Unit Interfacing         N/A                   N/A             N/A             
            Module Coupling          N/A                   N/A             N/A             
            Component Independence   N/A                   N/A             N/A             
            Component Entanglement   N/A                   N/A             N/A             
            -------------------------------------------------------------------------------
            Maintainability          4.0                   4.0             3.0    
        """

        self.assertEqual(buffer.getvalue().strip(), inspect.cleandoc(expected).strip())

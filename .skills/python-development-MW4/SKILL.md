---
name: python-development-MW4
description: used when develop for MW4 application
---

When developping code for MountWizzard4 project, reflect following requirments:
1. method names, function names, variable, etc stay in camelCase format
2. source is in src/mw4
3. unit tests are in tests/unit_tests
4. all code gets tests with a test coverage of 100%
5. as a first step a plan has to be made, before implement any changes
6. the plan will be saved as a md-file with an appropriate name in root directory
7. after all changes the package will be tested to 100%
8. ruff will be used as formatter and linter when finished. All discoveries will be solved
9. as last step before completion the overall package will be tested
10. python 3.11 capabilities should be used
11. there is a clear separation between business logic in src/mw4/logic and gui in src/gui
12. for gui pyside6 is used 
13. all longer lasting calculation will be separated into worker of thew main threadPool
14. if worker is needed, the variable holding the worker should be named worker{name of the function} and the worker method should be named runner{name of the function} the full names comply to camelCase
15. type annotations should be used for all functions and methods, including return types 
16. do not take src/maw/gui/widgets into account as there were automatically generated

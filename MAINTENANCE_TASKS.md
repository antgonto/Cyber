# Suggested Maintenance Tasks

## Fix a Typo
* **Location:** `app/api/assets/router.py` line 182
* **Issue:** The docstring reads "Delete a asset", which is grammatically incorrect. Update it to "Delete an asset" to fix the typo in the API documentation.

## Fix a Bug
* **Location:** `app/api/users/router.py` lines 239-253
* **Issue:** The `create_activity_log` SQL statement lists four columns but provides seven values, which raises a database error. Align the INSERT columns with the values so activity logs can be created successfully.

## Correct a Comment/Documentation Discrepancy
* **Location:** `app/api/users/router.py` line 164
* **Issue:** The comment says "Add asset_id to params" while the code appends `user_id`. Update the comment to reference `user_id` so it matches the implementation.

## Improve a Test
* **Location:** `cyber/src/App.test.js` lines 1-8
* **Issue:** The React test still looks for the default "learn react" link that no longer appears in `App.js`. Update the expectation to assert for content that actually renders (e.g., the "Dashboard" heading) so the test reflects the current UI.

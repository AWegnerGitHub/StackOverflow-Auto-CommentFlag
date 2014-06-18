This project is designed to test several different concepts:

 - Flask; This will be my first attempt at using Flask to manage data that is used outside of the main web application. This will be a simple control panel and not much more
 - Machine learning; This will be my first attempt to any machine learning algorithms. The initial attempt will be to use Naive Bayes. If this is successful, I'll look at other algorithms
 - Stack Exchange API; This will be my first attempt at using the SE API
 
Goals of the project:
 
 - Successfully retrieve data from StackExchange's StackOverflow API
 - Successfully write data to StackOverflow via the API
 - Classify training data (StackOverflow comments) into correct type
 - Run test data against training set and receive a high ratio of correctly classified comments. This ratio is not yet defined
 - Implement a Flask control panel which will allow manual insertion of comments via a direct link; manually reclassify comments
 
Higher level goals:

 - Attempt to use different algorithms to learn comment types
 
How to run:

 - The Flask Control panel can be run from Windows by executing the `run_flask.bat` file. If it is run within Linux, then the `PYTHONPATH` needs to be modified to include the root of this project and then you can execute `python FlaskPanel\app.py`. This modification is needed so that modules at a sibling level to `FlaskPanel` can be included.

Settings:

The System has several dynamic settings. Using the Flask control panel, these can be adjusted.

 - `classify_max_character_limit` - System will attempt to classify comments less than this character limit (used in combination with other `classify_*` settings).
 - `classify_max_score` - System will attempt to classify comments that have this score or less (used in combination with other `classify_*` settings).
 - `current_status` - The current status of the flagging application. This should *NOT* be adjusted manually.
 - `current_status_datetime` - The timestamp of when `current_status` changed. This should *NOT* be adjusted manually. Should be in UTC.
 - `current_status_last_run_datetime` - The last time the flagging application ran. This should *NOT* be adjusted manually. Should be in UTC.
 - `current_status_next_run_datetime` - The next scheduled run time of the flagging application. This should *NOT* be adjusted manually. Should be in UTC.
 - `flagging_enabled` - True/False value that will determine whether to flag comments on StackOverflow
 - `flagging_max_comments_retreive` - Maximium number of comments to retrieve per run. Default is 1000 and this equates to 10 pages at 100 comments per page (10 API calls).
 - `max_history_days` - Number of previous days to include when pulling data from database.
 - `min_sleep_between_comment_fetch` - Time between comment retreivals. The system may scale this time, but it will never drop below this limit.
 - `min_sleep_between_flags` - Time between issuing a flag. The system may scale this time, but it will never drop below this limit.
 - `se_api_remaining_quota` - Number of calls to the API remaining. If this reaches zero, the system will stop retreiving comments until the next UTC day. This should *NOT* be adjusted manually.
 - `se_api_token` - StackOverflow access token used when making API calls.
 
To Do:

 - Develop initial training algorithms
 - Develop background daemon that pulls comments on scheduled basis and puts them into table
   - Develop process that looks at new comments and classifies them
 - Develop process that flags appropriate comments
   - Should use `TrainingAlgorithm` and `TrainingResult` tables
 - Populate settings in populate db (with appropriate defaults)	
 - Handle API errors and warnings
   - No more comments
   - Over quota
   - Timeout
 - Need thresholds for each classification
   - If probability is >= the threshold for that option, flag. Otherwise, don't flag
   - Thresholds need to be reviewed
 - Settings need to refresh each run to ensure updates via the UI are handled without a restart
 - Change `while loop < 30` in `retrieve_comments`
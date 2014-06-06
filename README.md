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

 
To Do:

 - Develop initial training algorithms
 - Send access token along with API calls
 - Develop background daemon that pulls comments on scheduled basis and puts them into table
 - Develop process that looks at new comments and classifies them
 - Develop process that flags appropriate comments
   - Should use `TrainingAlgorithm` and `TrainingResult` tables
 - Compress classifier results and save
   - [Compress/decompress](http://henrysmac.org/blog/2010/3/15/python-pickle-example-including-gzip-for-compression.html) pickled object and ensure it is compressed at end of script
   - [Alternative using bz2](http://stackoverflow.com/questions/18474791/decreasing-the-size-of-cpickle-objects), though it looks like [gzip is faster and bzip has better compression](http://tukaani.org/lzma/benchmarks.html)


		
 
This Naive Bayes algorithm is based off code from [python-course.eu](http://www.python-course.eu/text_classification_python.php). It's been modified to pull data from a database and dynamically determine categories.

This will be the baseline algorithm that is utilized in this project. It does not use external modules, thus will make a good baseline for comparison against other algorithms. This includes other Naive Bayes implementations in other modules. 

This is a very simple algorithm. It only learns the text of the comment and it's classification. It does not attempt to use any other attributes of the comment for learning purposes.

Notes:

 - Does not function the way expected. Everything seems to be classified as all options, except in very rare circumstances
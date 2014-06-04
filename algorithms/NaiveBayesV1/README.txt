This Naive Bayes algorithm is based off code from [python-course.eu](http://www.python-course.eu/text_classification_python.php). It's been modified to pull data from a database and dynamically determine categories.

This will be the baseline algorithm that is utilized in this project. It does not use external modules, thus will make a good baseline for comparison against other algorithms. This includes other Naive Bayes implementations in other modules. 

This is a very simple algorithm. It only learns the text of the comment and it's classification. It does not attempt to use any other attributes of the comment for learning purposes.

Results:

    -----
    Comment => looks like you need to use camelCase: nsSize
    Real => good comment
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => The division between 0 is only an example. I want to handle other errors
    Real => good comment
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => fanta I've basically just put your comment into an answer and created a jsbin
    Real => good comment
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => Loop, not condition. It should be a `while`.
    Real => good comment
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => Thats excellent thank you..
    Real => too chatty
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => thank you for spotting this. I didn't realise i missed out the post method :) @Jenz
    Real => too chatty
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => Yes it does, thank you. Anyway the third solution by Abhik does work too.
		Thanks both of you.
    Real => too chatty
    Result => [[u'good comment', 1], [u'too chatty', 1]]
    -----
    Comment => Glad to help. :) Please accept the answer when you get a chance.
    Real => too chatty
    Result => [[u'good comment', 1], [u'too chatty', 1]]
	-----
	Comment => How can you supply multiple arguments?  As in this case: a.map {|x| x.method(1,2,3)}
	Real => good comment
	Result => [[u'good comment', 1], [u'too chatty', 1]]
	-----
	Comment => mail me your code
	Real => good comment
	Result => [[u'good comment', 1], [u'too chatty', 0]]
	
Comments:

 - Does not function the way expected. Everything seems to be classified as all options, except in very rare circumstances
 - Notice how everything except the last comment (`mail me your code`) is both a `good comment` and `too chatty`. 
 - The last one is listed as `good comment`, which is 100% wrong.
 - The second to last one (`How can you supply multiple arguments?  As in this case: a.map {|x| x.method(1,2,3)}`) should be a `good comment`.
 - Most of the others should be `too chatty` only.
 
Results:

 - *Don't use this algorithm*
 
 
This Naive Bayes implementation is based off code from [stevenloria.com](http://stevenloria.com/how-to-build-a-text-classification-system-with-python-and-textblob/). It's been modified to handle my existing data.

This implementation uses the [NLTK](http://www.nltk.org/) and [TextBlob](https://textblob.readthedocs.org/en/latest/). I've briefly played with NLTK before, so I am looking forward to using it again for a more advanced project.

Like the [NaiveBayesV1 algorithm](../NaiveBayesV1/README.txt), this only learns the text of the comment and it's classification. It does not attempt to use any other attributes of the comment for learning purposes.

This version requires that the corpora for TextBlob be downloaded prior to being used. This can be accomplished by doing this:

    python -m textblob.download_corpora

A pickled copy of the classifier will be saved into the directory, to prevent the long training session from occurring, unless the `TRAIN` variable is set to true, and the pickled object exists.

Results:

This initial test pulled 700 comments at random from each of the following categories: `good comment`, `obsolete`, and `too chatty`. It split these 2100 into 1575 comments for training and 525 for testing (~75/25 split).
*Accuracy*: 0.822857142857

Training for this test took 32 minutes. This seems long for only 1575 comments to train on. Further attempts to reduce this training time will be required.

Most Informative Features:

         contains(thank) = True           too ch : good c =    154.5 : 1.0
       contains(updated) = True           obsole : good c =    123.7 : 1.0
        contains(accept) = True           too ch : good c =     48.8 : 1.0
       contains(Updated) = True           obsole : too ch =     31.8 : 1.0
         contains(fixed) = True           obsole : too ch =     23.5 : 1.0
          contains(very) = True           too ch : good c =     22.5 : 1.0
          contains(mark) = True           too ch : obsole =     19.7 : 1.0
        contains(Thanks) = True           too ch : good c =     19.2 : 1.0
          contains(http) = True           good c : too ch =     18.2 : 1.0
      contains(accepted) = True           too ch : obsole =     17.6 : 1.0
        contains(thanks) = True           too ch : good c =     17.2 : 1.0
          contains(much) = True           too ch : good c =     16.3 : 1.0
           contains(now) = True           obsole : good c =     11.5 : 1.0
        contains(helped) = True           too ch : obsole =     10.6 : 1.0
        contains(answer) = True           obsole : good c =     10.3 : 1.0
            contains(or) = True           good c : obsole =      8.4 : 1.0
        contains(really) = True           too ch : obsole =      7.9 : 1.0
            contains(Do) = True           good c : obsole =      7.9 : 1.0
            contains(my) = True           obsole : good c =      7.8 : 1.0
         contains(would) = True           good c : obsole =      7.6 : 1.0
         contains(Thank) = True           too ch : obsole =      7.3 : 1.0
         contains(great) = True           too ch : obsole =      7.3 : 1.0
          contains(mean) = True           good c : obsole =      7.2 : 1.0
           contains(how) = True           good c : too ch =      6.9 : 1.0
           contains(See) = True           obsole : good c =      6.8 : 1.0
          contains(help) = True           too ch : good c =      6.8 : 1.0
         contains(Sorry) = True           obsole : good c =      6.4 : 1.0
         contains(reply) = True           too ch : good c =      6.4 : 1.0
        contains(upvote) = True           too ch : good c =      6.4 : 1.0
         contains(check) = True           obsole : too ch =      6.2 : 1.0

It is nice to see that all 3 types are detected. 82% isn't that bad for a base line either.

---


The second test pulled 1000 comments from `too chatty` and `good comment`. It split these 2000 into 1500 comments for training and 500 for testing (~75/25 split).
*Accuracy*: 0.9

Training for this test took 28 minutes.

Most Informative Features

        contains(accept) = True           too ch : good c =     63.7 : 1.0
        contains(thanks) = True           too ch : good c =     35.1 : 1.0
          contains(mark) = True           too ch : good c =     26.2 : 1.0
          contains(What) = True           good c : too ch =     23.8 : 1.0
          contains(http) = True           good c : too ch =     19.0 : 1.0
            contains(ok) = True           too ch : good c =     14.0 : 1.0
          contains(much) = True           too ch : good c =     13.0 : 1.0
          contains(very) = True           too ch : good c =     12.2 : 1.0
        contains(helped) = True           too ch : good c =     10.4 : 1.0
         contains(added) = True           good c : too ch =      9.5 : 1.0
          contains(used) = True           good c : too ch =      9.5 : 1.0
         contains(reply) = True           too ch : good c =      9.2 : 1.0
       contains(version) = True           good c : too ch =      8.2 : 1.0
          contains(mean) = True           good c : too ch =      8.2 : 1.0
    contains(appreciate) = True           too ch : good c =      7.8 : 1.0
         contains(Great) = True           too ch : good c =      7.8 : 1.0
            contains(Hi) = True           too ch : good c =      7.8 : 1.0
        contains(Thanks) = True           too ch : good c =      7.5 : 1.0
        contains(anyway) = True           too ch : good c =      7.2 : 1.0
          contains(show) = True           good c : too ch =      6.9 : 1.0
       contains(instead) = True           good c : too ch =      6.9 : 1.0
          contains(feel) = True           too ch : good c =      6.5 : 1.0
        contains(solved) = True           too ch : good c =      6.3 : 1.0
          contains(data) = True           good c : too ch =      6.2 : 1.0
         contains(wrong) = True           good c : too ch =      6.2 : 1.0
       contains(helpful) = True           too ch : good c =      5.9 : 1.0
         contains(Works) = True           too ch : good c =      5.8 : 1.0
          contains(vote) = True           too ch : good c =      5.8 : 1.0
          contains(guys) = True           too ch : good c =      5.8 : 1.0
          contains(line) = True           good c : too ch =      5.5 : 1.0

Both types of comments are detected. The 90% detection is nice as well. The downside is that we lose the 3rd category.



Things to investigate:

 - Ways to speed up training
 - Possible custom feature extraction
   - [Objectivity of comment](https://textblob.readthedocs.org/en/latest/quickstart.html#sentiment-analysis)
 - [Updating saved](https://textblob.readthedocs.org/en/latest/classifiers.html#loading-data-and-creating-a-classifier) classifier
 - DEBUG logging with [probability](https://textblob.readthedocs.org/en/latest/classifiers.html#classifying-text) of each type


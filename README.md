# Information Retrieval and Data Mining project
This is our project for the course Information Retrieval and Data Mining given at the TU/e. It is a search engine written in Python which lets you index and search a [Collection of NIPS papers](https://www.kaggle.com/benhamner/nips-papers). It is based on the Python package Whoosh, whish is a indexing and searching library implemented in pure Python.

# Requirements
* Java Development Kit (JDK) with environt variable set (i.e. `JAVA_HOME` set to the installation directory, for example `C:\Program Files\Java\jdk1.8.0_101`)
* [Anaconda](https://www.anaconda.com/download/), which is a package manager for Python.
* Using the NLTK downloader, you have to install the following corpora and models as follows:
    * Open a python console, and enter the following statements line by line:
    ```python
    import nltk
    nltk.download()
    ```
    * A window will pop up, go to the tab __Corpora__, and go to the identifier __wordnet__. Select this identifier and click on _Download_.
* [The Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/): download and extract the folder to a desired location.
* The SQLite database of the [Collection of NIPS papers](https://www.kaggle.com/benhamner/nips-papers). Make sure to put this file (which is named `database.sqlite` by default) in the directory called `data` in the root of this project.
__NOTE__: In version 3.8.0 of CoreNLP (which is currently the lastest stable version), there is a problem with removing certain control characters from the text that will be tokenized. For some control characters, this resulted in a `JSONDecodeError`. In [this commit](https://github.com/stanfordnlp/CoreNLP/issues/522), the problem was solved. However, no there has not been a new release of the CoreNLP that contains this fix. Therefore, you should manually build the project, which can be found [here](https://github.com/stanfordnlp/CoreNLP). Building of CoreNLP is very simple, as it only requires you to have Ant and the JDK installed:
    * After following the steps listed on the repository, you will end up with a jar called `stanford-corenlp.jar`. 
    * Assuming you have downloaded and extracted the Stanford CoreNLP, go to the CoreNLP folder and remove the `stanford-corenlp-3.8.0.jar`, which came with the Stanford CoreNLP. 
    * Rename the previously build `stanford-corenlp.jar` to `stanford-corenlp-3.8.0.jar` and move it the location were you removed the jar that came origianlly with the package.  Thats it!


# Running
Our project makes use of the Stanford CoreNLP, which provides a set of human language technology tools. The Stanford CoreNLP ships with a built-in server, which requires only the CoreNLP dependencies. Previously, we used NLTK wrappers for calling the jar that would launch the JVM whenever something had to be tokenized/tagged. This proved to be very slow. By launching the CoreNLP as a server, we increase the performance of our application.

To [run the Stanford CoreNLP as a server](https://stanfordnlp.github.io/CoreNLP/corenlp-server.html), we do the following
* Go to the location to which you extracted the Stanford CoreNLP.
* Open up a command line, go the into the CoreNLP directory and enter the following command:
    ``` bash
    # Run the server using all jars in the current directory (e.g., the CoreNLP home directory)
    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -encoding utf8 -port 9000 -timeout 150000
    ```
* In the command line, the final message should be: 
```bash
[main] INFO CoreNLP - StanfordCoreNLPServer listening at /0:0:0:0:0:0:0:0:9000
```
* If no port is specified, the default port will be 9000. 
* Go into the source of the project, and open `stanford.py` in `tokenizers`, and change the port in the server url to the correct value.
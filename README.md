# Information Retrieval and Data Mining project
This is our project for the course Information Retrieval and Data Mining given at the TU/e. It is a search engine written in Python which lets you index and search a [Collection of NIPS papers](https://www.kaggle.com/benhamner/nips-papers). It is based on the Python package Whoosh, whish is a indexing and searching library implemented in pure Python.

# Requirements
* Java Development Kit (JDK) with the environment variable set (i.e. `JAVA_HOME` set to the installation directory, for example `C:\Program Files\Java\jdk1.8.0_101`)
* [Anaconda](https://www.anaconda.com/download/), which is a package manager for Python. As we will use PyPi later on, you can add the `Scripts` directory, which can be found in the Anaconda root installation directory (e.g. `C:\ProgramData\Anaconda3\Scripts`) to your PATH system variable. Make sure to reopen any terminal in order to have the `pip` command available.
* [The Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/): download and extract the folder to a desired location.
* The SQLite database of the [Collection of NIPS papers](https://www.kaggle.com/benhamner/nips-papers). Make sure to put this file (which is named `database.sqlite` by default) in the directory called `data` in the root of this project.
* The _wordnet_ and _stopwords_ resource, which can be downloaded using the NLTK Downloader. In PyCharm, open up a Python console (Tools -> Python Console) and enter the following commands:
```python
>>> import nltk
>>> nltk.download('wordnet')
>>> nltk.download('stopwords')
```

# Notes
* In version 3.8.0 of CoreNLP (which is currently the lastest stable version), there is a problem with removing certain control characters from the text that will be tokenized. For some control characters, this resulted in a `JSONDecodeError.
    In [this commit](https://github.com/stanfordnlp/CoreNLP/issues/522), the problem was solved. However, no there has not been a new release of the CoreNLP that contains this fix. Therefore, you should manually build the project, which can be found [here](https://github.com/stanfordnlp/CoreNLP). Building of CoreNLP is very simple, as it only requires you to have Ant and the JDK installed:
    * After following the steps listed on the repository, you will end up with a jar called `stanford-corenlp.jar`. 
    * Assuming you have downloaded and extracted the Stanford CoreNLP, go to the CoreNLP folder and remove the `stanford-corenlp-3.8.0.jar`, which came with the Stanford CoreNLP. 
    * Rename the previously build `stanford-corenlp.jar` to `stanford-corenlp-3.8.0.jar` and move it the location were you removed the jar that came originally with the package.  Thats it!
    * To install the required python packages, run the following command: `pip install -r requirements.txt`

* NLTk version 3.2.5 is required to run the application. Currently, conda installs NLTK 3.2.4, and ignores the correctly installed version using PyPi. To solve this:
    * Remove NLTK both from Anaconda (`conda remove nltk`) and PyPi (`pip uninstall nltk`).
    * Let (in this case) PyCharm reindex the installed packages (which happens automatically if your "focus" is on the application)
    * Install nltk using PyPi (`pip install nltk`)
    * Ignore any messages from PyCharm stating that the requirement (nltk >= 3.2.5) is not fulfilled.

* November 26th: Download the latest sqlite database from [here](https://mega.nz/#!JaZwlapR!ykH23jX7HCfOqvJbQrJo3Py69DvtyurX7lDHqp6ewCI), with more abstracts than ever.

~~* November 24th: Download the latest sqlite database from [here](https://mega.nz/#!hWBCia5C!Ml6Y4pX1IcPvl3v_mBk2QW48gK2j5Zk2YuuYNASQ49Q) including topics and new paper suggestions.~~

~~* November 16th: Download the latest sqlite database from [here](https://mega.nz/#!8PASFDyL!zPVhfNUf2x22b6meYRDqJj97bDmFc_D7JyKE8fyOsyc) with updated author suggestions from Bart and paper to author suggestions by Matthias.~~

~~* November 13th: Download the latest sqlite database from [here](https://mega.nz/#!IeRASSqZ!f4t4pV3xFTMyIanh8hMCEJlfQyi5w1x_JqtspZqwZW4). This version contains the references, authors, author graph. No topics yet, some abstracts may be missing.~~

* If you encounter the module not found exception for a local module and you are using PyCharm, then mark the corresponding directory as source. For example if PyCharm mentions that the tokenizers.stanford module is not found, then mark the indexer folder (where stanford is a child of tokenizers in indexer) as a source.
This can be done by going to File > Settings > Project Structure > indexer > Mark as source in the top of the pop up window.

* If your Windows Powershell / Git Bash doesn't respond, right click and hit Properties. In the Edit Options disable the Quick Edit mode and the Insert Mode.

* "NLTK was unable to find the `JAVA_HOME` environment variable". Make sure you have set the environment variable.
If you have done this, restart PyCharm and try again. This should work.

# Running
Our project makes use of the Stanford CoreNLP, which provides a set of human language technology tools. The Stanford CoreNLP ships with a built-in server, which requires only the CoreNLP dependencies. 

To [run the Stanford CoreNLP as a server](https://stanfordnlp.github.io/CoreNLP/corenlp-server.html), do the following:
* Go to the location to which you extracted the Stanford CoreNLP.
* Open up a command line, go the into the CoreNLP directory and enter the following command:
```bash
# Run the server using all jars in the current directory (e.g., the CoreNLP home directory)
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -encoding utf8 -lowerCase -port 9000 -timeout 800000
```

* In the command line, the final message should be: 
```bash
[main] INFO CoreNLP - StanfordCoreNLPServer listening at /0:0:0:0:0:0:0:0:9000
```

* If no port is specified, the default port will be 9000. 

# Debugging
To run the project with the web interface, you can use the following command:
```bash
python.exe manage.py runserver
```
To debug using the web interface, you can do the following in PyCharm:
* Create a new Python Run/Debug configuration
* In the Configuration tab, enter following values in the corresponding fields:
    * Script: `path\to\manage.py`
    * Script paramaters: `runserver`
    * Working directory: `path\to\projectroot`
* Run the project using this configuration

# Notes
It can happen that the output in the terminal is not showing the most recent output.
Pressing some buttons while in the terminal causes the terminal to show any unprocessed output.
Make sure to do this when you have the feeling when indexing/processing is taking forever.
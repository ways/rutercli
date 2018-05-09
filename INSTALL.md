# Install

This client depends on the [tabulate](https://pypi.python.org/pypi/tabulate) and
[colorama](https://pypi.python.org/pypi/colorama) Python packages.
To install them, run
```bash
python -m pip install -r requirements.txt
```
or
```bash
pip install -r requirements.txt
```

## On mac

```bash
brew install python3
sudo pip3 install tabulate
sudo pip3 install colors 
```

* Edit ~/.bash_profile:

```bash
export LC_ALL="nb_NO.utf-8"
export LANG="nb_NO.utf-8"
export LC_COLLATE="nb_NO.utf-8"
export LC_CTYPE="nb_NO.utf-8"
export LC_MESSAGES="nb_NO.utf-8"
export LC_MONETARY="nb_NO.utf-8"
export LC_NUMERIC="nb_NO.utf-8"
export LC_TIME="nb_NO.utf-8"
export PYTHONPATH="${PYTHONPATH}:/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python"
export PYTHONIOENCODING=UTF-8
export PATH=/usr/local/bin:$PATH
export PATH=/usr/local/sbin:$PATH
export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "
export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
```



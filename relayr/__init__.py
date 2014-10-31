from relayr.client import Client, Api


def show_docs(url=''):
    "Open online documentation with the default webbrowser in a new window."

    import webbrowser
    url = url or 'http://relayr.readthedocs.org/'
    webbrowser.open_new(url)


## TODO: Start IPython notebook in the background and open given file (?).
def show_tutorial(path=''):
    "Open IPython notebook with given path."

    # see https://gist.github.com/minrk/2620876

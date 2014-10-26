from relayr.client import Client, RelayrAPI


## TODO: Install docs folder with default installation.
def show_docs(url=''):
    "Open documentation with the default webbrowser in a new window."

    import webbrowser
    url = url or 'file:///<path>/<to>/html/index.html'
    webbrowser.open_new(url)


## TODO: Start IPython notebook in the background and open given file.
def show_tutorial(path=''):
    "Open IPython notebook with given path."

    # see https://gist.github.com/minrk/2620876

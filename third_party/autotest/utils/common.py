import os, sys
dirname = os.path.dirname(sys.modules[__name__].__file__)
autotest_dir = os.path.abspath(os.path.join(dirname, ".."))
client_dir = os.path.join(autotest_dir, "client")


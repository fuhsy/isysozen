import sys
print sys.version

import view as v
import controller as c

def main():

    view = v.View()
    controller = c.Controller(view)
    view.app.exec_()
if __name__ == '__main__':
    main()

import sys
print (sys.version)
import view as v
import controller as c
import cv2


def main():
    view = v.View()
    controller = c.Controller(view)
    sys.exit(view.app.exec_())
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()

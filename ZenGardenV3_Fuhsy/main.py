import sys
import view as v
import controller as c


def main():
    view = v.View()
    controller = c.Controller(view)
    sys.exit(view.app.exec_())
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()

import pickle
import glob


files = glob.glob("../saved_pickle/*.pickle")
print files
for file in files:
    print "-----"+file+"------"
    with open(file, "rb") as pfile:
        data = pickle.load(pfile)
    for stamp in data:
        for entry in stamp:
            print entry

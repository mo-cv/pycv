import feat_det

# imgpath = sys.argv[1]
imgpath='../images/varese.jpg'

feat_det.feat(imgpath,"SIFT")
feat_det.feat(imgpath,"SURF")
feat_det.feat(imgpath,"ORB")
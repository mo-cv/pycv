import cv2
import sys

def fd(algorithm,hessionThrehold):
    algorithms = {
    "SIFT": cv2.xfeatures2d.SIFT_create(),
    "SURF": cv2.xfeatures2d.SURF_create(float(hessionThrehold) if len(sys.argv) == 4 else 4000),
    "ORB": cv2.ORB_create()
    }
    return algorithms[algorithm]

def feat(imgpath,alg,hessionThrehold=8000):
    img = cv2.imread(imgpath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    fd_alg = fd(alg,hessionThrehold)
    keypoints, descriptor = fd_alg.detectAndCompute(gray,None)

    img = cv2.drawKeypoints(image=img, outImage=img, keypoints = keypoints, flags = 4, color = (51, 163, 236))

    cv2.imshow('keypoints', img)
    while (True):
      if cv2.waitKey(1000 / 12) & 0xff == ord("q"):
        break
    cv2.destroyAllWindows()

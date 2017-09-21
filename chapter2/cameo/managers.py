import cv2
import numpy
import time

"""
This file is not same with the code of Book.

Here tries to refactor the code of the Book to make it responsibility clear.
Make it more OO.

"""


class ImageFrameWriter(object):
    def __init__(self):
        self._imageFilename = None
        self._new = False

    def writeImageFrame(self, frame):
        if not self._new: return
        cv2.imwrite(self._imageFilename, frame)
        self._new = False

    def newWrite(self, fileName):
        self._imageFilename = fileName
        self._new = True


class VideoFrameWriter(object):
    def __init__(self):
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._capture = None
        self._writing = False

    def writeVideoFrame(self, frame, fpsEstimte):
        if not self._writing: return
        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            fps = fpsEstimte.estimate(fps)

            if fps <= 0.0:
                return
            size = (int(self._capture.get(
                cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self._videoWriter = cv2.VideoWriter(
                self._videoFilename, self._videoEncoding, fps, size)

        self._videoWriter.write(frame)

    def startWrite(self, fileName, encoding=cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')):
        self._videoFilename = fileName
        self._videoEncoding = encoding
        self._writing = True

    def stop(self):
        """Stop writing exited frames to a video file."""
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._new = False

    def isWriting(self):
        return self._writing


class FpsEstimte(object):
    def __init__(self):
        self._startTime = None
        self._framesElapsed = long(0)
        self._fpsEstimate = None

    def update(self):
        # Update the FPS estimate and related variables.
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed
        self._framesElapsed += 1

    def estimate(self, fps):
        if fps <= 0.0:
            # The capture's FPS is unknown so use an estimate.
            if self._framesElapsed < 20:
                # Wait until more frames elapse so that the
                # estimate is more stable.
                return fps
            else:
                return self._fpsEstimate
        return fps


class CaptureManager(object):
    def __init__(self, capture, previewWindowManager=None,
                 shouldMirrorPreview=False):

        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview

        self._imageFrameWriter = ImageFrameWriter()
        self._videoFrameWriter = VideoFrameWriter()
        self._fpsEstimte = FpsEstimte()

        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            # As of OpenCV 3.0, VideoCapture.retrieve() no longer supports
            # the channel argument.
            # _, self._frame = self._capture.retrieve(channel = self.channel)
            _, self._frame = self._capture.retrieve()
        return self._frame

    def enterFrame(self):
        """Capture the next frame, if any."""

        # But first, check that any previous frame was exited.
        assert not self._enteredFrame, \
            'previous enterFrame() had no matching exitFrame()'

        if self._capture is not None:
            self._enteredFrame = self._capture.grab()

    def exitFrame(self):
        """Draw to the window. Write to files. Release the frame."""

        # Check whether any grabbed frame is retrievable.
        # The getter may retrieve and cache the frame.
        if self.frame is None:
            self._enteredFrame = False
            return

        self._fpsEstimte.update()

        # Draw to the window, if any.
        if self.previewWindowManager is not None:
            if self.shouldMirrorPreview:
                mirroredFrame = numpy.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else:
                self.previewWindowManager.show(self._frame)

        # Write to the image file, if any.
        self._imageFrameWriter.writeImageFrame(self._frame)

        # Write to the video file, if any.
        self._videoFrameWriter.writeVideoFrame(self._frame, self._fpsEstimte)

        # Release the frame.
        self._frame = None
        self._enteredFrame = False

    def writeImage(self, filename):
        """Write the next exited frame to an image file."""
        self._imageFrameWriter.newWrite(filename)

    def startWritingVideo(self, filename, encoding):
        """Start writing exited frames to a video file."""
        if not self._videoFrameWriter.isWriting(): return True
        self._videoFrameWriter.startWrite(filename, encoding)
        return False

    def stopWritingVideo(self):
        """Stop writing exited frames to a video file."""
        self._videoFrameWriter.stop()


class WindowManager(object):
    def __init__(self, windowName, keypressCallback=None):
        self.keypressCallback = keypressCallback

        self._windowName = windowName
        self._isWindowCreated = False

    @property
    def isWindowCreated(self):
        return self._isWindowCreated

    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True

    def show(self, frame):
        cv2.imshow(self._windowName, frame)

    def destroyWindow(self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False

    def processEvents(self):
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            # Discard any non-ASCII info encoded by GTK.
            keycode &= 0xFF
            self.keypressCallback(keycode)

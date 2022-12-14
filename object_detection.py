
# os allows us to find the file directory of where our training image is stored
import os

# import opencv to give us access to a wide range of image processing tools
import cv2

# import numpy for a wide range of mathematical tools
import numpy as np

# K mean allows us to group clusters
from sklearn.cluster import KMeans

class object_detection():
    """
    A class used to match an image to a live video feed, identify the corners,
    and to K-mean the corners.

    ...

    Methods
    -------
    load_screen()
        Prints the keyboard commands for operating the Neato robot.
    listen()
        Reads keyboard input from the terminal, prints the last input,
        and returns the input converted to uppercase.
    run_loop()
        Publishes the key presses and moves the robot based on some inputs.
    turn_left()
        Turns the neato counter clockwise.
    turn_right()
        Turns the neato clockwise.
    neato_stop()
        stops the neato from moving.
    neato_forward()
        Moves the neato forward.
    neato_backward()
        Moves the neato backward.
    """

    # init initializes any code contained within it when an instance is created
    # all global variables & constants are defined here, stored in self
    def __init__(self):
        """
        Loads the image and stores the initial threshold values for corner filtering.

        Args:

        Returns:
        """
        # define where the training image will be stored
        self.image_dir = os.getcwd() + "/Images/train.png"
        # define a variable to store the threshold at which we keep corners
        self.corner_threshold = 0.0
        # define a variable to check how distinct a corner is (no close second match)
        self.close_match_threshold = 1.0


    def find_corners(self, image):
        """
        Finds all of the corners in an image.

        Args:
            image: an image object

        Returns:
            corners: a list of corner objects
        """
        # takes an image and returns the corners within it

        # convert the image to black and white as we only care for gradient shift
        image_bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # find the corners in the images (also commonly called key points)
        corners = cv2.SIFT_create().detect(image_bw)

        # now filter only corners that are above the predefined threshold
        # this is the response and it indicates how strong SIFT_create considers
        # a corner to be based on how much gradient shift it has in two axes
        corners = [corner for corner in corners if corner.response > self.corner_threshold]

        return corners

    def find_descriptors(self, image):
        """
        Finds the gradient descriptors of an image.

        Args:
            image: an image object

        Returns:
            descriptors: a list of descriptor objects
        """
        # find the corners of an image
        corners = self.find_corners(image)

        # create a black and white copy of the image to find the gradient descriptors
        image_bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # calculate the descriptors of each corner
        _, descriptors = cv2.SIFT_create().compute(image_bw, corners)

        return descriptors

    def corner_match(self, original, new, new_corners):
        """
        Finds the matching corners between two objects based on the
        descriptors of both images.

        Args:
            original: the descriptors of the image that a new image is
            being compared to.
            new: the descriptors of the image that will assessed how it
            matches to the original image.
            new_corners: the corners of the new image that will be assessed

        Returns:
            new_corners: a list of corner objects that are the corners
            of the new image now filtered for whether they match with
            the original image.
        """
        # matches the corners based on descriptors between the new and old image
        # original is a list of descriptors for the original image
        # new is a list of descriptors for the new image
        # new_corners is the corners of the new image

        # match the descriptors with their second and first best match
        # matches will be a list of tuples with each tuple containing the first and second
        # best match for each descriptor
        matches = cv2.BFMatcher().knnMatch(original, new, k=2)

        # now assess that the matches are good enough
        good_matches = []
        # m is the first match, n is the second best match
        for m, n in matches:
            # make sure the distance to the closest match is sufficiently better than the second closest
            # distance refers to the difference in descriptor and gradient not physical distance
            if (m.distance < self.close_match_threshold*n.distance and
                new_corners[m.trainIdx].response > self.corner_threshold):
                good_matches.append((m.queryIdx, m.trainIdx))

        # create a list of just the new image corner indices
        corner_idx = [idx[1] for idx in good_matches]
        # now find the corners that matched
        new_corners = [new_corners[i] for i in corner_idx]

        # return a list of the matching corners
        return new_corners

    def find_x(self,corners):
        """
        Finds the x points from a list of corner objects.

        Args:
            corners: a list of corner objects

        Returns:
            x: a list of the x coordinates of each corner, corresponding
            to the index of the corners
        """
        # takes a list of corners and returns a list of their x pixel coordinates
        # pt is a tuple that stores the x,y position of each corner
        x = [corner.pt[0] for corner in corners]

        return x

    def find_y(self, corners):
        """
        Finds the y points from a list of corner objects.

        Args:
            corners: a list of corner objects

        Returns:
            y: a list of the y coordinates of each corner, corresponding
            to the index of the corners
        """
        # take a list of corners and returns a list of their y pixel coordinates
        # pt is a tuple that stores the x,y position of each corner
        y = [corner.pt[1] for corner in corners]

        return y

    def change_corner_threshold(self, value):
        """
        Changes the threshold at which to filter thresholds

        Args:
            value: threshold at which to discard corners

        Returns:
        """
        # allows us to change this threshold with a slider
        self.corner_threshold = value/1000.0

    def change_match_threshold(self, value):
        """
        Changes the threshold at which a corner is considered
        a good match by how close the second match is. If a second
        match is too close to the first match, this means that the
        corner was not distinct.

        Args:
            value: threshold at which to discard corners

        Returns:
        """
        # allows us to change this threshold with a slider
        self.close_match_threshold = value/100.0

    def find_four_clusters(self, corners):
        """
        Takes a list of corner objects, performs a K-mean algorithm
        on the x and y coordinates, and then returns the center points
        of the four distinct clusters.

        Args:
            corners: a list of corner objects

        Returns:
            clusters.cluster_centers_: a list of tuples representing the
            x and y coordinates of each K-mean cluster center.
        """
        # this will only work if there are at least 6 corner coordinates
        # find the x and y coordinates of the corners
        x = self.find_x(corners)
        y = self.find_y(corners)

        # convert these lists into an array to feed into Kmean
        points = np.transpose(np.array([x, y]))

        # define the kmean equation
        kmean = KMeans(init='random',
                        n_clusters=4)

        try:
            # attempt to apply the kmean, searching for 4 clusters
            clusters = kmean.fit(points)
        except Exception:
            # if the points are not dissimilar enough then it may throw an error
            return None

        # return the center coordinates of each cluster
        return clusters.cluster_centers_




if __name__ == '__main__':
    od = object_detection()

    # create the sliders
    cv2.namedWindow('UI')
    cv2.createTrackbar('Corner Threshold',
                       'UI',
                       0,
                       100,
                       od.change_corner_threshold)
    cv2.createTrackbar('Ratio Threshold',
                       'UI',
                       100,
                       100,
                       od.change_match_threshold)

    # define where to receive the video stream
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    # find the descriptors and corners of the training image
    # load the image
    train_image = cv2.imread(od.image_dir)

    train_corners = od.find_corners(train_image)

    train_descriptors = od.find_descriptors(train_image)


    while True:
        # load the live video feed
        ret, frame = cap.read()
        if frame is None:
            continue

        # find corners that match with training photo in the new frame
        # and draw a circle wherever they are
        new_corners = od.find_corners(frame)

        # only progress if there are corners
        if len(new_corners) > 1:
            new_descriptors = od.find_descriptors(frame)
            good_corners = od.corner_match(train_descriptors, new_descriptors, new_corners)
            # if there are enough corners check for clusters
            if len(good_corners) > 5:
                cluster_coords = od.find_four_clusters(good_corners)
        else:
            # if there are not enough corners restart the loop
            continue

        if cluster_coords is not None:
            for cluster in cluster_coords:
                # draw where the cluster coordinates are
                cv2.circle(frame,(int(cluster[0]),int(cluster[1])), 5, (0,255,0), -1)

        for corner in good_corners:
            # draw a circle on the video frame where each corner is
            cv2.circle(frame,(int(corner.pt[0]),int(corner.pt[1])), 5, (0,0,255), -1)

        frame = np.array(cv2.resize(frame,
                                    (frame.shape[1]//1,
                                     frame.shape[0]//1)))
        cv2.imshow('Video Feed', frame)
        # if the user presses esc, terminate the process
        cv2.waitKey(27)
    cv2.destroyAllWindows()

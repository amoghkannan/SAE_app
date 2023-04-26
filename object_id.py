#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

def show_img():
  pub=rospy.Publisher('feed',Image,queue_size=10)
  rospy.init_node('image_feed',anonymous=True)
  rate=rospy.Rate(100)
  cap=cv2.VideoCapture(0)
  bridge=CvBridge()
  while not rospy.is_shutdown():
        ret,frame=cap.read()
        grayed=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        ret,thresh=cv2.threshold(grayed,127,255,cv2.THRESH_BINARY)
        thresh = cv2.bitwise_not(thresh) #Black background, white contour
        unknown, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for i in range(0,len(contours)):
          epsilon=0.01*cv2.arcLength(contours[i],True)
          approx=cv2.approxPolyDP(contours[i],epsilon,True)
          n_vertices=len(approx)
          M=cv2.moments(contours[i])
          if(M['m00']<0.001):
             continue
          cx=int(M['m10']/M['m00']) #To find centroid and label
          cy=int(M['m01']/M['m00'])
          if(n_vertices==3):
            if( cv2.contourArea(contours[i]))>800: #Eleiminating artifacts
              x,y,w,h = cv2.boundingRect(contours[i]) #Distinguishing using mean colour
              mean_colour= np.array(cv2.mean(frame[y:y+h,x:x+w])).astype(np.uint8)
              cv2.putText(frame,'Triangle',(cx,cy),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
              rospy.loginfo("Triangle colour is(BGR)")
              rospy.loginfo(mean_colour)         
        cv2.drawContours(frame, contours, -1, (0,255,0), 3)

        cv2.imshow('Image feed',frame)
        cv2.waitKey(0)     
        pub.publish(bridge.cv2_to_imgmsg(frame))
             
        rate.sleep()
        cv2.destroyAllWindows()

if __name__ == '__main__':
  try:
    show_img()
  except rospy.ROSInterruptException:
    pass

import cv2
import numpy as np
import pytesseract as ps

class read_img:
    __kernel_size=5
    def __init__(self, img):
        if type(img) == type(str()):
            self.gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        else:
            self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.max_y, self.max_x = np.shape(self.gray)
        self.blur_gray=cv2.GaussianBlur(self.gray,(read_img.__kernel_size, read_img.__kernel_size),0)
        
    def get_val(self):
        return self.gray, self.blur_gray, self.max_y, self.max_x
            
    def display(self, img, title='', time=0):
        # --> Show in PC 
        cv2.imshow(title, img)
        cv2.waitKey(time)
        # --> Show in google colab
        # cv2_imshow(img)
        # cv2.waitKey(time)

class detect_table:
    def __init__(self, img):
        self.img = read_img(img)
        self.line_image = self.create_lines(self.img.gray, self.img.blur_gray)
        ps.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # self.img.display(self.line_image, title='line image')
        self.text_2D, self.table_name = self.crop_box(self.img.gray, self.line_image, self.img.max_y, self.img.max_x)
        
    def get_val(self): 
        return self.text_2D, self.table_name
        
    def create_lines(self,img, blur_gray):
        self.low_threshold = 50
        self.high_threshold = 150
        self.edges = cv2.Canny(blur_gray, self.low_threshold, self.high_threshold)
        self.rho = 1  # distance resolution in pixels of the Hough grid
        self.theta = np.pi / 180  # angular resolution in radians of the Hough grid
        self.threshold = 15  # minimum number of votes (intersections in Hough grid cell)
        self.min_line_length = 170  # minimum number of pixels making up a line
        self.max_line_gap = 5  # maximum gap in pixels between connectable line segments
        self.line_image = np.copy(img) * 0  # creating a blank to draw lines on
        # Run Hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        self.lines = cv2.HoughLinesP(self.edges, self.rho, self.theta, self.threshold, np.array([]), self.min_line_length, self.max_line_gap)
        for line in self.lines:
            for x1,y1,x2,y2 in line:
                cv2.line(self.line_image,(x1,y1),(x2,y2),255,3)
        # Draw the lines on the  image
        # lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
        return self.line_image 
    
    def position_axis(self, weight_y, weight_x, max_y, max_x, line_image, gray_image):
        # Lines in axis Y
        self.lines_y = []
        for y in range(max_y):
          if sum(line_image[y]) / max_x > weight_y:
            self.lines_y.append(y)
        self.posi_lines_y = self.avg_lines(self.lines_y)
      
        self.start = 0
        for y in range(0,len(self.posi_lines_y)+1):
          try : 
            self.table_name_img = gray_image[self.start:self.posi_lines_y[y]] 
            self.start = self.posi_lines_y[y]
          except: 
            self.table_name_img = gray_image[self.start:max_y]
          self.table_name = ps.image_to_string(self.table_name_img)
          self.ref = 'Bulk Freight Indices'
          self.ref = self.ref.split()
          if all(word in self.table_name.split() for word in self.ref):
            break
        # Lines in axis X
        self.new_img = line_image[self.posi_lines_y[0]:self.posi_lines_y[len(self.posi_lines_y)-1]]
        self.new_max_y, self.new_max_x  = np.shape(self.new_img)
        self.lines_x = []
        for x in range(0,self.new_max_x): 
          self.sum_l = 0
          for y in range(0,self.new_max_y): 
            self.sum_l += self.new_img[y][x]
          if (self.sum_l/self.new_max_y) > weight_x:
            self.lines_x.append(x)
        self.posi_lines_x = self.avg_lines(self.lines_x)
      
        # Delete line in gray_image
        self.gray_image = gray_image
        for i in self.posi_lines_y: 
          cv2.line(self.gray_image,(0,i),(max_x, i),255,2)
        for i in self.posi_lines_x:
          cv2.line(self.gray_image,(i,0),(i,max_y),255,2)
        return self.posi_lines_y , self.posi_lines_x, self.gray_image, self.table_name
    
    def avg_lines(self, lines): #AVG lines Method
        self.start = 0
        self.count = 0
        self.avg = []
        for i in range(len(lines)):
          self.count += 1 
          if i != len(lines)-1:
            if lines[i+1] - lines[i] > 5:
              self.avg.append(int(sum(lines[self.start:i+1])/self.count))
              self.count = 0
              self.start = i+1
          else :
            self.avg.append(int(sum(lines[self.start:])/self.count))
        return self.avg
    
    def resize_img(self, border, blank, img_, ts): 
        # Add Blank 
        self.img = img_
        for _ in range(border): 
          b = [_ for _ in [blank]*len(self.img[0])]
          self.img.append(b)
          self.img.insert(0,b)
        self.img = np.array(self.img)
        # New Resize image
        self.b_y, self.b_x = np.shape(self.img)
        self.width = int(self.b_x*3)
        self.height = int(self.b_y*3)
        self.dim = (self.width, self.height)
        self.img_resized = cv2.resize(self.img, self.dim, interpolation = cv2.INTER_AREA)
        self.kernel_size=7
        self.img_resized_blur = cv2.GaussianBlur(self.img_resized,(self.kernel_size, self.kernel_size),0)
        self.thresh_val, self.thresh_img = cv2.threshold(self.img_resized_blur, ts, 255, cv2.THRESH_BINARY)
        return self.thresh_img, self.img_resized_blur 
    
    def crop_box(self, gray_image, line_image, max_y, max_x, weight=210):
        self.ref_col = 'Route and Vessel Size'
        self.ref_col = self.ref_col.split()
        self.ref_end = 'Source:'
        self.ref_end = self.ref_end.split()
        self.posi_lines_y, self.posi_lines_x, self.gray_image, self.table_name = self.position_axis(weight, weight, max_y, max_x, line_image, gray_image)
        self.blank = np.uint8(255)
        self.border = 10
        self.ts = [200, 90]
        self.text_2D = []
        self.status = 0
        for i in range(len(self.posi_lines_y)-1):
          self.text_1D = []
          for j in range(len(self.posi_lines_x)-1):
            self.box = []
            for y in range(self.posi_lines_y[i], self.posi_lines_y[i+1]):
              self.temp = []
              for _ in range(self.border+1):
                if _ == int(self.border/2):
                  for x in range(self.posi_lines_x[j], self.posi_lines_x[j+1]): 
                    self.temp.append(gray_image[y][x])
                else:
                  self.temp.append(self.blank)
              self.box.append(self.temp)
            self.thresh_img, self.box_resized_blur = self.resize_img(self.border, self.blank, self.box, self.ts[0])
            self.sum_all = 0
            for s in self.thresh_img:
              self.sum_all += sum(s) 
            if int(self.sum_all/(len(self.thresh_img)*len(self.thresh_img[0]))) < 150: 
              self.thresh_val, self.thresh_img = cv2.threshold(self.box_resized_blur, self.ts[1], 255, cv2.THRESH_BINARY)
            self.text = ps.image_to_string(self.thresh_img)
            print(self.text)
            if all(word in self.text.split() for word in self.ref_col):
              self.status = 1
            if self.status == 1:
              self.text_1D.append(self.text)
          if self.text_1D[:-1] != []:
            if all(word in self.text_1D[:-1][0] for word in self.ref_end):
              return self.text_2D, self.table_name
            self.text_2D.append(self.text_1D)
        return self.text_2D, self.table_name
        
if __name__ == "__main__":
    dt = detect_table('test2.jpg')
    text2D, t_name = dt.get_val()
    print('All Cell : ', text2D)
    print('Table name : ', t_name)
    
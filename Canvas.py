from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from onedollar import OneDollar
import numpy as np
import random as rd


def points_to_qpolygonF(points):
    polygon = QPolygonF()
    for elem in points:
        polygon.append( QPoint(elem[0], elem[1]) )
    return polygon

def qpolygonF_to_points(polygon):
    points = []
    for elem in polygon:
        points.append( [ elem.x(), elem.y() ] )
    return points

def interpolate(x1, y1, x2, y2, weight):
    X = x1*(1-weight) + x2*weight
    Y = y1*(1-weight) + y2*weight
    return (X,Y)


class Canvas(QWidget):


    ##########################
    # TODO 9: create a selected_template signal with three parameters: label, template_id, score
    ##########################
    selected_template = Signal(str, int, float)


    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setMinimumSize(600, 600)
        self.oneDollar = OneDollar()            #create a $1 recognizer

        self.path = QPolygonF()                 #user path
        self.feedback = QPolygonF()             #used for displaying the animated feedback trace
        self.termination = QPolygonF()          #recognized gesture

        self.animation = False

        # self.counter = None

        #############################
        # TODO 11 create a timer
        # connect the timer to the sole timout
        #############################
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        
        #############################
        # Timer for gesture help display
        #############################
        self.help_timer = QTimer()
        self.help_timer.timeout.connect(self.show_gesture_help)
        self.help_timer.setSingleShot(True)  # Only fire once
        
        self.show_help = False
        self.help_templates = []  # Will store template polygons for display



    ##############################
    def paintEvent(self, QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        if self.animation == True:
            if self.feedback != QPolygonF():
                if len(self.feedback) >0:
                    p.setPen(Qt.green)
                    p.setBrush(Qt.green)
                    p.drawPolyline(self.feedback)
                    p.drawEllipse(self.feedback[0], 2, 2)
        else:

            if self.path != QPolygonF():
                if len(self.path) >0:
                    p.setPen(Qt.blue)
                    p.setBrush(Qt.blue)
                    p.drawPolyline(self.path)
                    p.drawEllipse(self.path[0], 2, 2)

            if self.termination != QPolygonF():
                if len(self.termination) >0:
                    p.setPen(Qt.red)
                    p.setBrush(Qt.red)
                    p.drawPolyline(self.termination)
                    p.drawEllipse(self.termination[0], 2, 2)

        # # Display available gestures when help is shown
        # if self.show_help:
        #     self.draw_gesture_help(p)


    ############################
    #TODO 11 create the animation
    ############################
    def timeout(self):
        self.animation = False       #used in paintEvent to know whether it displays the traces or the animated feedback
        nb_step = 50

        # TODO 11
        # self.termination is the template
        # self.path is the original gesture
        # self.feedback is the feedback path to animate
        # Weight should be within [0,1]
        self.feedback = []
        n = len(self.path)
        for i, (p, t) in enumerate(zip(self.path, self.termination)):
            weight = i/(n-1)  # varie de 0 à 1
            x1, y1 = p.x(), p.y()
            x2, y2 = t.x(), t.y()
            self.feedback.append(interpolate(x1, y1, x2, y2, weight))

        self.path = points_to_qpolygonF(self.feedback)
        self.counter += 1
        self.repaint()

        # stop the animation after nb_step iterations
        if self.counter >= nb_step:
            self.timer.stop()
            self.feedback = QPolygonF() # optional, clean up
            self.repaint()


    ############################
    # return a QPolygon located in the surrunding of the executed gesture
    ###########################
    def get_feedback(self, template_id):
        gesture = self.oneDollar.resampled_gesture
        template = self.oneDollar.resampled_templates[template_id]

        c_g = np.mean(gesture, 0)
        c_t = np.mean(template, 0)
        g0 = gesture[0]
        t0 = template[0]
        line_g = QLineF(QPoint(c_g[0], c_g[1]), QPoint(g0[0], g0[1]))
        line_t = QLineF(QPoint(c_t[0], c_t[1]), QPoint(t0[0], t0[1]))
        angle = line_g.angleTo(line_t) * 3.14 / 180
        res = self.oneDollar.rotateBy(template, angle)

        c_t = np.mean(res, 0)

        max_gx, max_gy = np.max(gesture, 0)
        min_gx, min_gy = np.min(gesture, 0)
        gb_height = max_gy - min_gy

        max_tx, max_ty = np.max(res, 0)
        min_tx, min_ty = np.min(res, 0)
        tb_height = max_ty - min_ty

        scale = gb_height / tb_height
        newPoints = np.zeros((1, 2))
        for point in res:
            q = np.array([0., 0.])
            q[0] = point[0] * scale
            q[1] = point[1] * scale
            newPoints = np.append(newPoints, [q], 0)
        res = newPoints[1:]
        c_t = np.mean(res, 0)
        res = self.oneDollar.translate(res, [c_g[0] - c_t[0], c_g[1] - c_t[1]])
        termination = points_to_qpolygonF(res)

        return termination


    #############################
    # TODO 10 and 11
    #############################
    def display_feedback(self, template_id):

        #todo 10
        self.termination = self.get_feedback(template_id)
        print(self.termination)

        #todo 11
        self.path = points_to_qpolygonF(self.oneDollar.resampled_gesture)
        self.feedback = self.path

        # #create a timer
        self.counter = 0
        self.timer.setInterval(100)
        self.timer.start()

        self.update()


    # ##############################
    # def show_gesture_help(self):
    #     """Called when help timer expires - prepares templates for display"""
    #     self.show_help = True
    #     self.prepare_help_templates()
    #     self.repaint()

    # ##############################
    # def prepare_help_templates(self):
    #     """Prepare scaled templates for help display"""
    #     self.help_templates = []
    #     canvas_width = self.width()
    #     canvas_height = self.height()
        
    #     # Grid layout parameters
    #     cols = 4  # Number of columns
    #     rows = 4  # Number of rows
    #     template_size = 80  # Size of each template display
    #     padding = 20
        
    #     grid_width = cols * (template_size + padding)
    #     grid_height = rows * (template_size + padding)
        
    #     start_x = (canvas_width - grid_width) // 2
    #     start_y = (canvas_height - grid_height) // 2
        
    #     for i, (template, label) in enumerate(zip(self.oneDollar.resampled_templates, self.oneDollar.labels)):
    #         if i >= cols * rows:  # Don't show more than grid can hold
    #             break
                
    #         row = i // cols
    #         col = i % cols
            
    #         # Calculate position for this template
    #         x = start_x + col * (template_size + padding)
    #         y = start_y + row * (template_size + padding)
            
    #         # Scale template to fit in the display area
    #         scaled_template = self.scale_template_for_display(template, x, y, template_size)
            
    #         self.help_templates.append({
    #             'template': scaled_template,
    #             'label': label,
    #             'x': x,
    #             'y': y,
    #             'size': template_size
    #         })

    # ##############################
    # def scale_template_for_display(self, template, x, y, size):
    #     """Scale a template to fit in the given display area"""
    #     if not template:
    #         return []
            
    #     # Convert template to numpy array for easier manipulation
    #     points = np.array(template)
        
    #     # Get bounding box
    #     min_x, min_y = np.min(points, axis=0)
    #     max_x, max_y = np.max(points, axis=0)
        
    #     # Calculate scale to fit in the display area (with some padding)
    #     template_width = max_x - min_x
    #     template_height = max_y - min_y
        
    #     if template_width == 0 or template_height == 0:
    #         return []
            
    #     scale_x = (size * 0.8) / template_width
    #     scale_y = (size * 0.8) / template_height
    #     scale = min(scale_x, scale_y)  # Use smaller scale to maintain aspect ratio
        
    #     # Scale and center the template
    #     scaled_points = []
    #     center_x = x + size // 2
    #     center_y = y + size // 2
        
    #     template_center_x = (min_x + max_x) / 2
    #     template_center_y = (min_y + max_y) / 2
        
    #     for point in points:
    #         # Scale around template center
    #         scaled_x = (point[0] - template_center_x) * scale
    #         scaled_y = (point[1] - template_center_y) * scale
            
    #         # Translate to display position
    #         final_x = center_x + scaled_x
    #         final_y = center_y + scaled_y
            
    #         scaled_points.append([final_x, final_y])
            
    #     return scaled_points

    # ##############################
    # def draw_gesture_help(self, painter):
    #     """Draw the gesture help overlay"""
    #     # Draw semi-transparent background
    #     painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        
    #     # Draw title
    #     painter.setPen(QColor(255, 255, 255))
    #     painter.setFont(QFont("Arial", 16, QFont.Bold))
    #     title_rect = QRect(0, 20, self.width(), 30)
    #     painter.drawText(title_rect, Qt.AlignCenter, "Available Gestures")
        
    #     # Draw instruction
    #     painter.setFont(QFont("Arial", 10))
    #     instruction_rect = QRect(0, 50, self.width(), 20)
    #     painter.drawText(instruction_rect, Qt.AlignCenter, "Continue drawing to dismiss this help")
        
    #     # Draw templates
    #     for template_info in self.help_templates:
    #         template = template_info['template']
    #         label = template_info['label']
    #         x = template_info['x']
    #         y = template_info['y']
    #         size = template_info['size']
            
    #         # Draw template background
    #         painter.setPen(QColor(100, 100, 100))
    #         painter.setBrush(QColor(50, 50, 50, 100))
    #         painter.drawRect(x, y, size, size)
            
    #         # Draw template path
    #         if template:
    #             painter.setPen(QPen(QColor(255, 255, 0), 2))
    #             painter.setBrush(Qt.NoBrush)
                
    #             template_polygon = points_to_qpolygonF(template)
    #             if len(template_polygon) > 1:
    #                 painter.drawPolyline(template_polygon)
    #                 # Draw start point
    #                 painter.setBrush(QColor(255, 255, 0))
    #                 painter.drawEllipse(template_polygon[0], 3, 3)
            
    #         # Draw label
    #         painter.setPen(QColor(255, 255, 255))
    #         painter.setFont(QFont("Arial", 8))
    #         label_rect = QRect(x, y + size + 2, size, 15)
    #         painter.drawText(label_rect, Qt.AlignCenter, label)

    # ##############################
    # def hide_novice_gesture(self):
    #     """Hide the gesture help overlay"""
    #     self.show_help = False
    #     self.help_templates = []
    #     self.repaint()


    ##############################
    def recognize_gesture(self):
        points = qpolygonF_to_points(self.path)
        template_id, label, score = self.oneDollar.recognize(points)
        print("template id: ", template_id, " label: ", label, " score: ", score)

        if score > 0.5:
            self.selected_template.emit(label, template_id, score)
            self.display_feedback(template_id)


    ##############################
    def clear(self):
        self.path = QPolygonF()
        self.feedback = QPolygonF()
        self.termination = QPolygonF()

    ##############################
    def mousePressEvent(self,e):
        self.clear()
        # self.hide_novice_gesture()  # Hide help when starting new gesture
        self.path.append( e.pos() )
        
        # # Start the help timer for 500ms delay
        # self.novice_timer.start(500)
        
        self.repaint()

    ##############################
    def mouseMoveEvent(self, e):
        # # Stop the help timer if user continues drawing
        # self.help_timer.stop()
        # self.hide_gesture_help()
        
        self.path.append( e.pos() )
        self.repaint()

    ##############################
    def mouseReleaseEvent(self, e):
        # # Stop the help timer when gesture is complete
        # self.novice_timer.stop()
        # self.hide_novice_gesture()
        
        if self.path.size() > 10:
            self.recognize_gesture()
        else:
            print("not enough points")

        self.repaint()

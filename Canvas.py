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


# Distinct colors to cycle through
base_colors = [
    QColor(255, 0, 0),      # red
    QColor(0, 128, 255),    # blue
    QColor(0, 200, 0),      # green
    QColor(255, 165, 0),    # orange
    QColor(148, 0, 211),    # violet
    QColor(255, 105, 180),  # hot pink
    QColor(139, 69, 19),    # brown
    QColor(0, 206, 209),    # teal
    QColor(255, 215, 0),    # gold
    QColor(128, 0, 128),    # purple
]


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
        self.novice_timer = QTimer()
        self.novice_timer.timeout.connect(self.show_gesture_help)
        self.novice_timer.setSingleShot(True)  # Only fire once
        
        self.show_help = False
        self.novice_templates = []  # Will store template polygons for display
        self.novice_labels = []  # Will store labels for display
        self.keep_template = []  # Will store the kept templates

        # Progressive shading state while drawing
        self.current_template_id = None
        self.current_score = 0.0
        self.user_path_length = 0.0



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

        # Display available gestures when help is shown
        if self.show_help:
            self.draw_gesture_help(p)


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


    ##############################
    def show_gesture_help(self):
        """
        Called when help timer expires - prepares templates for display.
        """
        self.show_help = True
        self.prepare_novice_templates()
        self.repaint()

    ##############################
    def prepare_novice_templates(self):
        """
        Translate templates to start at the mouse press point (or center of widget).
        """
        self.novice_templates = []
        scale_factor = 1.85
            
        # Anchor at mouse pressed point if available, else center of widget
        if self.path is not None and len(self.path) > 0:
            anchor = self.path[0]
        else:
            anchor = QPoint(self.width() // 2, self.height() // 2)

        for template in self.oneDollar.resampled_templates:
            if template is None or len(template) < 2:
                continue

            # Scale template around its first point
            cx, cy = template[0]
            scaled = [[cx + (pt[0] - cx) * scale_factor,
                       cy + (pt[1] - cy) * scale_factor] for pt in template]

            # Translate template so its first point matches the anchor (mouse press point)
            t0x, t0y = scaled[0]
            dx = anchor.x() - t0x
            dy = anchor.y() - t0y
            translated = [[pt[0] + dx, pt[1] + dy] for pt in scaled]

            self.novice_templates.append(translated)


    ##############################
    # TODO 12 Draw each template with its label
    ##############################
    def draw_gesture_help(self, painter):
        """Draw the gesture help overlay"""

        for idx, (template, label) in enumerate(zip(self.novice_templates, self.oneDollar.labels)):
            if template is None or len(template) < 2:
                continue

            # Pick a color
            color = QColor(base_colors[idx % len(base_colors)])
            color.setAlpha(64)  # 25% opacity

            # Draw the template polyline
            painter.setPen(QPen(color, 8))
            painter.setBrush(Qt.NoBrush)
            template_polygon = points_to_qpolygonF(template)
            if len(template_polygon) > 1:
                painter.drawPolyline(template_polygon)
                # Draw start point
                painter.setBrush(color)
                painter.drawEllipse(template_polygon[0], 3, 3)

            # Compute bounding box for label placement above the template
            xs = [pt[0] for pt in template]
            ys = [pt[1] for pt in template]
            if not xs or not ys:
                continue
            min_x, max_x = min(xs), max(xs)
            min_y = min(ys)

            # Draw label slightly above the template
            painter.setPen(QPen(color))
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            label_rect = QRectF(min_x, min_y - 18, max(40.0, (max_x - min_x)), 16)
            painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignVCenter, label)


    ##############################
    def update_gesture_progress(self):
        """Update selected template and path progress for progressive shading during drawing."""
        # Compute current path length
        path_points = qpolygonF_to_points(self.path)
        if len(path_points) < 2:
            self.user_path_length = 0.0
            self.current_template_id = None
            return

        # Update measured user path length in pixels
        def plength(pts):
            return sum(((pts[i+1][0] - pts[i][0])**2 + (pts[i+1][1] - pts[i][1])**2) ** 0.5 for i in range(len(pts)-1))

        self.user_path_length = plength(path_points)

        # Recognize to select the best matching template id
        try:
            template_id, _, score = self.oneDollar.recognize(path_points)
            self.current_template_id = template_id
            self.current_score = score
        except Exception:
            # In case recognizer raises during early drawing
            self.current_template_id = None
            self.current_score = 0.0


    ##############################
    def hide_novice_gesture(self):
        """Hide the gesture help overlay"""
        self.show_help = False
        self.novice_templates = []
        self.repaint()


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
        self.hide_novice_gesture()  # Hide help when starting new gesture
        self.path.append( e.pos() )
        
        # Start the help timer for 500ms delay
        self.novice_timer.start(500)
        
        self.repaint()

    ##############################
    def mouseMoveEvent(self, e):
        # Stop the help timer if user continues drawing
        self.novice_timer.stop()

        # Extend the current path, then update shading state
        self.path.append(e.pos())
        self.update_gesture_progress()
        self.repaint()

    ##############################
    def mouseReleaseEvent(self, e):
        # Stop the help timer when gesture is complete
        if self.show_help:
            self.novice_timer.stop()
            self.hide_novice_gesture()
        
        else:
            if self.path.size() > 10:
                self.recognize_gesture()
            else:
                print("not enough points")

        self.repaint()

# HCI-Project: Implementation of the $1 Gesture Recognizer

## Project Objective

The objective of this project is to implement a complete gesture recognition system based on the **$1 Recognizer** algorithm, and then develop a graphical interface allowing:

  - visualization of a gesture gallery (templates),
  - drawing a gesture with the mouse,
  - recognizing this gesture in real-time,
  - and displaying dynamic visual feedback.

This project is built in **Python** using **PySide6** for the graphical interface and **NumPy** for geometric calculations.

-----

## Project Structure

The project consists of the following main files:

  - `MainWindow.py` — application entry point (main class and general interface)
  - `Canvas.py` — user stroke management, feedback display, and interaction with the recognizer
  - `onedollar.py` — implementation of the gesture recognition algorithm ($1 Recognizer)
  - `onedol_ds.pkl` — dataset containing gesture templates (16 classes)
  - `resources/` — icons, potential additional files
  - `README.md` — project documentation

-----

## Installation

### 1\. Install dependencies

```bash
pip install numpy PySide6
```

### 2\. Launch the application

```bash
python MainWindow.py
```

-----

## Implemented Features

### Part 1 – Interface and Template Gallery

  * **Steps 1 to 3:**
      * Loading the application skeleton (`MainWindow.py`)
      * Creation of an icon gallery via `QListWidget`
      * Loading templates from `onedol_ds.pkl`
      * Displaying each template as a thumbnail with icon and label

### Part 2 – Implementation of the $1 Recognizer

  * **Step 4:** Adding templates to the recognition system (`addTemplate()` in `OneDollar`)
  * **Steps 5 to 8:** Complete implementation of normalization steps:
      * Point resampling (`resample()`)
      * Rotation to the horizontal axis (`rotateToZero()`, `rotateBy()`)
      * Scaling and translation to origin (`scaleToSquare()`)
      * Gesture recognition (`recognize()`) with calculation of the minimum distance between the gesture and each template

Result: the system displays the label of the recognized gesture with its similarity score in the console.

### Part 3 – Visual Feedback and User Interaction

  * **Step 9:** Addition of a **PySide6 signal** emitted upon gesture recognition (`selected_template`)
      * Connecting the signal to `set_action_on_gesture()` to automatically highlight the recognized template in the gallery
  * **Step 10:** Displaying **static feedback** of the recognized template near the user's gesture
  * **Step 11:** Adding **dynamic feedback** with animation using a `QTimer`, interpolating between the drawn gesture and the recognized template.

These features provide fluid and intuitive interaction.

-----

## Part 4 – Octopocus (Not Implemented)

  * **Step 12 (in progress / not implemented):**
    The objective of this step is to add an **Octopocus** type interaction, allowing:
      * An **expert mode** (classic fast recognition),
      * A **novice mode** (progressive display of all available gestures after a 500 ms wait).

This improvement has not yet been developed in the current version. However, all available gestures are displayed after 500ms.

-----

## Results

At this stage:

  * The system correctly recognizes gestures among the 16 available classes.
  * The user receives visual feedback (static and dynamic).
  * The interface is fully functional and stable.

-----

## Author

Project created by **Antony Manuel** based on a codebase provided by Professor **Sylvain Malacria**, as part of the **3DTechnology** course.

IMT Nord Europe — **2025–2026**

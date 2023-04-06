# MyPomoApp

MyPomoApp is a simple Pomodoro timer application developed in Python using PyQt5 and Matplotlib libraries.

The Pomodoro technique is a time management method developed by Francesco Cirillo in the late 1980s. The technique uses a timer to break down work into intervals, traditionally 25 minutes in length, separated by short breaks.

## Features

- Set custom Pomodoro and break times
- Option to automatically start the next timer after a break
- View your Pomodoro stats using graphs for the last 7 days, weekly or monthly

## Technologies Used

- Python
- PyQt5
- Matplotlib
- Pandas
- JSON

## Installation

1. Clone the repository using `git clone https://github.com/karimelhou/MyPomoApp.git`
2. Install the required packages using `pip install -r requirements.txt`
3. Run the application using `python main.py`

## Usage

1. Set your desired Pomodoro and break times in the settings menu.
2. Click on the start button to start the timer.
3. Work for the duration of the Pomodoro.
4. When the Pomodoro ends, take a short break.
5. The timer will automatically start the next Pomodoro or break, based on your settings.
6. View your Pomodoro stats using the "View Stats" button in the settings menu.

## Stats

You can view your Pomodoro stats by clicking on the "View Stats" button in the settings menu. The application provides the following graph options:

- Last 7 days: A graph showing your daily Pomodoro count for the last 7 days.
- Weekly: A graph showing your weekly Pomodoro count.
- Monthly: A graph showing your monthly Pomodoro count.

The graphs are plotted using Matplotlib library and displayed in a QDialog. The stats data is loaded from a JSON file located in the repository.

## License

This project is licensed under the CC-BY-4.0 License. See the `LICENSE` file for details.

## Acknowledgements

- The Pomodoro technique: https://francescocirillo.com/pages/pomodoro-technique
- PyQt5 library: https://pypi.org/project/PyQt5/
- Matplotlib library: https://matplotlib.org/


## Results 

These are some example screenshots of the application:

![image](https://user-images.githubusercontent.com/47016104/230431353-237e9f6e-9818-4caf-992b-18d0a0232ce4.png)

![image](https://user-images.githubusercontent.com/47016104/230431476-f40857a1-cc38-4432-baa1-c17fad358139.png)

![image](https://user-images.githubusercontent.com/47016104/230431655-38be5966-406e-4b59-82af-bbf5e9c8b731.png)

![image](https://user-images.githubusercontent.com/47016104/230431729-750a4d2c-1330-419e-b06f-e03f884920fc.png)


# django-web-timecard

![Logo](static/worktime/logo.svg)

Web based simple Time Card system written by django. Currently this application only supports Japanese and Japan holidays.

## Features
User can clock in and clock out from a smartphone or PC. Manager check users time records.

## Usage

### Time recording
- Click button for "attendance at work" or "leaving work".
- When you see a message or hear a sound effect, it indicates that time recording has been completed successfully.
- If you click in multiple times on the same day, the work time is first click to last click.

### Monthly time records
- You can check monthly records and working hours.
- Manager can check all user's records.

### Change Password
- Users can change own password.

## Demo
- Access to [https://cottonspace.pythonanywhere.com/worktime/login/](https://cottonspace.pythonanywhere.com/worktime/login/).
- Location information feature is turned off for demonstration purposes.
- Those users can use the demo:
- Demo user passwords are initialized to the default once a day.

| id  | password | role |
| ------------- | ------------- | ------------- |
| demo1  | demodemo1  | employee |
| demo2  | demodemo2  | employee |
| manage  | manemane1  | manager |

## Installation

### Download and edit settings
- Clone or download the application source code.
- Copy local_settings_template.txt located in the django-web-timecard/timecard directory to the same directory as local_settings.py.
- Edit the part from % to % of the local_settings.py according to your environment.
- If you do not know the database settings or want to test this application, please set DATABASES as follows.
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(__file__).resolve().parent.parent / 'db.sqlite3',
    }
}
```

### Initialize
- Run the following command in the django-web-timecard directory to prepare the database.
```
pip install -r requirements.txt
python3 manage.py migrate
```
- Create a superuser with the following command.
```
python3 manage.py createsuperuser
```
- Initialize the working hours for each day of the week with the following command. This will create default settings, so you can edit them later to create appropriate working hours rules.
```
python3 manage.py loaddata worktime/fixtures/standardworkpattern.json
```
- Start the server. For example, to start with Django's functions, run the following command.
```
python3 manage.py runserver
```

### Initial setting
- Log in as superuser in a web browser to access the administration screen.
- First, set the working time pattern for each day of the week on the "Work Pattern" screen. Be sure to perform this setting first before starting application operation.
- Use the following command to initialize the working hours for each day of the week and create a business day calendar.
```
python3 manage.py create_calendar
```
- Register the user who will be stamping the time by adding users as appropriate from the management screen.

### Adding commands to monthly tasks
- Register the following command to be executed once a month in a regular task such as crontab.
```
python3 manage.py create_calendar
```

### Disabling a user
- If you want to disable a user due to retirement, etc., we recommend unchecking the user's "enabled" checkbox on the administrator screen. If you delete it, you will no longer be able to view that user's past attendance history.
- Users whose "Enabled" checkbox is unchecked will be displayed with a "*" symbol after their "Name" when displayed in a list.

## License
[MIT](https://choosealicense.com/licenses/mit/)
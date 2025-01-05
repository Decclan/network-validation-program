
# Iperf3 Network Bandwidth Test

Python app with tkinter GUI offering different settings to conduct network performance testing using Iperf3 on Windows environments.


## Features

- Loops throught different packet lengths and bandwidth sizes
- Live log output from process within GUI
- Logs output and configures for .txt export
- Parsing logic to filter log data for CSV export


## Running Tests



Download pre compiled iperf3 for windows, V-3.17.1 was used for this project. Available at https://files.budman.pw/

Create a directory with both the iperf3 download contents and this application on the server and client machines.

To run tests, cmd as admin, cd to directory with iperf3.exe and this app.

```cmd
  cd C:\Users\directory-with-iperf.exe
```

```cmd
  python Bandwith_Test_V_2.3.py
```

![App Screenshot](https://github.com/Decclan/stock-take-docx-generator/blob/main/bandwidth-test-app-preview.png)

Change the settings to match role of machine, test type and duration.

Start the server side app first, then start the client side.

Once the test is complete, you can export the log output and/or the csv file which only collects relevant test result data.

![Log Screenshot](https://github.com/Decclan/stock-take-docx-generator/blob/main/example-log-export.png)

![CSV Screenshot](https://github.com/Decclan/stock-take-docx-generator/blob/main/example-csv-export.png)


Iperf3 docs: https://software.es.net/iperf/invoking.html#iperf3-manual-page
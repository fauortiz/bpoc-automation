# source of data
- reports.numbers on Desktop

# reminders
- schema
  - | date | task | percentage completion | weight |
  - weights calculate the percentage of the day you spent on a task.
- keep the reports.numbers inputs sorted chronologically, for a better monthly report
- do something like below on your rc file:
```
export PATH="$PATH:/Users/hipejapaninc./Documents/report-maker"
# chmod +x /Users/hipejapaninc./Documents/report-maker/daily.sh
# chmod +x /Users/hipejapaninc./Documents/report-maker/weekly.sh
# chmod +x /Users/hipejapaninc./Documents/report-maker/monthly.sh
export PATH="$HOME/bin:$PATH"
# sudo ln -s /Users/hipejapaninc./Documents/report-maker/daily.sh /usr/local/bin/daily
# sudo ln -s /Users/hipejapaninc./Documents/report-maker/weekly.sh /usr/local/bin/weekly
# sudo ln -s /Users/hipejapaninc./Documents/report-maker/monthly.sh /usr/local/bin/monthly
```

# daily report
- only works if you run it on the day itself
- input: tomorrow's task

# weekly report
- only works if you run it on the week itself, and only on the last day


# monthly report
- input: int representing the month (12 for december)


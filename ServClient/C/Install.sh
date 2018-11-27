#! /bin/sh
gcc main.c -o Notifier
sudo cp Notifier.d /etc/init.d/Notifier
sudo cp Notifier /bin/Notifier
sudo chmod 755 /etc/init.d/Notifier
sudo update-rc.d Notifier defaults
sudo /bin/Notifier

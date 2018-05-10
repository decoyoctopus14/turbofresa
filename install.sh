#!/bin/sh

if [ "$(id -u)" != "0" ] ; then
    echo "Please, run as root!"
    exit 1
fi

echo "==> Cloning the repository"
git clone https://github.com/WEEE-Open/turbofresa
echo "==> Installing the new version"
cd turbofresa
mv turbofresa /usr/bin
cd ..
rm -fr turbofresa

if [ ! -d /home/$USER/.local/share/turbofresa ]; then
   mkdir -p /home/$USER/.local/share/turbofresa
fi

echo "Done!"
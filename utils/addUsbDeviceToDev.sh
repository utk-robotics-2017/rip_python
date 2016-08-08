#!/bin/bash

#Set Script Name variable
SCRIPT=`basename ${BASH_SOURCE[0]}`

#Initialize variables to default values.
devNum="DeviceNum"
devNumListed=false
devName="DeviceName"
devNameListed=false
listDevs=false

#Set fonts for Help.
NORM=`tput sgr0`
BOLD=`tput bold`
REV=`tput smso`

#Help function
function HELP {
  echo -e \\n"Help documentation for ${BOLD}${SCRIPT}.${NORM}"\\n
  echo "Command line switches are optional. The following switches are recognized."
  echo "${REV}-d${NORM}  --Usb device. ${BOLD}[[bus]:][devnum]${NORM}. ex: ${BOLD}001:005${NORM}"
  echo "${REV}-n${NORM}  --Device name ${BOLD}name${NORM}. ex: ${BOLD}loadmega${NORM}"
  echo "${REV}-l${NORM}  --List usb devices."
  echo -e "${REV}-h${NORM}  --Displays this help message."\\n
  echo -e "Example: ${BOLD}$SCRIPT -d 001:005 -n loadmega${NORM}"\\n
  exit 1
}

#Check the number of arguments. If none are passed, print help and exit.
NUMARGS=$#
if [[ $NUMARGS -eq 0 ]]; then
  HELP
fi

### Start getopts code ###

#Parse command line flags
#If an option should be followed by an argument, it should be followed by a ":".
#Notice there is no ":" after "h". The leading ":" suppresses error messages from
#getopts. This is required to get my unrecognized option code to work.

while getopts ":d:n:lh" FLAG; do
  case $FLAG in
    d)  #set device number
      devNum=$OPTARG
      devNumListed=true
      ;;
    n)  #set device name
      devName=$OPTARG
      devNameListed=true
      ;;
    l)  #list usb devices
      listDevs=true
      ;;
    h)  #show help
      HELP
      ;;
    \?) #unrecognized option - show help
      echo -e \\n"Option -${BOLD}$OPTARG${NORM} not allowed."
      HELP
      ;;
    :)  #Required option
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

shift $((OPTIND-1))  #This tells getopts to move on to the next argument.

### End getopts code ###

if ( $listDevs && ( $devNameListed || $devNumListed )); then
    echo "You cannot list devices and add an arduino at the same time." >&2
    exit 1
elif ( $listDevs ); then
    lsusb
    exit 0
fi

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root." >&2
    exit 1
fi

devInfo=`lsusb -v -s $devNum`

devVendor=`echo "$devInfo" | grep -oP "idVendor.*0x\K\d+"`
devProduct=`echo "$devInfo" | grep -oP "idProduct.*0x\K\d+"`
devSerial=`echo "$devInfo" | grep -oP "iSerial.*\d+ \K\d+"`

udevRule=`printf 'SUBSYSTEM=="tty", ATTRS{idVendor}=="%s", ATTRS{idProduct}=="%s", ATTRS{serial}=="%s", SYMLINK+="%s"\n' "$devVendor" "$devProduct" "$devSerial" "$devName"`

echo $udevRule >> /etc/udev/rules.d/100-$devName-usb-serial.rules
udevadm trigger

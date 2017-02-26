do NOT use GPIO.BCM

do use GPIO.BOARD

edits to settings.cfg:
    
    * SWITCH_PIN = 12
    * LED_PIN = 23

comment out lines: `28, 263`

notes:

    [pull down resistor circuit]: https://www.raspberrypi.org/learning/physical-computing-guide/pull_up_down/
    
    [raspi 3 header pinout]: http://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900.png

AMR-Motor-Control-Power-Distribution

The AMR-Motor-Control-Power-Distribution board is a custom-designed PCB that serves as the central power distribution and low-level control unit of the autonomous mobile robot. Its primary role is to distribute power from the 24V battery to the robot’s major subsystems, including the base motors, robotic arm, onboard computer, and supporting electronics.

To support components with different voltage requirements, the board includes buck converters that efficiently step down the input voltage to the required levels. This enables stable and regulated power delivery to each subsystem while maintaining overall efficiency.

The board also integrates two electrically isolated STM32F411 microcontrollers. These microcontrollers are responsible for motor control and for transmitting encoder and IMU data to the Jetson compute module. Electrical isolation between the control and power sections helps reduce noise, improve reliability, and protect sensitive electronics from faults in high-current subsystems.

The design places strong emphasis on protection and reliability. The electrical architecture uses galvanic isolation, isolated DC–DC converters, polyfuses, and TVS diodes to protect against overcurrent, voltage spikes, and electrical noise. An emergency kill switch with fuse protection is also included in the main power path to allow safe and immediate shutdown when required.

This modular design improves serviceability and fault isolation by separating power electronics, sensing, and computing into distinct electrical domains. As a result, the AMR-Motor-Control-Power-Distribution board plays a key role in ensuring stable operation, easier debugging, and reliable long-term performance of the robot in demanding autonomous applications.

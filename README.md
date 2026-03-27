# AMR-Motor-Control-Power-Distribution
<img width="992" height="912" alt="image" src="https://github.com/user-attachments/assets/c16a23ef-ea93-4b7a-9286-895b1ff2b397" />



Certainly — here it is in a clear pointer-based format:

## AMR-Motor-Control-Power-Distribution

* A custom-designed PCB that acts as the **central power distribution** and **low-level control unit** of the autonomous mobile robot. 
* Distributes power from the **24V battery** to the robot’s major subsystems, including:

  * **Base motors**
  * **Robotic arm**
  * **Onboard Jetson compute module**
  * **Supporting electronics and sensors** 

## Power Regulation

* Includes **buck converters** to step down the input voltage to the required levels for different subsystems. 
* Provides **stable and regulated power delivery** to components with different voltage requirements.
* Improves overall system efficiency through localized voltage regulation.

## Control Architecture

* Integrates **two electrically isolated STM32F411 microcontrollers**. 
* The microcontrollers are responsible for:

  * **Motor control**
  * **Encoder data handling**
  * **IMU data handling**
  * **Communication with the Jetson compute module** 
* Electrical isolation between control and power sections helps:

  * Reduce electrical noise
  * Improve system reliability
  * Protect sensitive electronics from faults in high-current sections

## Protection and Reliability Features

* Designed with a strong focus on **electrical protection** and **robust operation**. 
* Protection features include:

  * **Galvanic isolation**
  * **Isolated DC-DC converters**
  * **Polyfuses**
  * **TVS diodes** 
* These features help protect the system against:

  * Overcurrent conditions
  * Voltage spikes
  * Electrical noise and transients
* Includes an **emergency kill switch** with **fuse protection** in the main power path for safe and immediate shutdown. 

## System Design Advantages

* Separates **power electronics**, **sensing**, and **computing** into distinct electrical domains. 
* Improves:

  * **Serviceability**
  * **Fault isolation**
  * **Debugging efficiency**
  * **Long-term system reliability**
* Plays a key role in ensuring stable operation of the robot in demanding autonomous applications.

I can also merge this with your **dual-STM isolation scheme** section so the whole README reads in one consistent pointer-based style.


## The Two Brains 

<img width="1295" height="415" alt="image" src="https://github.com/user-attachments/assets/a078d64a-a272-426f-a399-04390958be0e" />

Got it. For a schematic description, pointer-style is better.

You can write it like this:

## Isolation and Communication Architecture

* The board uses **two STM32 microcontrollers** arranged in **separate electrical domains**. 
* The two controllers communicate through **optocouplers**, providing electrical isolation between the domains.
* Communication across the isolation barrier consists of:

  * **1 clock synchronization line**
  * **2 UART lines**
* This arrangement allows reliable data exchange while reducing the effect of electrical noise and preventing fault propagation between subsystems.

## Powering Scheme

* One STM32 is powered using an **isolated DC-DC converter**.
* The other STM32 is powered directly from the **raw power rail**.
* This split power architecture helps isolate sensitive control and sensing electronics from noisy power sections.

## Functional Division Between the Two STM32s

### STM32-1

* Receives **encoder data**
* Sends encoder feedback to the **Jetson**
* Receives **motor actuation commands** from the Jetson through **USB CDC**
* Acts as the main communication bridge to the Jetson

### STM32-2

* Acquires **IMU data**
* Sends IMU data to **STM32-1**

## Data Flow

* **Jetson → STM32-1**: motor actuation commands via USB CDC
* **STM32-2 → STM32-1**: IMU data
* **STM32-1 → Jetson**: encoder data and forwarded IMU data

## Design Benefits

* Clear separation of sensing and control responsibilities
* Reduced electrical interference between domains
* Improved robustness in noisy motor-control environments
* Easier debugging and modular system integration

Here is an even shorter README-style version:

## Dual-STM Isolation Scheme

* Two STM32 microcontrollers are used in separate electrical domains.
* The domains are isolated using optocouplers.
* Cross-domain communication uses **one clock synchronization line** and **two UART lines**.
* One STM32, powered through an isolated DC-DC converter, handles encoder acquisition and Jetson communication over USB CDC for motor commands.
* The second STM32, powered from the raw supply, handles IMU acquisition and sends this data to the first STM32.
* The first STM32 forwards the combined feedback data to the Jetson.




<img width="1249" height="368" alt="image" src="https://github.com/user-attachments/assets/9d6caf21-4981-42ef-bffb-2def22e31e06" />


## Switch Layout

* The schematic includes three primary power switches: **Main Kill**, **Arm Kill**, and **Base Kill**.
* The **Main Kill Switch** controls overall system power.
* The **Arm Kill Switch** only disables the arm power domain.
* The **Base Kill Switch** only disables the base power domain.
* The **Jetson remains powered even when the Arm Kill Switch is turned off**, allowing computation and system monitoring to continue independently of the arm power domain.

<img width="999" height="411" alt="image" src="https://github.com/user-attachments/assets/7b50407a-b543-4a1b-a3ae-fa15494c2980" />

## Fuse Layout and Protection

* The schematic includes **three main fuses on the PCB**:

  * one for the **IMU**
  * one for **each STM32 microcontroller**
* These fuses protect the low-power sensing and control sections of the board.
* In addition, **one fuse may also be added along with each kill switch**, depending on the required level of subsystem protection.
* This design provides better electrical safety and allows faults to be isolated more effectively across different power domains.



<img width="690" height="654" alt="image" src="https://github.com/user-attachments/assets/538db351-fd02-4af9-be60-af99e491612d" />
<img width="1029" height="880" alt="image" src="https://github.com/user-attachments/assets/536407ca-75a2-426f-98d8-6d0f3419dc13" />


You can write it like this:

## High-Current Power Routing

* The high-current section of the PCB is laid out as a **separate and clearly defined power zone**.
* This section is designed with **wider copper paths** to support higher current flow with lower resistance.
* Special attention has been given to the **battery input terminal** to improve current-carrying capability.
* In this region, the **solder mask has been removed intentionally** so that additional solder can be added over the copper.
* Adding extra solder increases the effective conductive cross-section and helps the board handle higher current more reliably.
* This layout improves:

  * **current-carrying capacity**
  * **thermal performance**
  * **power delivery reliability** under heavy load


<img width="878" height="349" alt="image" src="https://github.com/user-attachments/assets/30623c91-e67c-4b61-bfee-9fad8ec4ab52" />


## Acknowledgment and Conclusion

* This project represents the combined effort of the entire electronics team and all the members who contributed to making this AMR possible.
* The development of the AMR-Motor-Control-Power-Distribution board was made possible through continuous design, testing, debugging, and integration across multiple subsystems.
* Special acknowledgment goes to all the members of the electronics system whose work on power distribution, control, sensing, protection, and system integration contributed to the successful realization of this project.
* This board serves as a key part of the robot’s electrical architecture, enabling reliable power delivery, subsystem isolation, and robust low-level control.
* With this work, the project establishes a strong foundation for stable and scalable operation of the autonomous mobile robot.






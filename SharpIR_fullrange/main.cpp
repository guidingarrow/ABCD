#include "mbed.h"
#include "SHARPIR.h"

SHARPIR Sensor(p19);
SHARPIR Sensor2(p20);
DigitalOut danger(p21);

//________Used for Debugging/ testing________//  
Serial pc(USBTX, USBRX); // tx, rx
//DigitalOut led1(LED1);
//DigitalOut led2(LED2);
//DigitalOut led3(LED3);
//DigitalOut led4(LED4);
//___________________________________________// 

int main() {
//________Used for Debugging/ testing________//    
//    led1 = 0;
//    led2 = 0;
//    led3 = 0;
//    led4 = 0;
//___________________________________________// 
    float IR;  //Stores the voltage value of one IR sensor
    float IR2; // Stores the voltage value of the other IR sensor
    int danger1 = 0;
    int danger2 = 0;

    while(1){
        IR = Sensor.volt();
        IR2 = Sensor2.volt();
        
        // Check if IR sensor sees something between 100cm and 550cm
        if ((IR <= 2.52) && (IR >= 1.269)){
            danger1 = 1;
        }
        else {
            danger1 = 0;    
        }
        
        // Check if IR2 sensor sees something between 100cm and 550cm
        if ((IR2 <= 2.52) && (IR2 >= 1.269)){
            danger2 = 1;
        }
        else {
            danger2 = 0;    
        }

        
        danger = (danger1 || danger2); //Set danger output to 1 if both sensors see danger.
        
//________Used for Debugging/ testing________//           
//        printf("Volt1: %f\n\rVolt2: %f\n\r", IR, IR2);
//        wait(1);
//      if( a <= 2.52 && a > 1.8) {
//           led1 = 1;
//        }
//        else if ( a <= 1.8 && a > 1.36 ) {
//            led1 = 1;
//            led2 = 1;
//        }
//        else if ( a <= 1.36 && a > 1.3 ) {
//            led1 = 1;
//            led2 = 1;
//            led3 = 1;
//        }
//        else if ( a <= 1.3 && a > 1.269 ) {
//            led1 = 1;
//            led2 = 1;
//            led3 = 1;
//            led4 = 1;
//        }
//        else {
//            led1 = 0;
//            led2 = 0;
//            led3 = 0;
//            led4 = 0;
//        }
//      
//       
//      wait_ms(200);
//___________________________________________//         
    }
}

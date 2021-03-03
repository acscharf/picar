import picar_4wd as fc
import time

speed = 10

def main():
    while True:
        scan_list = fc.scan_step(35)


        if not scan_list:
            continue
        
        tmp = scan_list[3:7]
        print(tmp)
        if tmp != [2,2,2,2]:
            fc.stop()
            time.sleep(.5)
            fc.backward(15)
            time.sleep(.5)
            fc.stop()
            time.sleep(.5)
            fc.turn_right(speed)

        else:
            fc.forward(speed)

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()

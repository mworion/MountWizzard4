from mountcontrol.mount import Mount

print("Importing Python Packages - please wait.")

import itertools
import threading
import time
import sys


#here is the animation
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rThinking ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    # sys.stdout.write('\nDone!     \n')
    # print('\nDone!     \n')

done = False
t = threading.Thread(target=animate, daemon=True)
t.start()

time.sleep(2)


def main():
    return
    m = Mount(host=('192.168.2.15', 3492),
              MAC='00.c0.08.87.35.db',
              pathToData='.',
              expire=False,
              verbose=False,
              )

    m.firmware.poll()
    print(m.firmware.product)
    print(m.firmware.number())

    suc = m.obsSite.setTargetAltAz(alt_degrees=50, az_degrees=50)
    print(suc)
    suc = m.obsSite.pollPointing()
    print(suc)
    print(m.obsSite.angularPosRA.degrees, m.obsSite.angularPosDEC.degrees)
    print(m.obsSite.raJNow._degrees, m.obsSite.decJNow.degrees)

    print(m.obsSite.angularPosRA.degrees + m.obsSite.raJNow._degrees)
    print(m.obsSite.angularPosDEC.degrees + m.obsSite.decJNow.degrees)


if __name__ == "__main__":
    main()

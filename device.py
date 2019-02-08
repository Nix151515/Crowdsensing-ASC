"""
State Nicolae - Tema1 ASC
"""
from threading import Thread, Event, Lock, Condition
import Queue


class ReusableBarrier(object):
    """
    Barrier with condition, taken from the lab
    """

    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count_threads = self.num_threads
        self.cond = Condition()

    def wait(self):
        """
        Wait until all the devices reach the barrier
        """
        self.cond.acquire()
        self.count_threads -= 1
        if self.count_threads == 0:
            self.cond.notify_all()
            self.count_threads = self.num_threads
        else:
            self.cond.wait()
        self.cond.release()

    def show(self):
        """
        Print details about the properties
        """
        print "Total : " +self.num_threads
        print "Remaining : "+self.count_threads


class Device(object):
    """
    Class that represents a device.
    """

    def __init__(self, device_id, sensor_data, supervisor):
        """
        Constructor.

        @type device_id: Integer
        @param device_id: the unique id of this node; between 0 and N-1

        @type sensor_data: List of (Integer, Float)
        @param sensor_data: a list containing (location, data) as measured by this device

        @type supervisor: Supervisor
        @param supervisor: the testing infrastructure's control and validation component
        """

        #Shared properties (barrier, lock array)
        self.barrier = None
        self.location_locks = None

        #Threads running the scripts and the scripts queue
        self.workers = []
        self.nr_workers = 8
        self.queue = Queue.Queue()

        #Found neighbours
        self.neighbours = None

        self.device_id = device_id
        self.sensor_data = sensor_data
        self.supervisor = supervisor
        self.scripts = []
        self.timepoint_done = Event()
        self.thread = DeviceThread(self)

    def __str__(self):
        """
        Pretty prints this device.

        @rtype: String
        @return: a string containing the id of this device
        """
        return "Device %d" % self.device_id

    def setup_devices(self, devices):
        """
        Setup the devices before simulation begins.
        @type devices: List of Device
        @param devices: list containing all devices
        """

        #We actually need the stinkin' setup:
        #Init and start the workers
        self.thread.start()
        for i in range(self.nr_workers):
            self.workers.append(ScriptWorker(self))
            self.workers[i].start()

        #Initialize the shared barrier and the locks
        if self.device_id == 0:
            self.barrier = ReusableBarrier(len(devices))
            self.location_locks = []
            for i in devices:
                i.barrier = self.barrier
                i.location_locks = self.location_locks

    def assign_script(self, script, location):
        """
        Provide a script for the device to execute.

        @type script: Script
        @param script: the script to execute from now on at each timepoint; None if the
            current timepoint has ended

        @type location: Integer
        @param location: the location for which the script is interested in
        """
        if script is not None:
            self.scripts.append((script, location))
        else:
            self.timepoint_done.set()

    def get_data(self, location):
        """
        Returns the pollution value this device has for the given location.

        @type location: Integer
        @param location: a location for which obtain the data

        @rtype: Float
        @return: the pollution value
        """
        return self.sensor_data[location] if location in self.sensor_data else None

    def set_data(self, location, data):
        """
        Sets the pollution value stored by this device for the given location.

        @type location: Integer
        @param location: a location for which to set the data

        @type data: Float
        @param data: the pollution value
        """
        if location in self.sensor_data:
            self.sensor_data[location] = data

    def shutdown(self):
        """
        Instructs the device to shutdown (terminate all threads). This method
        is invoked by the tester. This method must block until all the threads
        started by this device terminate.
        """
        self.thread.join()


class ScriptWorker(Thread):
    """
    Class that implements a worker
    """
    def __init__(self, device):
        Thread.__init__(self)
        self.device = device
        self.stopped = Event()

    def add_location(self, location):
        """
        Add a location to the array and init its lock
        """
        found = None
        for (zone, lock) in self.device.location_locks:
            if zone == location and lock is not None:
                found = True
                break
        if found is None:
            self.device.location_locks.append((location, Lock()))

    def set_lock(self, location):
        """
        Set the lock for a location
        """
        for (zone, lock) in self.device.location_locks:
            if zone == location:
                lock.acquire()

    def release_lock(self, location):
        """
        Release the lock for a location
        """
        for (zone, lock) in self.device.location_locks:
            if zone == location:
                lock.release()

    def run(self):
        while True:

            #No more neighbours, receive stop event
            if self.stopped.isSet():
                break

            #Get script if available, else loop
            try:
                (script, location) = self.device.queue.get(False)
            except Queue.Empty:
                continue

            #Add the location to array and set its lock
            self.add_location(location)
            self.set_lock(location)
            neighbours = self.device.neighbours

            #Main code ('for' deleted, scripts taken from the queue)
            script_data = []
            for device in neighbours:
                data = device.get_data(location)
                if data is not None:
                    script_data.append(data)
            data = self.device.get_data(location)
            if data is not None:
                script_data.append(data)
            if script_data != []:
                result = script.run(script_data)
                for device in neighbours:
                    device.set_data(location, result)
                self.device.set_data(location, result)

            #Task taken from queue finished
            self.device.queue.task_done()

            #Release the location lock
            self.release_lock(location)


class DeviceThread(Thread):
    """
    Main device thread
    """
    def __init__(self, device):
        Thread.__init__(self, name="Device Thread %d" % device.device_id)
        self.device = device

    def run(self):
        while True:
            neighbours = self.device.supervisor.get_neighbours()
            worker = None
            if neighbours is not None:
                self.device.neighbours = neighbours
            else:
                #No neighbours, notify workers to stop
                for worker in self.device.workers:
                    worker.stopped.set()
                    worker.join()
                worker.stopped.clear()
                break

            #All the scripts are sent
            self.device.timepoint_done.wait()

            #Put scripts in queue and wait to be processed
            for script in self.device.scripts:
                self.device.queue.put(script)
            self.device.queue.join()

            #Timepoint done and waiting everyone to reach it
            self.device.barrier.wait()
            self.device.timepoint_done.clear()

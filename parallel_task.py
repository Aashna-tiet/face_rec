from multiprocessing import Process, JoinableQueue, Value, Lock
import time
import logging
from abc import ABC, abstractmethod
import face_recognition
import numpy as np
import pymysql
from imageDb import saveData


class Runnable(ABC):
    """Abstract base class for tasks that can be submitted for
    execution to the {Parrun} executor.

    Arguments:
        ABC {[type]} -- [description]
    """

    @abstractmethod
    def run(self):
        pass


class Parrun(object):
    """
    Implements a simple task executor backed by a JoinableQueue
    queue which can have a bounded capacity. This is somewhat similar
    to the java.util.concurrent.Executor.
    """

    def __init__(self, queue_size=100, worker_count=4, status_callback=None):
        """Constructor for the class.

        Keyword Arguments:
            queue_size {int} -- Size of the task queue  (default: {100})
            worker_count {int} -- No. of worker processes to create (default: {4})
            status_callback -- Callback function for updating status back to caller
        """
        self.q = JoinableQueue(queue_size)
        self.worker_count = worker_count
        self.status_callback = status_callback
        self.closing = False
        self.items_done = Value("i", 0)
        self.lock = Lock()

    def submit_item(self, item: Runnable):
        """Adds a Runnable instance to the task queue. This method
        blocks if the queue is full.

        Arguments:
            item {Runnable} -- Task object to run.

        Raises:
            ValueError: If the supplied item is not an instance of
            Runnable class, an exception is raised.
        """
        if not isinstance(item, Runnable):
            raise ValueError("Only instances of Runnable can be submitted.")
        if not self.closing:
            self.q.put(item)
        else:
            logging.debug("Runner closing. Rejecting the item.")

    def run_task(self):
        """Each of the worker processes will execute this method.
        Until the executor is shutdown, this method keeps looping
        to get the items off the task queue. The worker processes
        block when the queue is empty. The method returns either
        when the item in the queue is None, or when the executor is
        shut down.
        """
        while not self.closing:
            try:
                runnable = self.q.get()
                if runnable == None:
                    break
                done_count = runnable.run()
                with self.lock:
                    if done_count:
                        self.items_done.value = self.items_done.value + done_count

                if self.status_callback is not None:
                    self.status_callback(self.items_done.value)
            except Exception as ex:
                logging.exception("Error when handling task.")

    def start_workers(self):
        """Starts the worker processes.
        """
        for w in range(0, self.worker_count):
            p = Process(target=self.run_task)
            p.start()
        logging.debug("Started {} consumers.".format(self.worker_count))

    def shutdown(self):
        logging.info("Shutting down workers.")
        for w in range(0, self.worker_count):
            self.q.put(None)
        self.q.close()
        self.closing = True


dbc = None


def insert_data(name, image_path, face_enc, ref_dist):
    try:
        print(">>>>> Connected to DB.")
        add_entry = ("INSERT INTO face_encodings"
                     "(person_name,image_path, face_enc, ref_dist)"
                     "VALUES (%(person_name)s, %(image_path)s, %(face_enc)s, %(ref_dist)s)")

        data_val = {
            'person_name': name,
            'image_path': image_path,
            'face_enc': face_enc,
            'ref_dist': ref_dist,
        }
        cr = dbc.cursor()
        cr.execute(add_entry, data_val)
        dbc.commit()
        cr.close()
        print("Saved the data in DB")

    except Exception as ex:
        print("Error occurred when saving to DB {}".format(ex))


class MyRunnable(Runnable):
    """
    Simple example for testing/demo.
    """

    def __init__(self, image_path):
        print("Processing image: {}".format(image_path))
        self.image_path = image_path

    def run(self):
        try:
            # 1. Read the image
            print("Processing {0}".format(self.image_path))
            # 2. Get face vector
            image_data = face_recognition.load_image_file(self.image_path)
            image_encoding = face_recognition.face_encodings(
                image_data, known_face_locations=None, num_jitters=10, model="large")[0]
            # 3. Save the vector and other details in DB table
            import os
            name = os.path.basename(self.image_path)
            print(name)
            distance = np.linalg.norm(image_encoding)
            face_enc = ' '.join([str(elem) for elem in image_encoding])
            # call the function from imageDb and pass values
            insert_data(name, self.image_path, face_enc, distance)
        except Exception as ex:
            print("Error in thread function: {}".format(ex))


def main():
    db_args = {
        'user': 'user1',
        'password': 'passw0rd.',
        'host': '127.0.0.1',
        'database': 'frec_db'
    }
    dbc = pymysql.connect(**db_args)

    pr = Parrun()
    pr.start_workers()
    import glob

    for file_path in glob.glob("/home/userone/Downloads/lfw/**/*"):
        pr.submit_item(MyRunnable(file_path, db_args))
    pr.shutdown()


if __name__ == "__main__":
    main()

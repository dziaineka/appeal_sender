import multiprocessing
from preparer import start
import config


if __name__ == '__main__':
    jobs = []

    for email in config.EMAILS:
        p = multiprocessing.Process(target=start,
                                    args=(email,))
        jobs.append(p)
        p.start()

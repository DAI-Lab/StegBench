from stegbench.utils import lookup
from stegbench import stegbench as steg
import stegbench.algo.algo_info as algo
import os
import shutil
import json
import datetime


def init_working_dir(clear_cache):
    if os.path.exists(lookup.stegbench_tld):
        if clear_cache:
            shutil.rmtree(lookup.stegbench_tld)
        else:
            return
    steg.initialize()
    steg.add_config(directory=["examples/configs/detector_csfc",
                               "examples/configs/detector_prob",
                               "examples/configs/embeddor"])


class EmbeddorWrapper(object):
    def __init__(self, embeddor_name, clear_cache=True):
        init_working_dir(clear_cache)
        embeddor_info = algo.get_all_algorithms(lookup.embeddor)
        self._embeddor_name = embeddor_name

        self._embeddor = None
        for embeddor in embeddor_info:
            if embeddor["name"] == embeddor_name:
                self._embeddor = embeddor
                break

        if self._embeddor is None:
            raise RuntimeError("embeddor not found.")
        self._embeddor_set_uuid = steg.add_embeddor([self._embeddor["uuid"]])


    def embed(self, cover_path, steg_path, ratio, overwrite=False):
        if os.path.exists(steg_path):
            if overwrite:
                shutil.rmtree(steg_path)
            else:
                raise RuntimeError("steg path exists")

        cover_db_name = datetime.datetime.now().strftime("cover-%Y%m%d-%H%M%S")
        steg_db_name = datetime.datetime.now().strftime(
            "steg-{embeddor}-%Y%m%d-%H%M%S".format(embeddor=self._embeddor_name))

        cover_db_uuid = steg.process(cover_path, cover_db_name)
        steg_db_uuid = steg.embed(self._embeddor_set_uuid, cover_db_uuid, ratio, steg_db_name)

        for db in lookup.get_all_dbs():
            if db["uuid"] == steg_db_uuid:
                meta = db.copy()

        shutil.copytree(meta["path"], steg_path)

        with open(steg_path + "/meta.json", "w") as f:
            json.dump(meta, f)

        shutil.copy(os.path.join(lookup.stegbench_tld, lookup.db, lookup.metadata,
                                 steg_db_uuid, lookup.db_file), steg_path)

        return steg.verify(steg_db_uuid)


class DetectorWrapper(object):
    def __init__(self, detector_name, clear_cache=True):
        init_working_dir(clear_cache)
        detector_info = algo.get_all_algorithms(lookup.detector)
        self._detector_name = detector_name

        self._detector = None
        for detector in detector_info:
            if detector["name"] == detector_name:
                self._detector = detector

        print(self._detector)
        if self._detector is None:
            raise RuntimeError("detector not found.")
        self._detector_set_uuid = steg.add_detector([self._detector["uuid"]])

    def detect(self, cover_path=None, steg_path=None):
        cover_db_name = datetime.datetime.now().strftime("cover-%Y%m%d-%H%M%S")
        steg_db_name = datetime.datetime.now().strftime("steg--%Y%m%d-%H%M%S")

        cover_acc = None
        steg_acc = None
        if cover_path is not None:
            cover_db_uuid = steg.process(cover_path, cover_db_name)
            result = steg.detect(self._detector_set_uuid, [cover_db_uuid])
            assert len(result) == 1
            print(result)
            cover_acc = result[self._detector["uuid"]][lookup.result_metric][lookup.accuracy]

        if steg_path is not None:
            steg_db_uuid = steg.process(steg_path, steg_db_name)
            result = steg.detect(self._detector_set_uuid, [steg_db_uuid])
            steg_acc = 1 - result[self._detector["uuid"]][lookup.result_metric][lookup.accuracy]
        return cover_acc, steg_acc



if __name__ == "__main__":
    embeddor = EmbeddorWrapper("steganogan-basic")
    accuracy = embeddor.embed("notebooks/example_dataset", "tmp/", ratio=0.0001)
    print(accuracy)
    detector = DetectorWrapper("spa")
    cover_acc, steg_acc = detector.detect("notebooks/example_dataset", "tmp/")
    print(cover_acc)
    print(steg_acc)

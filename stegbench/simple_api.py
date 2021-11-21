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
    def __init__(self, embeddor_name, clear_cache=False):
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
        print(self._embeddor_set_uuid)


    def embed(self, cover_path, steg_path, ratio):
        if os.path.exists(steg_path):
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


if __name__ == "__main__":
    embeddor = EmbeddorWrapper("steganogan-basic", clear_cache=False)
    accuracy = embeddor.embed("notebooks/example_dataset", "tmp/", ratio=0.0001)
    print(accuracy)

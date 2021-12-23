"""Hashtable implementation for large entity embedding files."""

import hashlib
import json
import os
import pickle
import time

import numpy as np


class EmbeddingHashtable:
    """
    Hashtable implementation for large entity embedding files.

    :param hash_table: list of full size hashtable buffers
    :param hash_table_collisions: dict containing longer collision chain
    :param root_path: Path to folder containing the entity embedding file
    :param entity_file: entity embedding gile name, has to be stored in hash_table_config.json
    :param num_entities: number of enities in entity file, has to be store in hash_table_config.json
    :param hash_table_size: number of entries in hashtable buffer in hash_table
    :param hash_table_mask: used to cut down hash to generate index in [0,hash_table_size[
    :param use_hash_bytes: number of bytes used from sha256 hash
    """

    PRINT_EVERY = 100000

    def __init__(self, root_path: str) -> None:
        self.hash_table: list = []
        self.hash_table_collisions: dict = {}
        self.root_path = root_path
        self.entity_file = ""
        self.num_entities = 0
        self.hash_table_size = 0
        self.hash_table_mask = 0
        self.use_hash_bytes = 0

    def load(self) -> None:
        """
        Load hashtable stored at root_path.

        Hashtable itself is stored in compressed .npz format and the collision dict in .pkl format.
        hash_table.npz, hash_table.pkl, hash_table_config.json and entity_file have to be located at root_path.
        """
        self.load_config()
        with open(os.path.join(self.root_path, "hash_table.npz"), "rb") as in_file:
            data = np.load(in_file)
            self.hash_table = [data[tab] for tab in data]
        with open(os.path.join(self.root_path, "hash_table.pkl"), "rb") as in_file:
            self.hash_table_collisions = pickle.load(in_file)

    def load_config(self) -> None:
        """
        Load hash_table_config.json.

        hash_table_config.json contains:
        entity_file: name of the file containing the entity embeddings
        num_entities: the number of entities in entity_file
        """
        with open(
            os.path.join(self.root_path, "hash_table_config.json"),
            "r",
            encoding="UTF-8",
        ) as config_file:
            data = json.load(config_file)
            print(data)
            self.entity_file = data["entity_file"]
            self.num_entities = data["num_entities"]
            log_num_entities = int(np.ceil(np.log2(self.num_entities)))
            self.hash_table_size = 2 ** log_num_entities
            self.hash_table_mask = self.hash_table_size - 1
            self.use_hash_bytes = (log_num_entities - 1) // 8 + 1

    def store(self) -> None:
        """
        Store hashtable to root_path.

        hash_table is stored as compressed .npz file.
        hash_table_collisions is stored as .pkl file.
        """
        with open(os.path.join(self.root_path, "hash_table.npz"), "wb") as out_file:
            np.savez_compressed(out_file, *self.hash_table)
        with open(os.path.join(self.root_path, "hash_table.pkl"), "wb") as out_file:
            pickle.dump(self.hash_table_collisions, out_file)

    def generate(self) -> None:
        """
        Generate hashtable from entity_file stored at root_path.

        Remark: hash_table_config.json has to be created before calling generate
                and has to be located at root_path
        """
        self.load_config()
        t_start = time.time()
        num_collisions = 0
        with open(
            os.path.join(self.root_path, self.entity_file),
            "r",
            newline="",
            encoding="utf-8",
        ) as tsv_file:
            tsv_file.seek(0)
            file_pos = tsv_file.tell()
            line = tsv_file.readline()
            self.hash_table = []
            self.hash_table.append(
                np.zeros(self.hash_table_size, dtype=np.int64)
                - np.ones(self.hash_table_size, dtype=np.int64)
            )
            self.hash_table_collisions = {}
            i = 0
            while line:
                uri = line.split(sep="\t", maxsplit=1)[0]
                uri = uri.split("/", maxsplit=2)[2]
                uri_bytes = uri.encode("UTF-8")
                sha256_instance = hashlib.sha256()
                sha256_instance.update(uri_bytes)
                file_hash = sha256_instance.digest()
                hash_table_idx = (
                    int.from_bytes(file_hash[: self.use_hash_bytes], "little")
                    & self.hash_table_mask
                )
                for tab in self.hash_table:
                    if tab[hash_table_idx] == -1:
                        tab[hash_table_idx] = file_pos
                        break
                else:
                    num_collisions += 1
                    if hash_table_idx in self.hash_table_collisions:
                        self.hash_table_collisions[hash_table_idx].append(file_pos)
                    else:
                        self.hash_table_collisions[hash_table_idx] = [file_pos]

                    if num_collisions > self.hash_table_size // 10:
                        print("Adding new hash_table")
                        num_collisions = 0
                        self.hash_table.append(
                            np.zeros(self.hash_table_size, dtype=np.int64)
                            - np.ones(self.hash_table_size, dtype=np.int64)
                        )
                        remove_hashes = []
                        for entry in self.hash_table_collisions:
                            self.hash_table[-1][entry] = self.hash_table_collisions[
                                entry
                            ].pop(0)
                            if self.hash_table_collisions[entry] == []:
                                remove_hashes.append(entry)
                        for entry in remove_hashes:
                            del self.hash_table_collisions[entry]
                i += 1
                if i % EmbeddingHashtable.PRINT_EVERY == 0:
                    print(f"Hashed {i} elements ({i/self.num_entities*100.0:.1f}%")
                    print(f"Speed: {i/(time.time()-t_start):.1f}")

                file_pos = tsv_file.tell()
                line = tsv_file.readline()
        self.store()

    def lookup(self, uri: str) -> list[int]:
        """
        Gather all seek positions for hash of given uri.

        :param str uri: URI without "http(s)://"
        :return: list of seek positions in entity_file
        """
        uri_bytes = uri.encode("UTF-8")
        sha256_instance = hashlib.sha256()
        sha256_instance.update(uri_bytes)
        file_hash = sha256_instance.digest()
        hash_table_idx = (
            int.from_bytes(file_hash[: self.use_hash_bytes], "little")
            & self.hash_table_mask
        )
        seek_positions = []
        for tab in self.hash_table:
            if tab[hash_table_idx] != -1:
                seek_positions.append(tab[hash_table_idx])
            else:
                break
        else:
            if hash_table_idx in self.hash_table_collisions:
                seek_positions.extend(self.hash_table_collisions[hash_table_idx])
        return seek_positions

"""
A simple inventory plugin that generates a random inventory
"""

import json
import random
import uuid

from typing import Any

# The imports below are the ones required for an Ansible plugin
from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable

DOCUMENTATION = r'''
    name: random_plugin
    plugin_type: inventory
    short_description: Generates random hosts looking like k8s cluster
    description: Returns a dynamic host inventory that is generated to look like k8s cluster
    options:
      number_of_workers:
        description: Number of worker nodes to generate
        required: true
'''

class HostDoesNotExist(Exception):
    """
    Used when trying to use a host that does not exist.
    """
    pass

class HostAlreadyExist(Exception):
    """
    Used when trying to add a host that already exist
    """
    pass

class GroupAlreadyExist(Exception):
    """
    Used when trying to add a group that already exist.
    """
    pass

class GroupDoesNotExist(Exception):
    """
    Used when trying to use a group that does not exist.
    """

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'cwnr.bnp.random_plugin'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.number_of_workers = 10
    def verify_file(self, path: str):
        if super(InventoryModule, self).verify_file(path):
            return path.endswith('yaml') or path.endswith('yml')
        return False

    def parse(self, inventory: Any, loader: Any, path: Any, cache: bool = True) -> Any:
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        try:
            self.number_of_workers = self.get_option('number_of_workers')

            for group, number_of_hosts in [
                ("etcd", 3),
                ("kube-master", 3),
                ("kube-worker", self.number_of_workers)
            ]:
                self.inventory.add_group(group)
                for _ in range(number_of_hosts):
                    host = "host-" + str(random.randint(100000, 999999))
                    self.inventory.add_host(host)
                    self.inventory.add_child(group, host)
                    self.inventory.set_variable(host, "role", group)
                    self.inventory.set_variable(host, "uuid", str(uuid.uuid4()))
        except KeyError as kerr:
            raise AnsibleParserError(f'Missing required option on the configuration file: {path} -> {str(kerr)}"')

# Copyright 2015,  A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.from neutron.db import model_base

import itertools
from oslo_log import log as logging

import a10_neutron_lbaas.a10_config as a10_config
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.common import resources as common_resources

import a10_neutron_lbaas.neutron_ext.db.a10_device as a10_device
import a10_neutron_lbaas.vthunder.instance_manager as instance_manager
from a10_openstack_lib.resources import a10_device as resources

LOG = logging.getLogger(__name__)

# api, vthunder, instance, and db keys
_API = 0
_VTHUNDER_CONFIG = 1
_INSTANCE = 2
_DB = 3

_vthunder_mappings = [("id", None, None, "id"),
                      ("tenant_id", None, None, "tenant_id"),
                      ("tenant_id", None, None, "project_id"),
                      ("project_id", None, None, "tenant_id"),
                      ("project_id", None, None, "project_id"),
                      ("name", None, None, "name"),
                      ("description", None, None, "description"),
                      ("host", None, "ip_address", "host"),
                      ("username", "username", None, "username"),
                      ("password", "password", None, "password"),
                      ("api_version", "api_version", None, "api_version"),
                      ("protocol", "protocol", None, "protocol"),
                      ("port", "port", None, "port"),
                      ("nova_instance_id", None, "nova_instance_id", "nova_instance_id"),
                      (None, "autosnat", None, "autosnat"),
                      (None, "v_method", None, "v_method"),
                      (None, "shared_partition", None, "shared_partition"),
                      (None, "use_float", None, "use_float"),
                      (None, "default_virtual_server_vrid", None, "default_virtual_server_vrid"),
                      (None, "ipinip", None, "ipinip"),
                      (None, "write_memory", None, "write_memory"),
                      ("management_network", "vthunder_management_network", None, None),
                      ("data_networks", "vthunder_data_networks", None, None),
                      ("image", "glance_image", None, None),
                      ("flavor", "nova_flavor", None, None)]

_device_mappings = [("id", None, None, "id"),
                    ("name", None, None, "name"),
                    ("description", None, None, "description"),
                    ("host", None, "ip_address", "host"),
                    ("username", "username", None, "username"),
                    ("password", "password", None, "password"),
                    ("api_version", "api_version", None, "api_version"),
                    ("protocol", "protocol", None, "protocol"),
                    ("port", "port", None, "port"),
                    (None, "autosnat", None, "autosnat"),
                    (None, "v_method", None, "v_method"),
                    (None, "shared_partition", None, "shared_partition"),
                    (None, "use_float", None, "use_float"),
                    (None, "default_virtual_server_vrid", None, "default_virtual_server_vrid"),
                    (None, "ipinip", None, "ipinip"),
                    (None, "write_memory", None, "write_memory")]

_key_mappings = []

_value_mappings = []

def _convert(source, from_type, to_type, _mappings):
    result = {}

    for mapping in _mappings:
        source_key = mapping[from_type]
        if source_key is None or source_key not in source:
            continue

        dest_key = mapping[to_type]
        if dest_key is None:
            continue

        result[dest_key] = source[source_key]

    return result


def _make_api_dict(db_record, _mappings):
    return _convert(db_record, _DB, _API, _mappings)


class A10DevicePlugin(a10_device.A10DeviceDbMixin):

    supported_extension_aliases = [constants.A10_DEVICE_EXT]

    def get_vthunder(self, context, filters=None, fields=None):
        LOG.debug(
            "A10DevicePlugin.get_vthunder(): filters=%s, fields=%s",
            filters,
            fields)

        db_instances = super(A10DevicePlugin, self).get_a10_device(
            context, filters=filters, fields=fields)

        return map(_make_api_dict, db_instances, itertools.repeat(_vthunder_mappings, len(db_instances)))

    def create_vthunder(self, context, vthunder):
        """Attempt to create vthunder using neutron context"""
        LOG.debug("A10DevicePlugin.create(): vthunder=%s", vthunder)

        config = a10_config.A10Config()
        vthunder_defaults = config.get_vthunder_config()

        imgr = instance_manager.InstanceManager.from_config(config, context)

        dev_instance = common_resources.remove_attributes_not_specified(
            a10_device_instance.get(resources.DEVICES))

        # Create the instance with specified defaults.
        vthunder_config = vthunder_defaults.copy()
        vthunder_config.update(_convert(dev_instance, _API, _VTHUNDER_CONFIG))
        instance = imgr.create_device_instance(vthunder_config, dev_instance.get("name"))

        db_record = {}
        db_record.update(_convert(vthunder_config, _VTHUNDER_CONFIG, _DB))
        db_record.update(_convert(dev_instance, _API, _DB))
        db_record.update(_convert(instance, _INSTANCE, _DB))

        # If success, return the created DB record
        # Else, raise an exception because that's what we would do anyway
        db_instance = super(A10DevicePlugin, self).create_a10_device(
            context, {resources.DEVICES: db_record})

        return _make_api_dict(db_instance, itertools.repeat(_device_mappings, len(db_instance)))

    def get_vthunder(self, context, id, fields=None):
        LOG.debug("A10DevicePlugin.get_vthunder(): id=%s, fields=%s",
                  id, fields)
        db_instance = super(A10DevicePlugin, self).get_a10_device(
            context, id, fields=fields)

        return _make_api_dict(db_instance, itertools.repeat(_device_mappings, len(db_instance)))

    def update_vthunder(self, context, id, vthunder):
        LOG.debug(
            "A10DevicePlugin.update_vthunder(): id=%s, vthunder=%s",
            id,
            vthunder)

        db_instance = super(A10DevicePlugin, self).update_vthunder(
            context,
            id,
            vthunder)

        return _make_api_dict(db_instance, itertools.repeat(_device_mapping, len(db_instance)))

    def delete_vthunder(self, context, id):
        LOG.debug("A10DevicePlugin.delete(): id=%s", id)
        # Deleting the actual instance requires knowing the nova instance ID
        vthunder = super(A10DevicePlugin, self).get_a10_device(context, id)
        nova_instance_id = vthunder.get("nova_instance_id")
        config = a10_config.A10Config()
        imgr = instance_manager.InstanceManager.from_config(config, context)
        imgr.delete_instance(nova_instance_id)

        return super(A10DevicePlugin, self).delete_a10_device(context, id)

    def get_a10_device_key(self, context, id, fields=None):
        LOG.debug("A10DevicePlugin.get_a10_device_key(): id=%s, fields=%s",
                  id, fields)

        db_instance = super(A10DevicePlugin, self).get_a10_device_key(
            context, id, fields=fields)

        return _make_api_dict(db_instance, itertools.repeat(_device_key_mappings, len(db_instance)))
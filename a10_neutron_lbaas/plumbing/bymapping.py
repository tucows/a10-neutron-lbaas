# Copyright 2014, A10 Networks
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
#    under the License.

import acos_client

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import models

from a10_neutron_lbaas.plumbing import base


# The default set of plumbing hooks/scheduler, meant for hardware or manual orchestration

class PlumbingHooks(base.BasePlumbingHooks):
    def __init__(self, driver, devices=None, get_devices_func=None, **kwargs):
        super(PlumbingHooks, self).__init__(
            driver, devices=devices, get_devices_func=get_devices_func, **kwargs)
        self.devices = models.A10Devices.get_all(db_session=db_session)

    def _select_device_db(self, tenant_id, db_session=None):
        # See if we have a saved tenant
        a10 = models.A10TenantBinding.find_by_tenant_id(tenant_id, db_session=db_session)
        if a10 is not None:
            if a10.device_name in self.devices:
                return self.devices[a10.device_name]
            else:
                raise ex.DeviceConfigMissing(
                    'A10 device %s mapped to tenant %s is not present in config; '
                    'add it back to config or migrate loadbalancers' %
                    (a10.device_name, tenant_id))

        raise ex.DeviceConfigMissing(
            'No A10 device mapped to tenant %s, configure to continue.' %
            (tenant_id))

    def select_device(self, tenant_id, **kwargs):
        return self._select_device_db(tenant_id)

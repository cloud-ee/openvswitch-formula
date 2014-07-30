'''
Manage OpenVSwitch bridges from Salt.

Based on the Apache licensed salt/modules/bridge.py.

:maintainer:    Florian Ermisch <florian.ermisch@fokus.fraunhofer.de>
:maturity:      new
:depends:       openvswitch-switch
:platform:      Linux,FreeBSD
'''

import salt.utils
from salt.exceptions import CommandExecutionError, SaltInvocationError

__func_alias__ = {
    'list_': 'list'
}

def __virtual__():
    '''
    Confirm this module is supported by the OS and the system has
    required tools
    '''
    if salt.utils.which('ovs-vsctl'):
      return True
    return False


def test():
    '''
    Test ovs-bridge module.
    '''
    retcode = __salt__['cmd.retcode']('ovs-vsctl show')
    if retcode == 0:
        return True
    else:
        return False

def add(br):
    '''
    Add a OVS bridge.
    '''
    # Make sure we don't create None bridges
    retcode = __salt__['cmd.retcode']('ovs-vsctl add-br {0}'.format(str(br)))
    if retcode == 0:
        return True
    elif exists(br):
        return False
    else:
        raise CommandExecutionError

def addif(br, iface):
    '''
    On given bridge, add interface as port.
    
    .. code-block:: bash
    
    salt '*' ovs_bridge.addif ovs-br0 eth0
    '''
    retcode = __salt__['cmd.retcode'](
            'ovs-vsctl add-port {0} {1}'.format(str(br),str(iface))
            )
    if retcode == 0:
        return True
    else:
        return False

def delete(br):
    '''
    Delete given OVS bridge.
    '''
    # Managed to create a None bridge, forcing str() to
    # get rid of those:
    retcode = __salt__['cmd.retcode']('ovs-vsctl del-br {0}'.format(str(br)))
    if retcode == 0 and not exists(str(br)):
        return True
    else:
        return False

def delif(br, iface):
    '''
    On given bridge, delete interface as port.
    
    .. code-block:: bash
    
    salt '*' ovs_bridge.delif ovs-br0 eth0
    '''
    retcode = __salt__['cmd.retcode'](
            'ovs-vsctl del-port {0} {1}'.format(str(br),str(iface))
            )
    if retcode == 0:
        return True
    else:
        return False


def exists(br):
    '''
    Check if given OVS bridge exists.
    '''
    retcode = __salt__['cmd.retcode']('ovs-vsctl br-exists {0}'.format(br))
    if retcode == 0:
        return True
    # From `ovs-vsctl --help`:
    #     br-exists BRIDGE            exit 2 if BRIDGE does not exist
    elif retcode == 2:
        return False
    else:
        raise CommandExecutionError

def find_interfaces(*args):
    '''
    Returns a dict mapping interfaces to the bridge they're bond to.
    The dict doesn't contain entries for non-existant interfaces
    or interfaces not bond to a bridge.

    CLI Example:

    .. code-block:: bash

    salt '*' ovs_bridge.find_interfaces eth0 [eth1...]
    '''

    ifdict = {}

    for iface in args:
        for br in list_():
            if iface in interfaces(br):
                ifdict[iface] = br
                break

    return ifdict

def interfaces(br):
    '''
    Returns interfaces attached to a bridge

    CLI Example:

    .. code-block:: bash

    salt '*' ovs_bridge.interfaces br0
    '''
    if not exists(br):
        return None

    ports = []
    cmd_output = __salt__['cmd.run']('ovs-vsctl list-ports {0}'.format(br))
    for line in cmd_output.splitlines():
        ports += [line]
        
    return ports

def list_():
    '''
    Returns the machine's OVS bridges list

    CLI Example:

    .. code-block:: bash

    salt '*' ovs_bridge.list
    '''

    brlist = []

    cmd_output = __salt__['cmd.run']('ovs-vsctl list-br')
    for line in cmd_output.splitlines():
        brlist += [line]

    return brlist

def show():
    '''
    Run `ovs-vsctl show` and return (unparsed) output.
    '''
    return __salt__['cmd.run']('ovs-vsctl show')

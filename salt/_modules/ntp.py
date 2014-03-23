"""
Read ntp timing statistics

"""
import salt.utils


def offset():
    """
    Return ntp delay, offset and jitter

    CLI Example::

        salt '*' ntp.offset
    """

    ntpq_out = __salt__['cmd.run']('ntpq -n -p | grep \'^[*o]\'')

    delay = ntpq_out.split()[7]
    offset = ntpq_out.split()[8]
    jitter = ntpq_out.split()[9]
    
    return {
        'delay': float(delay),
        'offset': float(offset),
        'jitter': float(jitter),
    }

def kerninfo():
    """
    Return ntp kernel info

    CLI Example::

        salt '*' ntp.kerninfo
    """

    ntpdc_out = __salt__['cmd.run']('ntpdc -c kerninfo')

    lines = ntpdc_out.splitlines()

    ppl_offset = lines[0].split()[2]
    ppl_frequency = lines[1].split()[2]
    estimated_error = lines[3].split()[2]
    
    return {
        'ppl_offset': float(ppl_offset),
        'ppl_frequency': float(ppl_frequency),
        'estimated_error': float(estimated_error),
    }
